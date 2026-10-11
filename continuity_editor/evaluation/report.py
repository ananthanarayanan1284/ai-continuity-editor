"""A readable Markdown report of an evaluation run."""

from continuity_editor.checking.checker import Flag
from continuity_editor.evaluation.corpus import Injection
from continuity_editor.evaluation.metrics import Evaluation, false_alarms


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.0%}"


def _cell(text: str | None, limit: int = 140) -> str:
    text = (text or "").replace("|", "/").replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render_report(
    evaluation: Evaluation,
    injected_flags: list[Flag],
    clean_flags: list[Flag] | None,
    injections: list[Injection],
    meta: dict[str, str],
) -> str:
    e = evaluation
    lines = [
        "# Evaluation: injected contradictions",
        "",
        " · ".join(f"**{k}:** {v}" for k, v in meta.items()),
        "",
        "## Summary",
        "",
        "| Measure | Value |",
        "|---|---|",
        f"| Injected contradictions | {e.contradictions} |",
        f"| Detected (recall) | {e.detected} ({_pct(e.recall)}) |",
        f"| Detected in the injected chapter itself | {e.detected_in_chapter} |",
        f"| Flags raised on the test corpus | {e.flags} |",
        f"| Flags that point at an injected contradiction (precision) | {e.true_positive_flags} ({_pct(e.precision)}) |",
        f"| False alarms on harmless control edits | {e.control_false_alarms} |",
        f"| Confidence tier matches the expected tier | {_pct(e.tier_agreement)} |",
    ]
    if clean_flags is not None:
        lines.append(f"| Flags on the original, unedited book (all false alarms) | {len(clean_flags)} |")

    lines += ["", "## Recall by category", "", "| Category | Injected | Detected | Recall |", "|---|---|---|---|"]
    for category, row in e.by_category.items():
        lines.append(f"| {category} | {row['injected']:.0f} | {row['detected']:.0f} | {_pct(row['recall'])} |")

    lines += ["", "## Precision by confidence tier", "", "| Tier | Flags | Pointing at an injection | Precision |",
              "|---|---|---|---|"]
    for tier, row in e.by_confidence.items():
        lines.append(f"| {tier} | {row['flags']:.0f} | {row['true_positives']:.0f} | {_pct(row['precision'])} |")

    lines += ["", "## Every injected contradiction", "",
              "| Id | Ch | Category | Injected text | Detected | Expected tier | Flagged tier | Checker's reason |",
              "|---|---|---|---|---|---|---|---|"]
    for r in e.injections:
        found = "yes" if r.detected_in_chapter else ("later" if r.detected else "**no**")
        lines.append(
            f"| {r.id} | {r.chapter} | {r.category} | {_cell(r.replace, 90)} | {found} | {r.expected_confidence} | "
            f"{r.predicted_confidence or '-'} | {_cell(r.reason)} |"
        )

    alarms = false_alarms(injected_flags, injections)
    lines += ["", f"## False alarms on the test corpus ({len(alarms)})", "",
              "| Ch | Entity | New statement | Earlier fact | Tier | Checker's reason |", "|---|---|---|---|---|---|"]
    for flag in alarms:
        lines.append(
            f"| {flag.chapter_number} | {_cell(flag.entity_name, 40)} | {flag.new_attribute}: {_cell(flag.new_value, 50)} | "
            f"ch{flag.prior_chapter} {flag.prior_attribute}: {_cell(flag.prior_value, 50)} | {flag.confidence} | "
            f"{_cell(flag.reason)} |"
        )
    return "\n".join(lines) + "\n"
