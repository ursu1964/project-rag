"""Safe deterministic cognitive workflow placeholder."""

from __future__ import annotations


class _Workflow:
    def invoke(self, state: dict) -> dict:
        objective = str(state.get("objective") or state.get("question") or "")
        return {
            **state,
            "chief_summary": {"objective": objective, "mode": "recommendation_only"},
            "plan": ["Analyze evidence", "Prepare recommendation", "Require human approval before action"],
            "security": {"blocked": True, "reason": "execution_disabled"},
            "cost": {"estimated": 0.0},
            "validation": {"grounded": True, "requires_human_approval": True},
            "lessons_learned": [],
        }


def build_workflow() -> _Workflow:
    return _Workflow()
