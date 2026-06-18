"""Local worker for safe registered agent tasks."""

from __future__ import annotations

from time import perf_counter
from typing import Any, Callable

from app.cluster.task_queue import claim_next_task, complete_task, fail_task

_SAFE_AGENTS: dict[str, Callable[[dict], dict]] = {}


def register_safe_agent(agent_name: str, callable: Callable[[dict], dict]) -> None:
    """Register an agent callable that the local worker is allowed to execute."""
    if not agent_name.strip():
        raise ValueError("agent_name is required")
    if not callable:
        raise ValueError("callable is required")
    _SAFE_AGENTS[agent_name] = callable


def list_safe_agents() -> list[str]:
    """List agent names allowed for worker execution."""
    return sorted(_SAFE_AGENTS)


def clear_safe_agents() -> None:
    """Clear registered safe agents. Intended for tests."""
    _SAFE_AGENTS.clear()


def execute_task(task: dict[str, Any]) -> dict[str, Any]:
    """Execute one claimed task only if its agent is registered as safe."""
    agent_name = str(task.get("agent_name") or "")
    agent = _SAFE_AGENTS.get(agent_name)
    start = perf_counter()
    if agent is None:
        error = f"unregistered or unsafe agent: {agent_name}"
        result_id = fail_task(task, error=error, latency_ms=0)
        return {"executed": False, "status": "failed", "error": error, "result_id": result_id}

    try:
        input_state = task.get("input") if isinstance(task.get("input"), dict) else {}
        output = agent(input_state)
        latency_ms = int((perf_counter() - start) * 1000)
        result_id = complete_task(task, output=output, latency_ms=latency_ms)
        return {"executed": True, "status": "completed", "output": output, "result_id": result_id}
    except Exception as exc:  # pragma: no cover - agent failures vary
        latency_ms = int((perf_counter() - start) * 1000)
        result_id = fail_task(task, error=str(exc), latency_ms=latency_ms)
        return {"executed": False, "status": "failed", "error": str(exc), "result_id": result_id}


def run_once(agent_name: str | None = None) -> dict[str, Any]:
    """Claim and execute one local task."""
    task = claim_next_task(agent_name=agent_name)
    if task is None:
        return {"status": "idle", "executed": False}
    return execute_task(task)
