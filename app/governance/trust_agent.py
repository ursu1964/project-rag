"""Trust agent for deterministic trust scoring.

This module estimates trust from validation, evidence, and policy signals. It is
recommendation-only and does not grant authority.
"""

from __future__ import annotations

from typing import Any


def calculate_trust_score(state: dict[str, Any]) -> dict[str, Any]:
    """Calculate a bounded trust score from available governance signals."""
    validation = state.get("validation") or {}
    evidence = state.get("evidence") or state.get("evidence_summary") or {}
    violations = state.get("policy_violations") or state.get("violations") or []

    grounded_bonus = 0.35 if validation.get("grounded") else 0.0
    confidence_bonus = min(0.35, float(validation.get("confidence", 0.0)) * 0.35)
    evidence_bonus = 0.2 if evidence else 0.0
    violation_penalty = min(0.6, len(violations) * 0.2)
    score = round(max(0.0, min(1.0, 0.1 + grounded_bonus + confidence_bonus + evidence_bonus - violation_penalty)), 6)

    if score >= 0.75:
        level = "high"
    elif score >= 0.45:
        level = "medium"
    else:
        level = "low"
    return {
        "trust_score": score,
        "trust_level": level,
        "signals": {
            "grounded": bool(validation.get("grounded")),
            "validation_confidence": float(validation.get("confidence", 0.0)),
            "has_evidence": bool(evidence),
            "violation_count": len(violations),
        },
        "mode": "recommendation_only",
        "execution": "disabled",
    }


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Agent-compatible trust scoring entrypoint."""
    return {**state, "trust": calculate_trust_score(state)}
