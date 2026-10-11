"""Step 5: precision and recall against a test corpus with deliberately injected contradictions."""

from continuity_editor.evaluation.corpus import Injection, apply_injections, load_injections
from continuity_editor.evaluation.metrics import Evaluation, evaluate, false_alarms, hits
from continuity_editor.evaluation.report import render_report

__all__ = [
    "Evaluation",
    "Injection",
    "apply_injections",
    "evaluate",
    "false_alarms",
    "hits",
    "load_injections",
    "render_report",
]
