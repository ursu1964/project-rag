"""Local PostgreSQL-backed scheduler facade."""

from __future__ import annotations

from typing import Any

from app.cluster.task_queue import enqueue_task, list_tasks


def schedule_agent_task(
    agent_name: str,
    task_type: str,
    input: dict[str, Any] | None = None,
    workflow_id: str | None = None,
    priority: int = 100,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Schedule a safe registered agent task for local worker pickup."""
    task_id = enqueue_task(
        agent_name=agent_name,
        task_type=task_type,
        input=input,
        workflow_id=workflow_id,
        priority=priority,
        metadata=metadata,
    )
    return {"task_id": task_id, "status": "pending", "agent_name": agent_name, "task_type": task_type}


def scheduled_tasks(status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """List scheduled tasks."""
    return list_tasks(status=status, limit=limit)
