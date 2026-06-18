"""Experience persistence repository for future learning agents."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, fetch_all, get_connection
from app.security.tenant_context import current_tenant_id


def create_experience_run(
    goal: str,
    plan: dict[str, Any] | list[Any] | None = None,
    tenant_id: str | None = None,
) -> str:
    """Create an experience run and return its id."""
    tenant = current_tenant_id(tenant_id)
    plan_payload = dict(plan or {}) if isinstance(plan, dict) else {"items": list(plan or [])}
    plan_payload["tenant_id"] = tenant
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO experience_runs (goal, plan)
                VALUES (%s, %s::jsonb)
                RETURNING id
                """,
                (goal, json.dumps(plan_payload)),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def add_experience_step(
    experience_run_id: str,
    step_index: int,
    action: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
) -> None:
    """Store an action/result step for an experience run."""
    execute(
        """
        INSERT INTO experience_steps (experience_run_id, step_index, action, result)
        VALUES (%s, %s, %s::jsonb, %s::jsonb)
        """,
        (experience_run_id, step_index, json.dumps(action or {}), json.dumps(result or {})),
    )


def store_experience_outcome(
    experience_run_id: str,
    status: str,
    results: dict[str, Any] | None = None,
    lessons_learned: list[str] | None = None,
    tenant_id: str | None = None,
) -> None:
    """Store final outcome and lessons for an experience run."""
    tenant = current_tenant_id(tenant_id)
    execute(
        """
        INSERT INTO experience_outcomes (experience_run_id, status, results, lessons_learned)
        VALUES (%s, %s, %s::jsonb, %s::jsonb)
        """,
        (
            experience_run_id,
            status,
            json.dumps({**(results or {}), "tenant_id": tenant}),
            json.dumps(lessons_learned or []),
        ),
    )
    execute(
        """
        UPDATE experience_runs
        SET lessons_learned = %s::jsonb, updated_at = now()
        WHERE id = %s
        """,
        (json.dumps(lessons_learned or []), experience_run_id),
    )


def get_experience_run(experience_run_id: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    """Fetch an experience run by id."""
    rows = fetch_all(
        """
        SELECT id, goal, plan, lessons_learned, created_at, updated_at
        FROM experience_runs
        WHERE id = %s
          AND COALESCE(plan->>'tenant_id', 'local') = %s
        LIMIT 1
        """,
        (experience_run_id, current_tenant_id(tenant_id)),
    )
    return rows[0] if rows else None


def list_recent_experience_runs(limit: int = 20, tenant_id: str | None = None) -> list[dict[str, Any]]:
    """List recent experience runs."""
    return fetch_all(
        """
        SELECT id, goal, plan, lessons_learned, created_at, updated_at
        FROM experience_runs
        WHERE COALESCE(plan->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (current_tenant_id(tenant_id), limit),
    )
