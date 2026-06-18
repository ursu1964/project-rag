"""PostgreSQL-backed local task queue for cluster agent tasks."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import fetch_all, get_connection

PENDING = "pending"
RUNNING = "running"
COMPLETED = "completed"
FAILED = "failed"
RETRY = "retry"
TASK_STATES = {PENDING, RUNNING, COMPLETED, FAILED, RETRY}


def _validate_status(status: str) -> str:
    normalized = str(status).lower()
    if normalized not in TASK_STATES:
        raise ValueError(f"Unsupported task status: {status}")
    return normalized


def enqueue_task(
    agent_name: str,
    task_type: str,
    input: dict[str, Any] | None = None,
    workflow_id: str | None = None,
    priority: int = 100,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Enqueue a local agent task."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agent_tasks (
                    workflow_id, agent_name, task_type, priority, status, input, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                RETURNING id
                """,
                (
                    workflow_id,
                    agent_name,
                    task_type,
                    int(priority),
                    PENDING,
                    json.dumps(input or {}),
                    json.dumps(metadata or {}),
                ),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def claim_next_task(agent_name: str | None = None) -> dict[str, Any] | None:
    """Claim the next pending/retry task and mark it running."""
    params: list[Any] = []
    agent_filter = ""
    if agent_name:
        agent_filter = "AND agent_name = %s"
        params.append(agent_name)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT id
                FROM agent_tasks
                WHERE status IN (%s, %s)
                {agent_filter}
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
                """,
                [PENDING, RETRY, *params],
            )
            row = cursor.fetchone()
            if row is None:
                connection.commit()
                return None

            cursor.execute(
                """
                UPDATE agent_tasks
                SET status = %s, updated_at = now()
                WHERE id = %s
                RETURNING id, workflow_id, agent_name, task_type, priority, status,
                          input, metadata, created_at, updated_at
                """,
                (RUNNING, row["id"]),
            )
            task = cursor.fetchone()
        connection.commit()
    return dict(task) if task else None


def update_task_status(task_id: str, status: str) -> None:
    """Update task status."""
    normalized = _validate_status(status)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE agent_tasks
                SET status = %s, updated_at = now()
                WHERE id = %s
                """,
                (normalized, task_id),
            )
        connection.commit()


def store_task_result(
    task: dict[str, Any],
    output: dict[str, Any] | None = None,
    status: str = COMPLETED,
    error: str | None = None,
    latency_ms: int = 0,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Store task execution result."""
    normalized = _validate_status(status)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agent_results (
                    task_id, workflow_id, agent_name, status, output, error, latency_ms, metadata
                )
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb)
                RETURNING id
                """,
                (
                    task.get("id"),
                    task.get("workflow_id"),
                    task.get("agent_name"),
                    normalized,
                    json.dumps(output or {}),
                    error,
                    int(latency_ms),
                    json.dumps(metadata or {}),
                ),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def complete_task(task: dict[str, Any], output: dict[str, Any] | None = None, latency_ms: int = 0) -> str:
    """Mark task completed and store result."""
    result_id = store_task_result(task, output=output, status=COMPLETED, latency_ms=latency_ms)
    update_task_status(str(task["id"]), COMPLETED)
    return result_id


def fail_task(task: dict[str, Any], error: str, latency_ms: int = 0) -> str:
    """Mark task failed and store error."""
    result_id = store_task_result(task, output={}, status=FAILED, error=error, latency_ms=latency_ms)
    update_task_status(str(task["id"]), FAILED)
    return result_id


def retry_task(task_id: str) -> None:
    """Move task to retry state."""
    update_task_status(task_id, RETRY)


def list_tasks(status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """List recent tasks."""
    if status:
        return fetch_all(
            """
            SELECT id, workflow_id, agent_name, task_type, priority, status,
                   input, metadata, created_at, updated_at
            FROM agent_tasks
            WHERE status = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (_validate_status(status), int(limit)),
        )
    return fetch_all(
        """
        SELECT id, workflow_id, agent_name, task_type, priority, status,
               input, metadata, created_at, updated_at
        FROM agent_tasks
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (int(limit),),
    )
