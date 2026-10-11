"""The consistency checker: prior-fact selection and flags (offline), plus live judge tests."""

import pytest

from continuity_editor.checking.checker import Verification, check_facts, final_confidence, judge, select_priors
from continuity_editor.graph.models import Fact
from continuity_editor.retrieval.history import PriorFact
from tests.conftest import FakeJudge

TOTO = "oz:character:toto"
CONTRADICTION = {"analysis": "Chapter 1 says black; chapter 7 says white.", "verdict": "high", "earlier_fact": 1}


def new_fact(attribute, value, evidence="Toto, the little white dog, ran on ahead of them.", chapter=7):
    return Fact(novel_id="oz", subject_id=TOTO, attribute=attribute, value=value, category="characterisation",
                evidence_span=evidence, chapter_number=chapter)


def prior(attribute, value, fact_id="p1", chapter=1,
          evidence="Toto was not gray; he was a little black dog, with long silky hair."):
    return PriorFact(fact_id=fact_id, entity_id=TOTO, chapter=chapter, attribute=attribute, value=value,
                     category="characterisation", evidence=evidence)


def test_a_different_value_for_a_related_attribute_is_compared():
    priors = [prior("appearance", "a little black dog"), prior("home", "Kansas", fact_id="p2")]
    assert [p.fact_id for p in select_priors(new_fact("colour", "white"), priors)] == ["p1"]


def test_a_restatement_is_not_compared():
    assert select_priors(new_fact("appearance", "a little black dog"), [prior("appearance", "a little black dog")]) == []


def test_a_negation_is_not_a_restatement():
    assert select_priors(new_fact("colour", "green"), [prior("colour", "not green")]) != []


def test_unrelated_facts_are_not_compared():
    assert select_priors(new_fact("occupation", "farmer"), [prior("eye_colour", "black")]) == []


def test_a_contradiction_becomes_a_flag_citing_both_facts():
    flags = check_facts(
        FakeJudge(CONTRADICTION), [new_fact("colour", "white")], {TOTO: [prior("appearance", "a little black dog")]},
        {TOTO: "Toto"},
    )
    assert len(flags) == 1
    flag = flags[0]
    assert (flag.entity_name, flag.confidence, flag.prior_chapter, flag.prior_value, flag.new_value) == (
        "Toto", "high", 1, "a little black dog", "white"
    )


def test_the_llm_is_not_asked_when_there_is_nothing_to_compare():
    llm = FakeJudge(CONTRADICTION)
    assert check_facts(llm, [new_fact("colour", "white")], {}, {}) == []
    assert llm.calls == 0


def test_the_double_check_drops_statements_about_different_properties():
    different = {"reason": "Likes vs friendliness.", "same_property": False, "both_can_be_true": True}
    llm = FakeJudge(CONTRADICTION, verification=different)
    assert check_facts(llm, [new_fact("colour", "white")], {TOTO: [prior("appearance", "a little black dog")]}, {}) == []
    assert llm.calls == 2  # the judgement and the double-check


def test_the_double_check_lowers_a_clash_that_both_statements_could_survive():
    explained = {"reason": "Green glasses explain it.", "same_property": True, "both_can_be_true": True}
    flags = check_facts(FakeJudge(CONTRADICTION, verification=explained), [new_fact("colour", "white")],
                        {TOTO: [prior("appearance", "a little black dog")]}, {})
    assert [f.confidence for f in flags] == ["low"]
    assert "Double-check: Green glasses explain it." in flags[0].reason


def test_final_confidence_after_the_double_check():
    clash = Verification(reason="", same_property=True, both_can_be_true=False)
    assert final_confidence("high", clash) == "high"
    assert final_confidence("medium", clash) == "medium"
    assert final_confidence("low", clash) == "medium"  # confirmed: no longer a mere surface mismatch


def test_a_consistent_verdict_is_not_flagged():
    llm = FakeJudge({"analysis": "It only adds detail.", "verdict": "no contradiction", "earlier_fact": 1})
    assert check_facts(llm, [new_fact("colour", "white")], {TOTO: [prior("appearance", "a little black dog")]}, {}) == []


@pytest.mark.integration
def test_live_judge_flags_a_colour_change(live_llm):
    verdict = judge(live_llm, "Toto", new_fact("colour", "white"), [prior("appearance", "a little black dog")])
    assert verdict.verdict in {"high", "medium"}


@pytest.mark.integration
def test_live_judge_accepts_an_added_detail(live_llm):
    detail = new_fact("appearance", "long silky hair", "Toto's long silky hair blew about in the wind.")
    verdict = judge(live_llm, "Toto", detail, [prior("appearance", "a little black dog")])
    assert verdict.verdict == "no contradiction"


@pytest.mark.integration
def test_live_judge_rates_a_lighting_mismatch_low(live_llm):
    """The PDF's example: a mismatch that context explains is flagged, but only as "low"."""
    glow = new_fact("colour", "looked almost green",
                    "In the green glow of the Emerald City, even Toto looked almost green.")
    verdict = judge(live_llm, "Toto", glow, [prior("appearance", "a little black dog")])
    assert verdict.verdict == "low"
