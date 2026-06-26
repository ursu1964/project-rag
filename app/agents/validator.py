"""Answer validation agent."""

from __future__ import annotations

from app.core.config import settings
from app.core.timing import elapsed_ms, now_ms


def run(state: dict) -> dict:
    start = now_ms()
    answer = str(state.get("answer") or "")
    evidence = state.get("evidence") or []
    warnings: list[str] = []
    if not answer:
        warnings.append("missing_answer")
    if not evidence:
        warnings.append("missing_evidence")
    answer_for_validation = answer.split("\nRules:", 1)[0].lower()
    uncertain = any(term in answer_for_validation for term in ("i do not know", "insufficient", "not enough context", "unknown"))
    grounded = bool(answer and evidence and not uncertain)
    confidence = 0.8 if grounded else 0.2 if answer else 0.0
    metrics = {**(state.get("metrics") or {}), "validation_ms": elapsed_ms(start)}
    return {
        **state,
        "metrics": metrics,
        "validation": {
            "grounded": grounded,
            "confidence": confidence,
            "warnings": warnings,
            "requires_human_approval": not grounded or confidence < 0.5,
            "llm_judge": None if not settings.use_llm_judge else {},
        },
    }
