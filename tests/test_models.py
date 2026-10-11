"""Offline tests: ids, node models and schema statements. No database needed."""

import pytest
from pydantic import ValidationError

from continuity_editor.graph.models import (
    Chapter,
    Character,
    Fact,
    FactCategory,
    Location,
    WorldElement,
    make_entity_id,
    slugify,
)
from continuity_editor.graph.schema import CONSTRAINTS, INDEXES


def test_slugify():
    assert slugify("Mira  Voss") == "mira_voss"
    assert slugify("  O'Brien! ") == "o_brien"


def test_entity_id_includes_novel_and_type():
    assert make_entity_id("dune", "Character", "Paul Atreides") == "dune:character:paul_atreides"


def test_same_name_different_type_gets_different_ids():
    prince = Character(novel_id="rj", name="Paris")
    city = Location(novel_id="rj", name="Paris")
    assert prince.entity_id != city.entity_id


def test_empty_name_is_rejected():
    with pytest.raises(ValueError):
        make_entity_id("dune", "Character", "?!")


def test_explicit_entity_id_is_kept():
    # Entity resolution maps "Mira" onto the existing Mira Voss node this way.
    mira = Character(novel_id="toy", name="Mira", entity_id="toy:character:mira_voss")
    assert mira.entity_id == "toy:character:mira_voss"


def test_world_element_kind_is_stored_as_plain_string():
    rule = WorldElement(novel_id="toy", name="Iron ward", kind="rule")
    assert rule.model_dump()["kind"] == "rule"
    assert type(WorldElement(novel_id="toy", name="x").model_dump()["kind"]) is str


def test_chapter_id_is_derived():
    chapter = Chapter(novel_id="toy", number=3)
    assert chapter.chapter_id == "toy:ch3"
    assert chapter.model_dump()["chapter_id"] == "toy:ch3"


def test_chapter_number_starts_at_one():
    with pytest.raises(ValidationError):
        Chapter(novel_id="toy", number=0)


def _fact(**overrides) -> Fact:
    fields = dict(
        novel_id="toy",
        subject_id="toy:character:mira_voss",
        attribute="eye_colour",
        value="blue",
        category="characterisation",
        evidence_span="her blue eyes",
        chapter_number=1,
    )
    return Fact(**(fields | overrides))


def test_fact_gets_unique_ids_and_plain_category():
    first, second = _fact(), _fact()
    assert first.fact_id != second.fact_id
    assert first.category == FactCategory.CHARACTERISATION
    assert type(first.model_dump()["category"]) is str


def test_unknown_fact_category_is_rejected():
    with pytest.raises(ValidationError):
        _fact(category="vibes")


def test_schema_statements_are_idempotent():
    for statement in CONSTRAINTS + INDEXES:
        assert "IF NOT EXISTS" in statement
