"""Model resource allocation agent."""

from __future__ import annotations

MODEL_TIERS = {
    "small": ["routing", "summarization"],
    "medium": ["validation"],
    "large": ["reasoning"],
}


def _task_type(state: dict) -> str:
    explicit = str(state.get("task_type") or "").lower()
    if explicit:
        return explicit
    route = str(state.get("route") or "").lower()
    if route:
        return "routing"
    if state.get("validation") is not None:
        return "validation"
    if state.get("merged_context") or state.get("compressed_context"):
        return "reasoning"
    return "summarization"


def _tier_for_task(task_type: str) -> str:
    for tier, tasks in MODEL_TIERS.items():
        if task_type in tasks:
            return tier
    return "small"


def run(state: dict) -> dict:
    task_type = _task_type(state)
    tier = _tier_for_task(task_type)
    allocation = {
        "task_type": task_type,
        "model_tier": tier,
        "reason": f"Use {tier} model for {task_type}.",
        "policy": {
            "small": "routing and summarization",
            "medium": "validation",
            "large": "reasoning",
        },
    }
    return {**state, "resource_allocation": allocation}
