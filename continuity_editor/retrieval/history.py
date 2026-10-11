"""Targeted retrieval: everything earlier chapters established about the entities a new
chapter mentions, pulled from the story bible in one query."""

from collections.abc import Iterable

from pydantic import BaseModel

from continuity_editor.graph.connection import Neo4jConnection


class PriorFact(BaseModel):
    fact_id: str
    entity_id: str
    chapter: int
    attribute: str
    value: str
    category: str
    evidence: str


def fact_history(
    conn: Neo4jConnection, entity_ids: Iterable[str], before_chapter: int
) -> dict[str, list[PriorFact]]:
    """entity_id -> facts stated about it in chapters before `before_chapter`, oldest first."""
    entity_ids = sorted(set(entity_ids))
    history: dict[str, list[PriorFact]] = {entity_id: [] for entity_id in entity_ids}
    if not entity_ids:
        return history
    rows = conn.query(
        """
        MATCH (e:Entity)-[:HAS_FACT]->(f:Fact)-[:STATED_IN]->(ch:Chapter)
        WHERE e.entity_id IN $entity_ids AND ch.number < $before_chapter
        RETURN e.entity_id AS entity_id, f.fact_id AS fact_id, ch.number AS chapter,
               f.attribute AS attribute, f.value AS value, f.category AS category,
               f.evidence_span AS evidence
        ORDER BY chapter, attribute, value, evidence
        """,
        entity_ids=entity_ids,
        before_chapter=before_chapter,
    )
    for row in rows:
        history[row["entity_id"]].append(PriorFact(**row))
    return history
