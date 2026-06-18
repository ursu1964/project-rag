"""Answer validation agent."""

from __future__ import annotations

from app.core.config import settings
from app.core.timing import elapsed_ms, now_ms
from app.tools.safety import classify_question_risk
from app.validation.llm_judge import judge_answer

_UNCERTAIN_PHRASES = ("i do not know", "insufficient", "not enough context", "unknown", "cannot determine", "no information")


def _calibrate_confidence(
    base: float,
    evidence_summary: dict,
    evidence: list,
) -> float:
    """Calibrate confidence using evidence signals from the context merger.

    Signals used (all from existing pipeline output, no new deps):
    - top_score: highest reranked evidence relevance score (0–1)
    - total_evidence: number of evidence items assembled
    - vector_count / graph_count: coverage breadth
    """
    confidence = base
    top_score = float(evidence_summary.get("top_score") or 0.0)
    total_ev = int(evidence_summary.get("total_evidence") or len(evidence))
    graph_count = int(evidence_summary.get("graph_count") or 0)
    vector_count = int(evidence_summary.get("vector_count") or 0)

    # Blend base confidence with top evidence relevance score
    if top_score > 0:
        confidence = 0.55 * base + 0.45 * top_score

    # Penalise if very little evidence assembled, but don't destroy high-quality single items
    if total_ev == 0:
        confidence = min(confidence, 0.10)
    elif total_ev == 1:
        confidence = min(confidence, 0.65)

    # Bonus for breadth: both graph and vector evidence present
    if graph_count > 0 and vector_count > 0:
        confidence = min(1.0, confidence + 0.05)

    return round(max(0.0, min(1.0, confidence)), 4)


def run(state: dict) -> dict:
    start_ms = now_ms()
    answer = str(state.get("answer") or "").strip()
    question = str(state.get("question") or state.get("objective") or "")
    safety = classify_question_risk(question)
    evidence = state.get("evidence") or []
    evidence_summary: dict = state.get("evidence_summary") or {}
    warnings = []

    if not answer:
        warnings.append("missing_answer")
    if not evidence:
        warnings.append("missing_evidence")

    answer_for_validation = answer.split("\nRules:", 1)[0]
    uncertain = any(phrase in answer_for_validation.lower() for phrase in _UNCERTAIN_PHRASES)
    grounded = bool(answer and evidence and not uncertain)
    base_confidence = 0.8 if grounded else 0.2 if answer else 0.0
    confidence = _calibrate_confidence(base_confidence, evidence_summary, evidence)

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
            "evidence_calibration": {
                "top_score": float(evidence_summary.get("top_score") or 0.0),
                "total_evidence": int(evidence_summary.get("total_evidence") or 0),
                "graph_count": int(evidence_summary.get("graph_count") or 0),
                "vector_count": int(evidence_summary.get("vector_count") or 0),
            },
        },
    }
