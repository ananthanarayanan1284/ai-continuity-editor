"""What the LLM returns for a passage. Entities are referred to by name here; the
retrieval step later resolves names to graph ids."""

from typing import Literal

from pydantic import BaseModel, Field, create_model

EntityKind = Literal["character", "location", "world_element"]
# FactCategory minus narrative_style, which describes the telling rather than a fact.
ExtractedCategory = Literal["characterisation", "factual_detail", "timeline", "world_building"]


class ExtractedEntity(BaseModel):
    name: str
    kind: EntityKind
    aliases: list[str] = Field(default_factory=list)


class EntityList(BaseModel):
    entities: list[ExtractedEntity]


class ExtractedFact(BaseModel):
    subject: str  # an entity name
    attribute: str
    value: str
    category: ExtractedCategory
    evidence: str  # sentence quoted from the passage


class ExtractedEvent(BaseModel):
    description: str
    participants: list[str]  # entity names
    location: str | None = None  # a location entity name
    story_time: str | None = None  # in-story time as written, e.g. "that night"
    evidence: str


class FactsAndEvents(BaseModel):
    facts: list[ExtractedFact]
    events: list[ExtractedEvent]


class ChapterExtraction(BaseModel):
    """Everything extracted from one chapter, plus how it was produced."""

    novel_id: str
    chapter_number: int
    chapter_title: str
    text_hash: str  # fingerprint of the chapter text, so an edited chapter is re-extracted
    model: str
    extraction_version: str
    seconds: float
    entities: list[ExtractedEntity]
    facts: list[ExtractedFact]
    events: list[ExtractedEvent]
    unverified_dropped: int = 0  # facts/events whose evidence was not found in the text
    failed_chunks: int = 0  # chunks the model could not answer in valid JSON


def facts_schema_for(names: list[str], locations: list[str]) -> type[FactsAndEvents]:
    """A FactsAndEvents schema whose subjects, participants and locations must be one of the
    given names. Ollama enforces the schema while generating, so no fact can name an unknown entity."""
    name = Literal[tuple(names)]
    location = (Literal[tuple(locations)] | None) if locations else None
    fact = create_model("Fact", __base__=ExtractedFact, subject=(name, ...))
    event = create_model(
        "Event", __base__=ExtractedEvent, participants=(list[name], ...), location=(location, None)
    )
    return create_model("FactsAndEvents", __base__=FactsAndEvents, facts=(list[fact], ...), events=(list[event], ...))
