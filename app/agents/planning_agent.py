"""Planning agent for safe recommendations."""

from __future__ import annotations


def run(state: dict) -> dict:
    objective = str(state.get("objective") or state.get("question") or "")
    tasks = state.get("tasks") or [objective]
    plan = [
        {"step": index + 1, "action": task, "mode": "recommendation_only", "requires_approval": True}
        for index, task in enumerate(tasks)
    ]
    return {**state, "plan": plan}
