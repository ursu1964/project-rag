"""Answer validation agent."""

from __future__ import annotations

from app.core.config import settings
from app.core.timing import elapsed_ms, now_ms
from app.tools.safety import classify_question_risk
from app.validation.llm_judge import judge_answer


def run(state: dict) -> dict:
    start_ms = now_ms()
    answer = str(state.get("answer") or "").strip()
    question = str(state.get("question") or state.get("objective") or "")
    safety = classify_question_risk(question)
    evidence = state.get("evidence") or []
    warnings = []

    if not answer:
        warnings.append("missing_answer")
    if not evidence:
        warnings.append("missing_evidence")

    uncertain_phrases = ("i do not know", "insufficient", "not enough context", "unknown")
    uncertain = any(phrase in answer.lower() for phrase in uncertain_phrases)
    grounded = bool(answer and evidence and not uncertain)
    confidence = 0.8 if grounded else 0.2 if answer else 0.0
    requires_human_approval = bool(safety["requires_human_approval"]) or not grounded or confidence < 0.5
    llm_judge = None
    if settings.use_llm_judge:
        llm_judge = judge_answer(question, answer, evidence)
        confidence = min(confidence, float(llm_judge.get("groundedness", confidence)))
        requires_human_approval = requires_human_approval or confidence < 0.5

    metrics = {**(state.get("metrics") or {}), "validation_ms": elapsed_ms(start_ms)}
    return {
        **state,
        "metrics": metrics,
        "validation": {
            "grounded": grounded,
            "confidence": confidence,
            "warnings": warnings,
            "requires_human_approval": requires_human_approval,
            "safety": safety,
            "llm_judge": llm_judge,
        },
    }
