"""Chapter text -> entities, facts and events, using the local LLM.

Each chunk of a chapter goes through two passes:
1. list the entities in the chunk;
2. extract facts and events, with subjects restricted (while the model generates) to the
   names from pass 1, so every fact is about a known entity.
Facts and events whose quoted evidence can't be found in the text are dropped, so every
contradiction flagged later can cite a real sentence.
"""

import hashlib
import json
import re
import time
from collections.abc import Iterable
from pathlib import Path

from pydantic import ValidationError
from rapidfuzz import fuzz
from tqdm.auto import tqdm

from continuity_editor.extraction.chapters import ChapterText, chunk_text
from continuity_editor.extraction.prompts import ENTITY_SYSTEM, FACTS_SYSTEM, EXTRACTION_VERSION
from continuity_editor.extraction.schemas import (
    ChapterExtraction,
    EntityList,
    ExtractedEntity,
    ExtractedEvent,
    ExtractedFact,
    facts_schema_for,
)
from continuity_editor.llm import LLMClient

CHUNK_WORDS = 500  # smaller chunks: a small model misses fewer details
EVIDENCE_MIN_SCORE = 90  # rapidfuzz partial_ratio (0-100) for a quote to count as present in the text
EVIDENCE_MIN_WORDS = 5  # shorter "quotes" (e.g. "the house") match almost anywhere, so they prove nothing
_PLAIN_PUNCTUATION = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "—": "-", "–": "-"})
_ATTRIBUTE_SYNONYMS = {"eyes": "eye_colour", "eye": "eye_colour", "hair": "hair_colour"}
# Momentary states the prompt excludes but a small model still reports as facts.
_MOMENTARY_ATTRIBUTES = {"action", "activity", "decision", "emotion", "fear", "feeling", "mood", "movement", "reaction", "state"}
# End of a sentence: . ! or ? (maybe then a closing quote), space, and a capital or opening quote.
# “Oh!” she cried stays one sentence because "she" is lower case.
_SENTENCE_END = re.compile(r"[.!?][”’\"']?\s+(?=[“‘\"'A-Z])")


def normalise_attribute(attribute: str) -> str:
    """'Eye color' -> 'eye_colour', so an attribute gets the same label in every chapter."""
    key = re.sub(r"[^a-z0-9]+", "_", attribute.casefold()).strip("_").replace("color", "colour")
    return _ATTRIBUTE_SYNONYMS.get(key, key)


def locate_evidence(quote: str, text: str) -> str | None:
    """Check that `quote` really comes from `text` and return the full sentence it is part of.

    The model is asked for short quotes (fewer tokens to generate, so faster); the citation
    shown later is the whole sentence. Returns None for quotes too short to prove anything or
    not found in the text (small copying differences are allowed). A quote spanning several
    sentences is returned as quoted.
    """
    plain_quote = _plain(quote)
    if len(plain_quote.split()) < EVIDENCE_MIN_WORDS:
        return None
    if fuzz.partial_ratio(plain_quote, _plain(text)) < EVIDENCE_MIN_SCORE:
        return None
    for sentence in _sentences(text):
        if len(sentence) >= len(quote) and fuzz.partial_ratio(plain_quote, _plain(sentence)) >= EVIDENCE_MIN_SCORE:
            return sentence
    return quote.strip()


def evidence_found(quote: str, text: str) -> bool:
    return locate_evidence(quote, text) is not None


def merge_entities(entities: Iterable[ExtractedEntity]) -> list[ExtractedEntity]:
    """Combine entries of the same kind that share a name or alias (case-insensitive).

    Kinds must match because one name can mean two things: "Oz" is the Wizard and the land.
    """
    merged: list[ExtractedEntity] = []
    for entity in entities:
        if not entity.name.strip():
            continue
        names = {n.casefold() for n in (entity.name, *entity.aliases)}
        match = next(
            (
                m
                for m in merged
                if m.kind == entity.kind and names & {n.casefold() for n in (m.name, *m.aliases)}
            ),
            None,
        )
        if match is None:
            merged.append(entity.model_copy(update={"name": entity.name.strip()}))
            match = merged[-1]
        match.aliases = _unique([*match.aliases, entity.name, *entity.aliases], exclude=match.name)
    return merged


def extract_chunk(
    llm: LLMClient, text: str
) -> tuple[list[ExtractedEntity], list[ExtractedFact], list[ExtractedEvent], int]:
    """Run both passes on one chunk. Returns entities, verified facts and events, and the number dropped."""
    found = llm.structured(f"Passage:\n\n{text}", EntityList, system=ENTITY_SYSTEM, max_tokens=1500)
    entities = merge_entities(found.entities)
    if not entities:
        return [], [], [], 0
    names = [e.name for e in entities]
    locations = [e.name for e in entities if e.kind == "location"]
    answer = llm.structured(
        f"Listed entities: {json.dumps(names)}\n\nPassage:\n\n{text}",
        facts_schema_for(names, locations),
        system=FACTS_SYSTEM,
        max_tokens=4000,
    )
    facts, events, unverified = [], [], 0
    for f in answer.facts:
        attribute = normalise_attribute(f.attribute)
        if attribute in _MOMENTARY_ATTRIBUTES:
            continue
        if sentence := locate_evidence(f.evidence, text):
            facts.append(
                ExtractedFact(
                    subject=f.subject,
                    attribute=attribute,
                    value=f.value.strip(),
                    category=f.category,
                    evidence=sentence,
                )
            )
        else:
            unverified += 1
    for e in answer.events:
        if sentence := locate_evidence(e.evidence, text):
            events.append(ExtractedEvent.model_validate(e.model_dump() | {"evidence": sentence}))
        else:
            unverified += 1
    return entities, facts, events, unverified


