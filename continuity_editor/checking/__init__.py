"""Step 4: compare new claims with retrieved history and flag contradictions with a cited
reason and a high / medium / low confidence tier."""

from continuity_editor.checking.checker import (
    Flag,
    Judgement,
    Verification,
    check_facts,
    final_confidence,
    judge,
    select_priors,
    verify,
)

__all__ = ["Flag", "Judgement", "Verification", "check_facts", "final_confidence", "judge", "select_priors", "verify"]
