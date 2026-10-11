"""Pydantic models for the story-bible nodes.

The extraction step turns the LLM's structured output into these models, and the writer
turns the models into graph nodes, so each node type is defined in one place.
"""

import re
import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from continuity_editor.graph.schema import NodeLabel


def slugify(text: str) -> str:
    """'Mira  Voss' -> 'mira_voss'."""
    return re.sub(r"\W+", "_", text.casefold()).strip("_")


def make_entity_id(novel_id: str, label: str, name: str) -> str:
    """Stable id such as 'toy_novel:character:mira_voss'.

    The label is part of the id so a character and a place with the same name
    (Paris the prince, Paris the city) never collide.
    """
    slug = slugify(name)
    if not slug:
        raise ValueError(f"Cannot build an entity id from the name {name!r}")
    return f"{novel_id}:{slugify(label)}:{slug}"


def make_chapter_id(novel_id: str, number: int) -> str:
    return f"{novel_id}:ch{number}"


def _new_id() -> str:
    return uuid.uuid4().hex


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GraphModel(BaseModel):
    # Store enums as their plain string values, which is what gets written to Neo4j.
    model_config = ConfigDict(use_enum_values=True, validate_default=True)


class FactCategory(StrEnum):
    """Contradiction categories, following the ConStory-Bench taxonomy."""

    CHARACTERISATION = "characterisation"
    FACTUAL_DETAIL = "factual_detail"
    TIMELINE = "timeline"
    WORLD_BUILDING = "world_building"
    NARRATIVE_STYLE = "narrative_style"


class WorldElementKind(StrEnum):
    RULE = "rule"
    OBJECT = "object"
    ORGANISATION = "organisation"
    MAGIC_SYSTEM = "magic_system"
    OTHER = "other"


class Novel(GraphModel):
    novel_id: str
    title: str


class Chapter(GraphModel):
    novel_id: str
    number: int = Field(ge=1)
    title: str | None = None
    ingested_at: datetime = Field(default_factory=_utc_now)

    @computed_field
    @property
    def chapter_id(self) -> str:
        return make_chapter_id(self.novel_id, self.number)


class Entity(GraphModel):
    """Fields shared by Character, Location and WorldElement."""

    label: ClassVar[NodeLabel]

    novel_id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    entity_id: str = ""  # built from novel_id, label and name unless given explicitly

    @model_validator(mode="after")
    def _fill_entity_id(self) -> Self:
        if not self.entity_id:
            self.entity_id = make_entity_id(self.novel_id, self.label, self.name)
        return self


class Character(Entity):
    label: ClassVar[NodeLabel] = NodeLabel.CHARACTER


class Location(Entity):
    label: ClassVar[NodeLabel] = NodeLabel.LOCATION


class WorldElement(Entity):
    label: ClassVar[NodeLabel] = NodeLabel.WORLD_ELEMENT

    kind: WorldElementKind = WorldElementKind.OTHER


class Event(GraphModel):
    novel_id: str
    description: str
    chapter_number: int = Field(ge=1)
    story_time: str | None = None  # in-story time as written, e.g. "three days later"
    evidence_span: str = ""
    event_id: str = Field(default_factory=_new_id)
    # Stored as relationships, not node properties:
    participant_ids: list[str] = Field(default_factory=list, exclude=True)
    location_id: str | None = Field(default=None, exclude=True)


class Fact(GraphModel):
    """One claim about an entity, as stated in one chapter. Never modified once written."""

    novel_id: str
    subject_id: str  # entity_id of the Character / Location / WorldElement it describes
    attribute: str  # e.g. "eye_colour", "age", "home_city"
    value: str  # e.g. "blue", "25"
    category: FactCategory
    evidence_span: str  # verbatim quote from the chapter, cited when a contradiction is flagged
    chapter_number: int = Field(ge=1)
    fact_id: str = Field(default_factory=_new_id)
    created_at: datetime = Field(default_factory=_utc_now)
