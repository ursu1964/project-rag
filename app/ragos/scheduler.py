"""Local in-memory scheduler for lightweight RAG OS tasks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ScheduledTask:
    id: str
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    status: str = "pending"


_TASKS: list[ScheduledTask] = []


def schedule_task(name: str, payload: dict[str, Any] | None = None, priority: int = 100) -> ScheduledTask:
    """Schedule a local in-memory task without distributed queues."""
    task = ScheduledTask(id=str(uuid4()), name=name, payload=payload or {}, priority=int(priority))
    _TASKS.append(task)
    _TASKS.sort(key=lambda item: item.priority)
    return task


def next_task() -> ScheduledTask | None:
    """Return the next pending task by priority."""
    return next((task for task in _TASKS if task.status == "pending"), None)


def list_tasks() -> list[ScheduledTask]:
    """List scheduled local tasks."""
    return list(_TASKS)


def clear_tasks() -> None:
    """Clear local scheduler state. Intended for tests."""
    _TASKS.clear()
