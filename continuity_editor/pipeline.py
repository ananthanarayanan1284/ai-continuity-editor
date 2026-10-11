"""The whole continuity check, chapter by chapter, the way a writer would add them.

For each chapter:
1. store the chapter and its entities, resolving names to entities already in the story bible;
2. pull the history of every entity the chapter mentions (targeted retrieval);
3. check the chapter's new facts against that history and flag contradictions;
4. store the new facts and events (append-only) and link each flag to the facts it involves.
"""

import json
from pathlib import Path

from tqdm.auto import tqdm

from continuity_editor.checking.checker import Flag, check_facts
from continuity_editor.extraction.chapters import ChapterText
from continuity_editor.extraction.schemas import ChapterExtraction
from continuity_editor.graph.connection import Neo4jConnection
from continuity_editor.graph.models import Chapter, Event, Fact, Novel
from continuity_editor.graph.writer import (
    add_chapter,
    add_contradictions,
    add_entity,
    add_events,
    add_facts,
    add_novel,
    reset_novel,
)
from continuity_editor.llm import LLMClient
from continuity_editor.retrieval.history import fact_history
from continuity_editor.retrieval.resolver import EntityResolver


def process_chapter(
    conn: Neo4jConnection,
    llm: LLMClient,
    resolver: EntityResolver,
    chapter: ChapterText,
    extraction: ChapterExtraction,
    check: bool = True,
) -> list[Flag]:
    novel_id = resolver.novel_id
    chapter_node = Chapter(novel_id=novel_id, number=chapter.number, title=chapter.title)
    add_chapter(conn, chapter_node)

    ids: dict[str, str] = {}  # name used in this chapter (lower case) -> entity_id
    for extracted in extraction.entities:
        entity = resolver.resolve(extracted)
        add_entity(conn, entity, chapter_node)
        for name in (extracted.name, *extracted.aliases):
            ids.setdefault(name.casefold(), entity.entity_id)

    facts = [
        Fact(
            novel_id=novel_id,
            subject_id=ids[f.subject.casefold()],
            attribute=f.attribute,
            value=f.value,
            category=f.category,
            evidence_span=f.evidence,
            chapter_number=chapter.number,
        )
        for f in extraction.facts
        if f.subject.casefold() in ids
    ]
    flags = []
    if check and facts:
        history = fact_history(conn, {f.subject_id for f in facts}, before_chapter=chapter.number)
        flags = check_facts(llm, facts, history, resolver.names())

    add_facts(conn, facts)
    add_events(
        conn,
        [
            Event(
                novel_id=novel_id,
                description=e.description,
                chapter_number=chapter.number,
                story_time=e.story_time,
                evidence_span=e.evidence,
                participant_ids=[ids[p.casefold()] for p in e.participants if p.casefold() in ids],
                location_id=ids.get(e.location.casefold()) if e.location else None,
            )
            for e in extraction.events
        ],
    )
    add_contradictions(conn, [flag.model_dump() for flag in flags])
    return flags


def run_novel(
    conn: Neo4jConnection,
    llm: LLMClient,
    novel_id: str,
    title: str,
    chapters: list[ChapterText],
    extractions: list[ChapterExtraction],
    check: bool = True,
) -> list[Flag]:
    """Rebuild the story bible for `novel_id` from scratch, checking each chapter as it is added."""
    reset_novel(conn, novel_id)
    add_novel(conn, Novel(novel_id=novel_id, title=title))
    resolver = EntityResolver(novel_id)
    flags: list[Flag] = []
    for chapter, extraction in tqdm(list(zip(chapters, extractions)), desc=f"Checking {novel_id}", unit="chapter"):
        flags += process_chapter(conn, llm, resolver, chapter, extraction, check=check)
    return flags


def save_flags(flags: list[Flag], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([f.model_dump() for f in flags], ensure_ascii=False, indent=1), encoding="utf-8")


def load_flags(path: Path) -> list[Flag]:
    return [Flag.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]
