"""Offline tests for the test corpus and the scoring."""

import pytest

from continuity_editor.checking.checker import Flag
from continuity_editor.evaluation import Injection, apply_injections, evaluate, load_injections, render_report
from continuity_editor.extraction import load_chapters
from continuity_editor.extraction.chapters import ChapterText
from continuity_editor.paths import DATA_DIR, chapters_path

WHITE_DOG = Injection(
    id="I01", kind="contradiction", chapter=2, category="characterisation", expected_confidence="high",
    find="Toto ran ahead.", replace="Toto, the little white dog, ran ahead.",
)
CONTROL = Injection(id="K01", kind="control", chapter=2, find="Dorothy smiled.", replace="Dorothy, the farm girl, smiled.")


def flag(chapter, new_evidence, prior_chapter=1, prior_evidence="Toto was a little black dog.", confidence="high"):
    return Flag(
        novel_id="t", chapter_number=chapter, entity_id="t:character:toto", entity_name="Toto",
        category="characterisation", new_fact_id="n", new_attribute="colour", new_value="white",
        new_evidence=new_evidence, prior_fact_id="p", prior_chapter=prior_chapter, prior_attribute="appearance",
        prior_value="a little black dog", prior_evidence=prior_evidence, confidence=confidence, reason="black vs white",
    )


def test_injections_are_applied_where_they_belong():
    chapters = [ChapterText(1, "One", "Toto was a little black dog."), ChapterText(2, "Two", "Toto ran ahead. Dorothy smiled.")]
    changed = apply_injections(chapters, [WHITE_DOG, CONTROL])
    assert changed[0].text == chapters[0].text
    assert changed[1].text == "Toto, the little white dog, ran ahead. Dorothy, the farm girl, smiled."


def test_an_injection_that_does_not_fit_exactly_once_is_refused():
    with pytest.raises(ValueError):
        apply_injections([ChapterText(2, "Two", "No dog here.")], [WHITE_DOG])


def test_scoring_counts_hits_false_alarms_and_tiers():
    flags = [
        flag(2, "Toto, the little white dog, ran ahead."),  # hits I01
        flag(2, "Dorothy, the farm girl, smiled.", confidence="low"),  # a false alarm on the control
    ]
    result = evaluate(flags, [WHITE_DOG, CONTROL])
    assert (result.detected, result.recall, result.true_positive_flags, result.precision) == (1, 1.0, 1, 0.5)
    assert result.control_false_alarms == 1
    assert result.tier_agreement == 1.0
    assert result.by_confidence["low"] == {"flags": 1, "true_positives": 0, "precision": 0.0}


def test_a_later_flag_citing_the_injection_as_the_earlier_fact_counts_as_detected():
    later = flag(5, "Toto was black as ever.", prior_chapter=2, prior_evidence="Toto, the little white dog, ran ahead.")
    result = evaluate([later], [WHITE_DOG])
    assert result.detected == 1
    assert result.detected_in_chapter == 0


def test_the_report_lists_every_injection():
    result = evaluate([flag(2, "Toto, the little white dog, ran ahead.")], [WHITE_DOG, CONTROL])
    report = render_report(result, [], None, [WHITE_DOG, CONTROL], {"model": "fake"})
    assert "| I01 | 2 | characterisation |" in report


def test_the_real_oz_injections_all_apply():
    path = chapters_path("oz")
    if not path.exists():
        pytest.skip("run scripts/prepare_novel.py first")
    injections = load_injections(DATA_DIR / "test_corpus" / "oz_injections.json")
    changed = apply_injections(load_chapters(path), injections)
    for injection in injections:
        assert injection.replace in changed[injection.chapter - 1].text
