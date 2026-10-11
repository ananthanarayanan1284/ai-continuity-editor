"""Extraction logic with a stand-in LLM (offline), plus one live test against Ollama."""

import pytest
from pydantic import ValidationError

from continuity_editor.extraction.chapters import ChapterText
from continuity_editor.extraction.extractor import (
    evidence_found,
    extract_chapter,
    extract_novel,
    locate_evidence,
    merge_entities,
    normalise_attribute,
)
from continuity_editor.extraction.schemas import ExtractedEntity, facts_schema_for
from continuity_editor.llm import LLMClient

PASSAGE = (
    "Dorothy lived in the midst of the great Kansas prairies, with Uncle Henry, who was a farmer. "
    "Toto was a little black dog, with long silky hair and small black eyes."
)
TOTO_EVIDENCE = "Toto was a little black dog, with long silky hair and small black eyes."


class FakeLLM:
    """Gives canned answers in order, the way the real model would answer each pass."""

    model = "fake"

    def __init__(self, *answers):
        self.answers = list(answers)

    def structured(self, prompt, schema, system=None, max_tokens=None):
        return schema.model_validate(self.answers.pop(0))


def fact(subject, attribute, value, evidence):
    return {"subject": subject, "attribute": attribute, "value": value, "category": "characterisation", "evidence": evidence}


def test_quoted_facts_are_kept_and_invented_ones_dropped():
    llm = FakeLLM(
        {"entities": [{"name": "Toto", "kind": "character"}, {"name": "Dorothy", "kind": "character"}]},
        {
            "facts": [
                fact("Toto", "Eye Color", "black", TOTO_EVIDENCE),
                fact("Dorothy", "age", "twelve", "Dorothy was twelve years old that summer."),  # not in the text
            ],
            "events": [],
        },
    )
    result = extract_chapter(llm, "oz", ChapterText(1, "The Cyclone", PASSAGE))
    assert [(f.subject, f.attribute, f.value) for f in result.facts] == [("Toto", "eye_colour", "black")]
    assert result.unverified_dropped == 1


def test_names_are_unified_across_chunks():
    llm = FakeLLM(
        {"entities": [{"name": "Toto", "kind": "character", "aliases": ["the dog"]}]},
        {"facts": [], "events": []},
        {"entities": [{"name": "the dog", "kind": "character"}]},
        {"facts": [fact("the dog", "colour", "black", TOTO_EVIDENCE)], "events": []},
    )
    two_paragraphs = PASSAGE.replace("farmer. Toto", "farmer.\n\nToto")
    result = extract_chapter(llm, "oz", ChapterText(1, "The Cyclone", two_paragraphs), chunk_words=20)
    assert [e.name for e in result.entities] == ["Toto"]
    assert result.facts[0].subject == "Toto"


def test_momentary_states_are_not_kept_as_facts():
    llm = FakeLLM(
        {"entities": [{"name": "Toto", "kind": "character"}]},
        {"facts": [fact("Toto", "emotion", "did not like it", TOTO_EVIDENCE)], "events": []},
    )
    result = extract_chapter(llm, "oz", ChapterText(1, "x", PASSAGE))
    assert result.facts == []
    assert result.unverified_dropped == 0


def test_saved_results_are_reused_until_the_chapter_text_changes(tmp_path):
    chapter = ChapterText(1, "The Cyclone", PASSAGE)
    llm = FakeLLM(
        {"entities": [{"name": "Toto", "kind": "character"}]},
        {"facts": [fact("Toto", "colour", "black", TOTO_EVIDENCE)], "events": []},
    )
    first = extract_novel(llm, "oz", [chapter], tmp_path)[0]
    again = extract_novel(FakeLLM(), "oz", [chapter], tmp_path)[0]  # no answers: fails if the model is asked
    assert again == first

    edited = ChapterText(1, "The Cyclone", PASSAGE.replace("black dog", "white dog"))
    redone = extract_novel(FakeLLM({"entities": []}), "oz", [edited], tmp_path)[0]
    assert redone.facts == []


def test_an_unusable_answer_is_counted_not_fatal():
    result = extract_chapter(FakeLLM({"entities": "not a list"}), "oz", ChapterText(1, "x", PASSAGE))
    assert result.failed_chunks == 1
    assert result.facts == []


def test_facts_schema_only_accepts_listed_names():
    schema = facts_schema_for(["Toto"], [])
    with pytest.raises(ValidationError):
        schema.model_validate({"facts": [fact("Glinda", "a", "b", TOTO_EVIDENCE)], "events": []})


def test_entities_merge_by_alias_but_not_across_kinds():
    merged = merge_entities(
        [
            ExtractedEntity(name="the Tin Woodman", kind="character", aliases=["the Woodman"]),
            ExtractedEntity(name="the Woodman", kind="character"),
            ExtractedEntity(name="Oz", kind="character"),
            ExtractedEntity(name="Oz", kind="location"),
        ]
    )
    assert [(e.name, e.kind) for e in merged] == [
        ("the Tin Woodman", "character"),
        ("Oz", "character"),
        ("Oz", "location"),
    ]
    assert merged[0].aliases == ["the Woodman"]


def test_attribute_labels_are_normalised():
    assert normalise_attribute("Eye Color") == "eye_colour"
    assert normalise_attribute("eyes") == "eye_colour"
    assert normalise_attribute("Hair color") == "hair_colour"
    assert normalise_attribute("home town") == "home_town"


def test_evidence_must_be_a_real_quote():
    text = "“My darling child!” she cried, folding the little girl in her arms."
    assert evidence_found('"My darling child!" she cried, folding the little girl in her arms.', text)
    assert not evidence_found("the little girl", text)  # too short to prove anything
    assert not evidence_found("She pushed the little girl away in anger.", text)


def test_short_quotes_are_expanded_to_their_sentence():
    text = "Uncle Henry never laughed. He worked hard from morning till night and did not know what joy was."
    assert locate_evidence("worked hard from morning till night", text) == (
        "He worked hard from morning till night and did not know what joy was."
    )
    dialogue = "“My darling child!” she cried, folding the little girl in her arms. Then she wept."
    assert locate_evidence("she cried, folding the little girl", dialogue) == (
        "“My darling child!” she cried, folding the little girl in her arms."
    )


@pytest.fixture(scope="module")
def llm():
    client = LLMClient()
    try:
        client.verify()
    except RuntimeError as exc:
        pytest.skip(str(exc))
    return client


@pytest.mark.integration
def test_live_extraction_finds_characters_and_quoted_facts(llm):
    result = extract_chapter(llm, "oz", ChapterText(1, "The Cyclone", PASSAGE))
    names = " ".join(e.name for e in result.entities)
    assert "Dorothy" in names and "Toto" in names
    assert result.facts
    assert all(evidence_found(f.evidence, PASSAGE) for f in result.facts)
