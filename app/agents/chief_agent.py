"""Chief agent for high-level cognitive orchestration."""

from __future__ import annotations


def _split_objective(objective: str) -> list[str]:
    parts = [part.strip(" .") for part in objective.replace(";", ".").split(".")]
    return [part for part in parts if part] or [objective]


def run(state: dict) -> dict:
    objective = str(state.get("objective") or state.get("question") or "")
    tasks = _split_objective(objective)
    needed_agents = ["memory", "retrieval", "graph", "planning", "security", "cost", "validation", "learning"]

    chief_summary = {
        "objective": objective,
        "tasks": tasks,
        "needed_agents": needed_agents,
        "results": {
            key: state.get(key)
            for key in ("memory_context", "vector_context", "graph_context", "plan", "security", "cost", "validation", "lessons_learned")
            if key in state
        },
    }
    return {**state, "objective": objective, "question": state.get("question") or objective, "tasks": tasks, "needed_agents": needed_agents, "chief_summary": chief_summary}
