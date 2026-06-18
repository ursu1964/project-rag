"""Evidence agent.

Summarizes supplied evidence for research review. It performs no autonomous
experiments or external actions.
"""

from __future__ import annotations

from typing import Any


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Collect evidence already present in state into a structured summary."""
    evidence_items = []
    for key in ("graph_context", "vector_context", "memory_context", "digital_twin_context", "prediction_context"):
        value = state.get(key)
        if value:
            evidence_items.append({"source": key, "value": value})
    evidence_summary = {
        "items": evidence_items,
        "count": len(evidence_items),
        "status": "collected",
        "mode": "recommendation_only",
        "execution": "disabled",
    }
    return {**state, "evidence_summary": evidence_summary}
