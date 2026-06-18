"""Local in-memory goal manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class Goal:
    id: str
    objective: str
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)


_GOALS: dict[str, Goal] = {}


def create_goal(objective: str, metadata: dict[str, Any] | None = None) -> Goal:
    """Create a local goal record."""
    if not str(objective).strip():
        raise ValueError("objective is required")
    goal = Goal(id=str(uuid4()), objective=objective, metadata=metadata or {})
    _GOALS[goal.id] = goal
    return goal


def get_goal(goal_id: str) -> Goal | None:
    """Return a goal by id."""
    return _GOALS.get(goal_id)


def update_goal_status(goal_id: str, status: str) -> Goal:
    """Update goal status locally."""
    existing = _GOALS[goal_id]
    updated = Goal(id=existing.id, objective=existing.objective, status=status, metadata=existing.metadata)
    _GOALS[goal_id] = updated
    return updated


def list_goals() -> list[Goal]:
    """List local goals."""
    return list(_GOALS.values())


def clear_goals() -> None:
    """Clear local goal state. Intended for tests."""
    _GOALS.clear()
