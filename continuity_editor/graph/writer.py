"""Append-only writes into the story bible.

Novels, chapters and entities are MERGEd, so mentioning an entity again reuses its node.
Facts are always CREATEd, so a later chapter adds to an entity's history instead of
overwriting it. That history is what the consistency checker compares new claims against.
"""

from collections.abc import Mapping
from typing import Any

from continuity_editor.graph.connection import Neo4jConnection
from continuity_editor.graph.models import Chapter, Entity, Event, Fact, Novel, make_chapter_id
from continuity_editor.graph.schema import NodeLabel


def add_novel(conn: Neo4jConnection, novel: Novel) -> None:
    conn.write(
        "MERGE (n:Novel {novel_id: $novel.novel_id}) SET n.title = $novel.title",
        novel=novel.model_dump(),
    )


def add_chapter(conn: Neo4jConnection, chapter: Chapter) -> None:
    """Add a chapter to its novel and link it after the latest earlier chapter.

    Chapters are expected to arrive in reading order.
    """
    conn.write(
        """
        MERGE (n:Novel {novel_id: $chapter.novel_id})
        MERGE (ch:Chapter {chapter_id: $chapter.chapter_id})
        ON CREATE SET ch += $chapter
        MERGE (n)-[:HAS_CHAPTER]->(ch)
        WITH n, ch
        OPTIONAL MATCH (n)-[:HAS_CHAPTER]->(prev:Chapter)
        WHERE prev.number < ch.number
        WITH ch, prev
        ORDER BY prev.number DESC
        LIMIT 1
        FOREACH (p IN CASE WHEN prev IS NULL THEN [] ELSE [prev] END | MERGE (p)-[:NEXT]->(ch))
        """,
        chapter=chapter.model_dump(),
    )


def add_entity(conn: Neo4jConnection, entity: Entity, chapter: Chapter) -> None:
    """Record that `chapter` mentions `entity`, creating the entity on its first mention.

    On later mentions only new aliases (including a new name form) are added. The chapter
    must already exist (see add_chapter).
    """
    # Labels can't be query parameters; entity.label is always one of our NodeLabel values.
    conn.write(
        f"""
        MATCH (ch:Chapter {{chapter_id: $chapter_id}})
        MERGE (e:{NodeLabel.ENTITY}:{entity.label} {{entity_id: $entity.entity_id}})
        ON CREATE SET e += $entity
        ON MATCH SET e.aliases = coalesce(e.aliases, []) +
            [a IN $entity.aliases + [$entity.name] WHERE a <> e.name AND NOT a IN coalesce(e.aliases, [])]
        MERGE (ch)-[:MENTIONS]->(e)
        """,
        entity=entity.model_dump(),
        chapter_id=chapter.chapter_id,
    )


def add_fact(conn: Neo4jConnection, fact: Fact) -> None:
    """Attach a new fact to its entity, with provenance to the chapter that stated it."""
    chapter_id = make_chapter_id(fact.novel_id, fact.chapter_number)
    counters = conn.write(
        """
        MATCH (e:Entity {entity_id: $fact.subject_id})
        MATCH (ch:Chapter {chapter_id: $chapter_id})
        CREATE (e)-[:HAS_FACT]->(f:Fact)-[:STATED_IN]->(ch)
        SET f = $fact
        """,
        fact=fact.model_dump(),
        chapter_id=chapter_id,
    )
    if not counters.get("nodes_created"):
        raise ValueError(
            f"Fact not written: entity {fact.subject_id!r} or chapter {chapter_id!r} does not exist. "
            "Add them first with add_chapter and add_entity."
        )


def add_facts(conn: Neo4jConnection, facts: list[Fact]) -> None:
    """add_fact for a whole chapter's facts in one round trip. Every subject and chapter must exist."""
    if not facts:
        return
    rows = [
        {"props": f.model_dump(), "chapter_id": make_chapter_id(f.novel_id, f.chapter_number)} for f in facts
    ]
    counters = conn.write(
        """
        UNWIND $rows AS row
        MATCH (e:Entity {entity_id: row.props.subject_id})
        MATCH (ch:Chapter {chapter_id: row.chapter_id})
        CREATE (e)-[:HAS_FACT]->(f:Fact)-[:STATED_IN]->(ch)
        SET f = row.props
        """,
        rows=rows,
    )
    if counters.get("nodes_created", 0) != len(facts):
        raise ValueError("Some facts were not written: their entity or chapter does not exist.")


def add_events(conn: Neo4jConnection, events: list[Event]) -> None:
    """Add a chapter's events (in story order), linked to their chapter, participants and
    location, and chained with PRECEDES so the order is kept."""
    if not events:
        return
    rows = [
        {
            "props": e.model_dump(),
            "chapter_id": make_chapter_id(e.novel_id, e.chapter_number),
            "participant_ids": e.participant_ids,
            "location_id": e.location_id,
        }
        for e in events
    ]
    conn.write(
        """
        UNWIND $rows AS row
        MATCH (ch:Chapter {chapter_id: row.chapter_id})
        CREATE (ev:Event)-[:DESCRIBED_IN]->(ch)
        SET ev = row.props
        WITH ev, row
        OPTIONAL MATCH (p:Entity) WHERE p.entity_id IN row.participant_ids
        FOREACH (x IN CASE WHEN p IS NULL THEN [] ELSE [p] END | CREATE (x)-[:PARTICIPATES_IN]->(ev))
        WITH DISTINCT ev, row
        OPTIONAL MATCH (place:Entity {entity_id: row.location_id})
        FOREACH (x IN CASE WHEN place IS NULL THEN [] ELSE [place] END | CREATE (ev)-[:OCCURS_AT]->(x))
        """,
        rows=rows,
    )
    pairs = [[a.event_id, b.event_id] for a, b in zip(events, events[1:])]
    if pairs:
        conn.write(
            """
            UNWIND $pairs AS pair
            MATCH (a:Event {event_id: pair[0]}), (b:Event {event_id: pair[1]})
            CREATE (a)-[:PRECEDES]->(b)
            """,
            pairs=pairs,
        )


def add_contradictions(conn: Neo4jConnection, flags: list[Mapping[str, Any]]) -> None:
    """Link each flagged new fact to the earlier fact it contradicts.

    Each flag needs new_fact_id, prior_fact_id, confidence, reason and chapter_number.
    """
    if not flags:
        return
    conn.write(
        """
        UNWIND $flags AS flag
        MATCH (new:Fact {fact_id: flag.new_fact_id}), (old:Fact {fact_id: flag.prior_fact_id})
        CREATE (new)-[:CONTRADICTS {
            confidence: flag.confidence, reason: flag.reason, chapter_number: flag.chapter_number
        }]->(old)
        """,
        flags=[dict(f) for f in flags],
    )


def reset_novel(conn: Neo4jConnection, novel_id: str) -> dict[str, int]:
    """Delete every node of one novel, e.g. before re-running an evaluation from scratch."""
    return conn.write("MATCH (n {novel_id: $novel_id}) DETACH DELETE n", novel_id=novel_id)
