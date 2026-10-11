"""Scoring the checker's flags against the injected contradictions.

A flag *hits* an injection when it cites the injected text: either as the new statement in
the injected chapter, or as the earlier fact when a later chapter restates the original
detail (the error is then caught one step late, but it is caught).

- recall: the share of injected contradictions hit by at least one flag;
- precision: the share of flags that hit an injected contradiction (every other flag,
  including one on a harmless control edit, is a false alarm);
- tier agreement: for hit injections, how often the flag's confidence matches the expected one.
"""

from collections.abc import Iterable

from pydantic import BaseModel
from rapidfuzz import fuzz

from continuity_editor.checking.checker import Confidence, Flag
from continuity_editor.evaluation.corpus import Injection

MATCH_MIN_SCORE = 85  # rapidfuzz partial_ratio between a flag's quote and the injected text
TIERS: tuple[Confidence, ...] = ("high", "medium", "low")


class InjectionResult(BaseModel):
    id: str
    kind: str
    chapter: int
    category: str | None
    expected_confidence: str | None
    replace: str
    detected: bool
    detected_in_chapter: bool  # flagged when the injected chapter itself was checked
    predicted_confidence: str | None
    reason: str | None


class Evaluation(BaseModel):
    contradictions: int
    detected: int
    detected_in_chapter: int
    recall: float
    flags: int
    true_positive_flags: int
    precision: float | None
    control_false_alarms: int
    tier_agreement: float | None
    by_category: dict[str, dict[str, float]]
    by_confidence: dict[str, dict[str, float]]
    injections: list[InjectionResult]


def hits(flag: Flag, injection: Injection) -> bool:
    if flag.chapter_number == injection.chapter and _cites(flag.new_evidence, injection):
        return True
    return flag.prior_chapter == injection.chapter and _cites(flag.prior_evidence, injection)


def evaluate(flags: list[Flag], injections: list[Injection]) -> Evaluation:
    contradictions = [i for i in injections if i.kind == "contradiction"]
    controls = [i for i in injections if i.kind == "control"]

    results, true_positive = [], set()
    for injection in contradictions:
        matched = [n for n, flag in enumerate(flags) if hits(flag, injection)]
        true_positive.update(matched)
        in_chapter = [n for n in matched if flags[n].chapter_number == injection.chapter]
        first = flags[(in_chapter or matched)[0]] if matched else None
        results.append(
            InjectionResult(
                id=injection.id,
                kind=injection.kind,
                chapter=injection.chapter,
                category=injection.category,
                expected_confidence=injection.expected_confidence,
                replace=injection.replace,
                detected=bool(matched),
                detected_in_chapter=bool(in_chapter),
                predicted_confidence=first.confidence if first else None,
                reason=first.reason if first else None,
            )
        )

    detected = [r for r in results if r.detected]
    rated = [r for r in detected if r.expected_confidence]
    by_category = {}
    for category in sorted({r.category for r in results if r.category}):
        group = [r for r in results if r.category == category]
        found = sum(r.detected for r in group)
        by_category[category] = {"injected": len(group), "detected": found, "recall": _ratio(found, len(group))}
    by_confidence = {}
    for tier in TIERS:
        tier_flags = [n for n, flag in enumerate(flags) if flag.confidence == tier]
        correct = len([n for n in tier_flags if n in true_positive])
        by_confidence[tier] = {"flags": len(tier_flags), "true_positives": correct,
                               "precision": _ratio(correct, len(tier_flags))}

    return Evaluation(
        contradictions=len(contradictions),
        detected=len(detected),
        detected_in_chapter=sum(r.detected_in_chapter for r in results),
        recall=_ratio(len(detected), len(contradictions)),
        flags=len(flags),
        true_positive_flags=len(true_positive),
        precision=_ratio(len(true_positive), len(flags)) if flags else None,
        control_false_alarms=sum(any(hits(flag, c) for c in controls) for flag in flags),
        tier_agreement=_ratio(sum(r.predicted_confidence == r.expected_confidence for r in rated), len(rated))
        if rated else None,
        by_category=by_category,
        by_confidence=by_confidence,
        injections=results,
    )


def false_alarms(flags: list[Flag], injections: Iterable[Injection]) -> list[Flag]:
    """Flags that hit no injected contradiction."""
    contradictions = [i for i in injections if i.kind == "contradiction"]
    return [flag for flag in flags if not any(hits(flag, i) for i in contradictions)]


def _cites(evidence: str, injection: Injection) -> bool:
    return fuzz.partial_ratio(injection.replace.casefold(), evidence.casefold()) >= MATCH_MIN_SCORE


def _ratio(part: int, whole: int) -> float:
    return round(part / whole, 3) if whole else 0.0
