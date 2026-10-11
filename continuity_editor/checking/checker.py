"""Step 4: compare each new fact with its entity's history and flag contradictions.

For every new fact, cheap text rules pick the earlier facts worth comparing (a related
attribute, a different value). The LLM is asked only when there is such a fact, and answers
with a short analysis, a verdict and a confidence tier:
- high: a direct clash of facts;
- medium: probably a mistake, but a change of circumstances might explain it;
- low: a surface mismatch that context could explain (lighting, disguise, opinion).

Every would-be flag then gets a double-check: a second, narrower question about just the two
statements. Statements about different properties are dropped; a clash that both statements
could survive is kept only as "low"; a confirmed clash keeps its tier (a "low" becomes "medium").
"""

import re
from typing import Literal

from pydantic import BaseModel, ValidationError, create_model
from rapidfuzz import fuzz

from continuity_editor.checking.prompts import CHECK_SYSTEM, VERIFY_SYSTEM
from continuity_editor.graph.models import Fact
from continuity_editor.llm import LLMClient
from continuity_editor.retrieval.history import PriorFact

Confidence = Literal["high", "medium", "low"]

MAX_PRIORS = 6  # earlier facts shown to the judge for one new fact
RELEVANCE_MIN = 80  # 0-100; below this an earlier fact is about something else
SAME_VALUE_MIN = 90  # 0-100; at or above this the new fact just restates an earlier one

# Attribute labels vary ("eye_colour", "appearance", "looks"), so related labels are grouped by
# the words they contain. Two facts whose attributes share a group are worth comparing.
ATTRIBUTE_FAMILIES: dict[str, set[str]] = {
    "appearance": {"appearance", "colour", "color", "eye", "eyes", "hair", "fur", "coat", "height", "size", "build",
                   "body", "shape", "face", "skin", "cheek", "beard", "clothing", "clothes", "dress", "wears", "looks"},
    "home": {"home", "lives", "living", "residence", "location", "origin", "born", "birthplace", "country"},
    "occupation": {"occupation", "job", "profession", "work", "trade", "role", "title", "ruler"},
    "age": {"age", "old"},
    "nature": {"species", "made", "material", "stuffed", "stuffing", "type", "nature", "composition"},
    "relationship": {"relationship", "sister", "brother", "mother", "father", "aunt", "uncle", "wife",
                     "husband", "friend", "enemy", "married", "servant", "master"},
    "possession": {"owns", "possession", "possessions", "has", "carries", "belongs", "wears"},
    "goal": {"want", "wants", "wish", "wishes", "desire", "desires", "goal", "needs", "seeks", "hopes"},
    "ability": {"ability", "abilities", "power", "powers", "magic", "can", "cannot", "skill"},
    "rule": {"rule", "rules", "limit", "limits", "charm", "law", "must", "uses"},
    "count": {"count", "number", "times", "many", "limit", "uses"},
    "time": {"time", "duration", "days", "years", "when", "date", "season", "since"},
}
_NEGATION = {"not", "no", "never", "without", "none", "nothing"}


class Flag(BaseModel):
    """A contradiction between a new fact and an earlier one, with the checker's reasoning."""

    novel_id: str
    chapter_number: int
    entity_id: str
    entity_name: str
    category: str
    new_fact_id: str
    new_attribute: str
    new_value: str
    new_evidence: str
    prior_fact_id: str
    prior_chapter: int
    prior_attribute: str
    prior_value: str
    prior_evidence: str
    confidence: Confidence
    reason: str


class Judgement(BaseModel):
    # One verdict rather than a yes/no plus a separate tier: a small model otherwise answers
    # "contradiction" and leaves the tier empty.
    analysis: str
    verdict: Literal["high", "medium", "low", "no contradiction"]
    earlier_fact: int


class Verification(BaseModel):
    reason: str
    same_property: bool
    both_can_be_true: bool


def families(attribute: str) -> set[str]:
    words = set(attribute.lower().split("_"))
    return {family for family, keys in ATTRIBUTE_FAMILIES.items() if words & keys}


def relevance(fact: Fact, prior: PriorFact) -> float:
    """How likely `prior` is about the same thing as `fact`, 0-100."""
    if fact.attribute == prior.attribute:
        return 100.0
    if families(fact.attribute) & families(prior.attribute):
        return 90.0
    return fuzz.token_set_ratio(
        f"{fact.attribute.replace('_', ' ')} {fact.value}", f"{prior.attribute.replace('_', ' ')} {prior.value}"
    )


