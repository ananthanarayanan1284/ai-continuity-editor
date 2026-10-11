"""Neo4j tests. The live ones need credentials in .env and are skipped without them.

They write only under the novel id "pytest_novel" and delete it afterwards.
"""

import pytest

from continuity_editor.config import Neo4jSettings, get_neo4j_settings
from continuity_editor.graph import (
    Neo4jConnection,
    add_chapter,
    add_entity,
    add_fact,
    add_novel,
    apply_schema,
    describe_schema,
    reset_novel,
)
from continuity_editor.graph.models import Chapter, Character, Fact, Novel

TEST_NOVEL = "pytest_novel"

HISTORY = """
MATCH (e:Entity {entity_id: $entity_id})-[:HAS_FACT]->(f:Fact)-[:STATED_IN]->(ch:Chapter)
RETURN ch.number AS chapter, f.value AS value
ORDER BY chapter
"""


def test_driver_builds_without_connecting():
    settings = Neo4jSettings(
        neo4j_uri="neo4j+s://example.databases.neo4j.io",
        neo4j_username="neo4j",
        neo4j_password="not-a-real-password",
        _env_file=None,
    )
    with Neo4jConnection(settings) as conn:
        assert conn.settings.neo4j_uri.startswith("neo4j+s://")


@pytest.fixture(scope="module")
def conn():
    try:
        settings = get_neo4j_settings()
    except RuntimeError as exc:
        pytest.skip(str(exc))
    with Neo4jConnection(settings) as connection:
        apply_schema(connection)
        reset_novel(connection, TEST_NOVEL)
        yield connection
        reset_novel(connection, TEST_NOVEL)


@pytest.mark.integration
def test_verify(conn):
    assert conn.verify()["agent"].startswith("Neo4j/")


@pytest.mark.integration
def test_apply_schema_is_idempotent(conn):
    assert apply_schema(conn) == {"constraints_added": 0, "indexes_added": 0}
    names = {row["name"] for row in describe_schema(conn)["constraints"]}
    assert {"novel_id", "chapter_id", "entity_id", "event_id", "fact_id"} <= names


@pytest.mark.integration
def test_fact_history_keeps_every_version(conn):
    add_novel(conn, Novel(novel_id=TEST_NOVEL, title="Pytest Novel"))
    mira = Character(novel_id=TEST_NOVEL, name="Mira Voss")
    for number, colour in [(1, "blue"), (3, "green")]:
        chapter = Chapter(novel_id=TEST_NOVEL, number=number)
        add_chapter(conn, chapter)
        add_entity(conn, mira, chapter)
        add_fact(
            conn,
            Fact(
                novel_id=TEST_NOVEL,
                subject_id=mira.entity_id,
                attribute="eye_colour",
                value=colour,
                category="characterisation",
                evidence_span=f"her {colour} eyes",
                chapter_number=number,
            ),
        )

    rows = conn.query(HISTORY, entity_id=mira.entity_id)
    assert [(row["chapter"], row["value"]) for row in rows] == [(1, "blue"), (3, "green")]

    links = conn.query(
        "MATCH (a:Chapter {novel_id: $novel_id})-[:NEXT]->(b:Chapter) RETURN a.number AS a, b.number AS b",
        novel_id=TEST_NOVEL,
    )
    assert links == [{"a": 1, "b": 3}]


@pytest.mark.integration
def test_fact_for_unknown_entity_is_rejected(conn):
    add_chapter(conn, Chapter(novel_id=TEST_NOVEL, number=1))
    with pytest.raises(ValueError):
        add_fact(
            conn,
            Fact(
                novel_id=TEST_NOVEL,
                subject_id=f"{TEST_NOVEL}:character:nobody",
                attribute="age",
                value="30",
                category="characterisation",
                evidence_span="thirty years old",
                chapter_number=1,
            ),
        )
