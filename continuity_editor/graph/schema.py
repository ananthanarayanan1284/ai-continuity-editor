"""Story-bible graph schema: node labels, relationship types, constraints and indexes.

Facts are nodes, not properties. Each chapter's claims become new `Fact` nodes linked to
the chapter that stated them, so nothing is ever overwritten and an entity's full history
is one traversal away:

    (:Novel)-[:HAS_CHAPTER]->(:Chapter)-[:NEXT]->(:Chapter)
    (:Chapter)-[:MENTIONS]->(:Entity)
    (:Entity)-[:HAS_FACT]->(:Fact)-[:STATED_IN]->(:Chapter)
    (:Character)-[:PARTICIPATES_IN {role}]->(:Event)-[:OCCURS_AT]->(:Location)
    (:Event)-[:DESCRIBED_IN]->(:Chapter)
    (:Event)-[:PRECEDES]->(:Event)
    (:Character)-[:RELATES_TO {type, chapter_number, evidence_span}]->(:Character)
    (:Fact)-[:CONTRADICTS {confidence, reason, chapter_number}]->(:Fact)   (flagged by the checker)

Characters, locations and world elements carry two labels, e.g. (:Entity:Character), so
any of them can be looked up by `entity_id` through a single index.
"""

from enum import StrEnum
from typing import Any

from continuity_editor.graph.connection import Neo4jConnection


class NodeLabel(StrEnum):
    NOVEL = "Novel"
    CHAPTER = "Chapter"
    ENTITY = "Entity"  # shared by the three entity types below
    CHARACTER = "Character"
    LOCATION = "Location"
    WORLD_ELEMENT = "WorldElement"  # world rules, objects, organisations, magic systems
    EVENT = "Event"
    FACT = "Fact"


class RelType(StrEnum):
    HAS_CHAPTER = "HAS_CHAPTER"
    NEXT = "NEXT"
    MENTIONS = "MENTIONS"
    HAS_FACT = "HAS_FACT"
    STATED_IN = "STATED_IN"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    OCCURS_AT = "OCCURS_AT"
    DESCRIBED_IN = "DESCRIBED_IN"
    PRECEDES = "PRECEDES"
    RELATES_TO = "RELATES_TO"
    CONTRADICTS = "CONTRADICTS"


# Every statement uses IF NOT EXISTS, so apply_schema() is safe to run repeatedly.
CONSTRAINTS = [
    "CREATE CONSTRAINT novel_id IF NOT EXISTS FOR (n:Novel) REQUIRE n.novel_id IS UNIQUE",
    "CREATE CONSTRAINT chapter_id IF NOT EXISTS FOR (n:Chapter) REQUIRE n.chapter_id IS UNIQUE",
    "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.entity_id IS UNIQUE",
    "CREATE CONSTRAINT event_id IF NOT EXISTS FOR (n:Event) REQUIRE n.event_id IS UNIQUE",
    "CREATE CONSTRAINT fact_id IF NOT EXISTS FOR (n:Fact) REQUIRE n.fact_id IS UNIQUE",
]

INDEXES = [
    "CREATE INDEX chapter_number IF NOT EXISTS FOR (n:Chapter) ON (n.number)",
    "CREATE INDEX entity_novel IF NOT EXISTS FOR (n:Entity) ON (n.novel_id)",
    "CREATE INDEX event_novel IF NOT EXISTS FOR (n:Event) ON (n.novel_id)",
    "CREATE INDEX fact_attribute IF NOT EXISTS FOR (n:Fact) ON (n.attribute)",
    "CREATE INDEX fact_chapter_number IF NOT EXISTS FOR (n:Fact) ON (n.chapter_number)",
    # Fuzzy name/alias lookup for entity resolution ("Mira" -> Mira Voss).
    "CREATE FULLTEXT INDEX entity_names IF NOT EXISTS FOR (n:Entity) ON EACH [n.name, n.aliases]",
]


def apply_schema(conn: Neo4jConnection) -> dict[str, int]:
    """Create all constraints and indexes, returning how many were new."""
    added = {"constraints_added": 0, "indexes_added": 0}
    for statement in CONSTRAINTS + INDEXES:
        counters = conn.write(statement)
        for key in added:
            added[key] += counters.get(key, 0)
    return added


def describe_schema(conn: Neo4jConnection) -> dict[str, list[dict[str, Any]]]:
    """List the constraints and the standalone indexes (the ones not backing a constraint)."""
    constraints = conn.query(
        "SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties "
        "RETURN name, type, labelsOrTypes AS labels, properties ORDER BY name"
    )
    indexes = conn.query(
        "SHOW INDEXES YIELD name, type, labelsOrTypes, properties, state, owningConstraint "
        "WHERE owningConstraint IS NULL AND type <> 'LOOKUP' "
        "RETURN name, type, labelsOrTypes AS labels, properties, state ORDER BY name"
    )
    return {"constraints": constraints, "indexes": indexes}