def select_priors(fact: Fact, priors: list[PriorFact]) -> list[PriorFact]:
    """The earlier facts worth comparing with `fact`, most relevant first. Empty when there is
    nothing to compare, or when `fact` just restates an earlier fact."""
    scored = sorted(((relevance(fact, p), p) for p in priors), key=lambda pair: -pair[0])
    relevant = [p for score, p in scored if score >= RELEVANCE_MIN][:MAX_PRIORS]
    if any(p.attribute == fact.attribute and _same_value(p.value, fact.value) for p in relevant):
        return []
    return relevant


def judge(llm: LLMClient, entity_name: str, fact: Fact, priors: list[PriorFact]) -> Judgement:
    earlier = "\n".join(
        f'{i}. (chapter {p.chapter}) {p.attribute.replace("_", " ")}: {p.value}. Quote: "{p.evidence}"'
        for i, p in enumerate(priors, 1)
    )
    prompt = (
        f"Entity: {entity_name}\n\nEarlier facts:\n{earlier}\n\n"
        f"New statement (chapter {fact.chapter_number}): {fact.attribute.replace('_', ' ')}: {fact.value}. "
        f'Quote: "{fact.evidence_span}"'
    )
    schema = create_model("Judgement", __base__=Judgement, earlier_fact=(Literal[tuple(range(1, len(priors) + 1))], ...))
    return llm.structured(prompt, schema, system=CHECK_SYSTEM, max_tokens=300)


def verify(llm: LLMClient, entity_name: str, fact: Fact, prior: PriorFact) -> Verification:
    """The double-check: a narrower second look at just the two statements."""
    prompt = (
        f"Entity: {entity_name}\n\n"
        f'Earlier (chapter {prior.chapter}): {prior.attribute.replace("_", " ")}: {prior.value}. '
        f'Quote: "{prior.evidence}"\n'
        f"Later (chapter {fact.chapter_number}): {fact.attribute.replace('_', ' ')}: {fact.value}. "
        f'Quote: "{fact.evidence_span}"'
    )
    return llm.structured(prompt, Verification, system=VERIFY_SYSTEM, max_tokens=200)


def final_confidence(verdict: Confidence, check: Verification) -> Confidence | None:
    """The tier after the double-check, or None when the flag is dropped."""
    if not check.same_property:
        return None
    if check.both_can_be_true:
        return "low"
    return "high" if verdict == "high" else "medium"


def check_facts(
    llm: LLMClient, facts: list[Fact], history: dict[str, list[PriorFact]], names: dict[str, str]
) -> list[Flag]:
    """Flag every new fact that contradicts its entity's history."""
    flags = []
    for fact in facts:
        priors = select_priors(fact, history.get(fact.subject_id, []))
        if not priors:
            continue
        name = names.get(fact.subject_id, fact.subject_id)
        try:
            verdict = judge(llm, name, fact, priors)
        except ValidationError:  # an unusable answer: skip rather than guess
            continue
        if verdict.verdict == "no contradiction":
            continue
        prior = priors[verdict.earlier_fact - 1]
        confidence, reason = verdict.verdict, verdict.analysis.strip()
        try:
            check = verify(llm, name, fact, prior)
        except ValidationError:  # no usable double-check: keep the first verdict
            check = None
        if check is not None:
            confidence = final_confidence(verdict.verdict, check)
            if confidence is None:
                continue
            reason = f"{reason} Double-check: {check.reason.strip()}"
        flags.append(
            Flag(
                novel_id=fact.novel_id,
                chapter_number=fact.chapter_number,
                entity_id=fact.subject_id,
                entity_name=names.get(fact.subject_id, fact.subject_id),
                category=fact.category,
                new_fact_id=fact.fact_id,
                new_attribute=fact.attribute,
                new_value=fact.value,
                new_evidence=fact.evidence_span,
                prior_fact_id=prior.fact_id,
                prior_chapter=prior.chapter,
                prior_attribute=prior.attribute,
                prior_value=prior.value,
                prior_evidence=prior.evidence,
                confidence=confidence,
                reason=reason,
            )
        )
    return flags


def _same_value(a: str, b: str) -> bool:
    """True if two values say the same thing. "green" and "not green" are different."""
    negated_a = bool(_NEGATION & set(re.findall(r"[a-z]+", a.lower())))
    negated_b = bool(_NEGATION & set(re.findall(r"[a-z]+", b.lower())))
    return negated_a == negated_b and fuzz.token_set_ratio(a, b) >= SAME_VALUE_MIN
