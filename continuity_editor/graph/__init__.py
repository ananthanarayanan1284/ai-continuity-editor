"""Neo4j story bible: connection, schema, node models and append-only writes."""

from continuity_editor.graph.connection import Neo4jConnection
from continuity_editor.graph.schema import apply_schema, describe_schema
from continuity_editor.graph.writer import (
    add_chapter,
    add_contradictions,
    add_entity,
    add_events,
    add_fact,
    add_facts,
    add_novel,
    reset_novel,
)

__all__ = [
    "Neo4jConnection",
    "add_chapter",
    "add_contradictions",
    "add_entity",
    "add_events",
    "add_fact",
    "add_facts",
    "add_novel",
    "apply_schema",
    "describe_schema",
    "reset_novel",
]
