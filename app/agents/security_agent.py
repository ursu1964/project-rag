"""Security agent for MVP risk classification."""

from __future__ import annotations


def run(state: dict) -> dict:
    objective = str(state.get("objective") or state.get("question") or "").lower()
    high_risk_terms = ("delete", "destroy", "credential", "secret", "public", "firewall", "production", "execute", "deploy")
    risk = "high" if any(term in objective for term in high_risk_terms) else "medium"
    security = {
        "risk": risk,
        "execution_allowed": False,
        "blocked": True,
        "reason": "Execution is blocked by default until approval mode exists.",
    }
    return {**state, "security": security}