def extract_chapter(
    llm: LLMClient, novel_id: str, chapter: ChapterText, chunk_words: int = CHUNK_WORDS
) -> ChapterExtraction:
    start = time.perf_counter()
    entities: list[ExtractedEntity] = []
    facts: list[ExtractedFact] = []
    events: list[ExtractedEvent] = []
    dropped = failed = 0

    pending = [(chunk, True) for chunk in chunk_text(chapter.text, chunk_words)]
    while pending:
        chunk, can_split = pending.pop(0)
        try:
            chunk_entities, chunk_facts, chunk_events, chunk_dropped = extract_chunk(llm, chunk)
        except ValidationError:
            # Usually an answer cut off at max_tokens: retry once as two smaller chunks.
            halves = chunk_text(chunk, max(1, len(chunk.split()) // 2)) if can_split else []
            if len(halves) > 1:
                pending[:0] = [(half, False) for half in halves]
            else:
                failed += 1
            continue
        entities += chunk_entities
        facts += chunk_facts
        events += chunk_events
        dropped += chunk_dropped

    # Chunks may name the same entity differently; point everything at one name per entity.
    entities = merge_entities(entities)
    canonical = {e.name.casefold(): e.name for e in reversed(entities)}  # real names win over aliases
    for entity in entities:
        for alias in entity.aliases:
            canonical.setdefault(alias.casefold(), entity.name)

    def rename(name: str) -> str:
        return canonical.get(name.casefold(), name)

    seen: set[tuple[str, str, str]] = set()
    unique_facts = []
    for fact in facts:
        fact = fact.model_copy(update={"subject": rename(fact.subject)})
        key = (fact.subject.casefold(), fact.attribute, fact.value.casefold())
        if key not in seen:
            seen.add(key)
            unique_facts.append(fact)
    events = [
        e.model_copy(
            update={
                "participants": _unique(rename(p) for p in e.participants),
                "location": rename(e.location) if e.location else None,
            }
        )
        for e in events
    ]
    return ChapterExtraction(
        novel_id=novel_id,
        chapter_number=chapter.number,
        chapter_title=chapter.title,
        text_hash=text_hash(chapter.text),
        model=llm.model,
        extraction_version=EXTRACTION_VERSION,
        seconds=round(time.perf_counter() - start, 1),
        entities=entities,
        facts=unique_facts,
        events=events,
        unverified_dropped=dropped,
        failed_chunks=failed,
    )


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_extraction(path: Path) -> ChapterExtraction | None:
    """A saved extraction, or None if there is none (or it was saved in an older format)."""
    try:
        return ChapterExtraction.model_validate_json(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValidationError):
        return None


def extract_novel(
    llm: LLMClient, novel_id: str, chapters: list[ChapterText], cache_dir: Path, force: bool = False
) -> list[ChapterExtraction]:
    """Extract every chapter, reusing a saved result when the same chapter text was already
    extracted with the same model and extraction version, in this book or another version
    of it. The model is slow, so each distinct chapter text is done only once."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for chapter in tqdm(chapters, desc="Chapters", unit="chapter"):
        path = cache_dir / f"{text_hash(chapter.text)}_{re.sub(r'[^a-z0-9]+', '-', llm.model.lower())}_v{EXTRACTION_VERSION}.json"
        cached = None if force else load_extraction(path)
        if cached:
            cached = cached.model_copy(
                update={"novel_id": novel_id, "chapter_number": chapter.number, "chapter_title": chapter.title}
            )
        else:
            cached = extract_chapter(llm, novel_id, chapter)
            path.write_text(cached.model_dump_json(indent=1), encoding="utf-8")
        results.append(cached)
    return results


def _plain(text: str) -> str:
    return text.translate(_PLAIN_PUNCTUATION).casefold().strip()


def _sentences(text: str) -> list[str]:
    sentences = []
    for paragraph in text.split("\n\n"):
        start = 0
        for end in _SENTENCE_END.finditer(paragraph):
            sentences.append(paragraph[start : end.end()].strip())
            start = end.end()
        sentences.append(paragraph[start:].strip())
    return [s for s in sentences if s]


def _unique(names: Iterable[str], exclude: str = "") -> list[str]:
    """Drop blanks and case-insensitive duplicates (and `exclude`), keeping the first spelling."""
    seen = {exclude.casefold()}
    result = []
    for name in names:
        name = name.strip()
        if name and name.casefold() not in seen:
            seen.add(name.casefold())
            result.append(name)
    return result
