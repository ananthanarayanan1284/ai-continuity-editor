"""End-to-end pipeline on a tiny two-chapter book: live Neo4j, stand-in judge.

Writes only under the novel id "pytest_pipeline" and deletes it afterwards.
"""

import pytest

from continuity_editor.extraction.chapters import ChapterText
from continuity_editor.extraction.schemas import ChapterExtraction, ExtractedEntity, ExtractedEvent, ExtractedFact
from continuity_editor.graph import reset_novel
from continuity_editor.pipeline import run_novel
from tests.conftest import FakeJudge

NOVEL = "pytest_pipeline"


def extraction(number, entities, facts, events=()):
    return ChapterExtraction(
        novel_id=NOVEL, chapter_number=number, chapter_title=f"Chapter {number}", text_hash="x", model="fake",
        extraction_version="test", seconds=0, entities=entities, facts=facts, events=list(events),
    )


@pytest.mark.integration
def test_a_contradiction_is_flagged_and_linked_in_the_graph(neo4j_conn):
    toto = ExtractedEntity(name="Toto", kind="character")
    kansas = ExtractedEntity(name="Kansas", kind="location")
    chapter1 = extraction(
        1, [toto, kansas],
        [ExtractedFact(subject="Toto", attribute="appearance", value="a little black dog",
                       category="characterisation", evidence="Toto was a little black dog.")],
        [ExtractedEvent(description="Toto plays", participants=["Toto"], location="Kansas",
                        evidence="Toto played all day long in Kansas.")],
    )
    chapter2 = extraction(
        2, [ExtractedEntity(name="Toto", kind="character", aliases=["the dog"])],
        [ExtractedFact(subject="the dog", attribute="colour", value="white",
                       category="characterisation", evidence="Toto, the little white dog, ran ahead.")],
    )
    judge = FakeJudge({"analysis": "Black in chapter 1, white in chapter 2.", "verdict": "high", "earlier_fact": 1})
    try:
        flags = run_novel(neo4j_conn, judge, NOVEL, "Pipeline test",
                          [ChapterText(1, "One", ""), ChapterText(2, "Two", "")], [chapter1, chapter2])
        assert [(f.chapter_number, f.prior_chapter, f.confidence) for f in flags] == [(2, 1, "high")]

        links = neo4j_conn.query(
            "MATCH (n:Fact)-[c:CONTRADICTS]->(o:Fact) WHERE n.novel_id = $novel "
            "RETURN n.value AS new, o.value AS old, c.confidence AS confidence",
            novel=NOVEL,
        )
        assert links == [{"new": "white", "old": "a little black dog", "confidence": "high"}]
        counts = neo4j_conn.query(
            "MATCH (e:Entity {novel_id: $novel}) WITH count(e) AS entities "
            "MATCH (:Character {novel_id: $novel})-[:PARTICIPATES_IN]->(:Event)-[:OCCURS_AT]->(:Location) "
            "RETURN entities, count(*) AS event_links",
            novel=NOVEL,
        )
        assert counts == [{"entities": 2, "event_links": 1}]  # "Toto" in chapter 2 is the same entity
    finally:
        reset_novel(neo4j_conn, NOVEL)
