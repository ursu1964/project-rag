"""Workflow, checkpoint, and validation persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, fetch_all, get_connection


def create_workflow_run(question: str, route: str = "") -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO workflow_runs (workflow_name, status, input)
                VALUES (%s, %s, %s::jsonb)
                RETURNING id
                """,
                ("rag_query", "running", json.dumps({"question": question, "route": route})),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def complete_workflow_run(workflow_id: str, status: str = "completed") -> None:
    execute("UPDATE workflow_runs SET status = %s, updated_at = now() WHERE id = %s", (status, workflow_id))


def store_workflow_output(workflow_id: str, output: dict[str, Any]) -> None:
    execute("UPDATE workflow_runs SET output = %s::jsonb, updated_at = now() WHERE id = %s", (json.dumps(output), workflow_id))


def store_validation_result(workflow_id: str, validation: dict[str, Any]) -> None:
    execute(
        """
        INSERT INTO validation_results (workflow_id, validator_name, passed, details)
        VALUES (%s, %s, %s, %s::jsonb)
        """,
        (workflow_id, "validator", bool(validation.get("grounded")), json.dumps(validation)),
    )


def get_workflow_run(workflow_id: str) -> dict[str, Any] | None:
    rows = fetch_all(
        "SELECT id, workflow_name, status, input, output, error, created_at, updated_at FROM workflow_runs WHERE id = %s LIMIT 1",
        (workflow_id,),
    )
    return rows[0] if rows else None


def list_workflow_runs(limit: int = 100) -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT id, workflow_name, status, input, output, error, created_at, updated_at FROM workflow_runs ORDER BY created_at DESC LIMIT %s",
        (int(limit),),
    )


def list_agent_runs(workflow_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    if workflow_id:
        return fetch_all("SELECT * FROM agent_runs WHERE workflow_id = %s ORDER BY created_at DESC LIMIT %s", (workflow_id, int(limit)))
    return fetch_all("SELECT * FROM agent_runs ORDER BY created_at DESC LIMIT %s", (int(limit),))


def list_validation_results(workflow_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    if workflow_id:
        return fetch_all("SELECT * FROM validation_results WHERE workflow_id = %s ORDER BY created_at DESC LIMIT %s", (workflow_id, int(limit)))
    return fetch_all("SELECT * FROM validation_results ORDER BY created_at DESC LIMIT %s", (int(limit),))


def save_workflow_checkpoint(workflow_id: str, step_name: str, state: dict[str, Any], status: str = "running", error: str | None = None) -> None:
    execute(
        """
        INSERT INTO workflow_checkpoints (workflow_id, step_name, state, status, error)
        VALUES (%s, %s, %s::jsonb, %s, %s)
        """,
        (workflow_id, step_name, json.dumps(state, default=str), status, error),
    )


def list_workflow_checkpoints(workflow_id: str) -> list[dict[str, Any]]:
    return fetch_all("SELECT * FROM workflow_checkpoints WHERE workflow_id = %s ORDER BY created_at DESC", (workflow_id,))


def latest_workflow_checkpoint(workflow_id: str) -> dict[str, Any] | None:
    rows = fetch_all("SELECT * FROM workflow_checkpoints WHERE workflow_id = %s ORDER BY created_at DESC LIMIT 1", (workflow_id,))
    return rows[0] if rows else None


def store_workflow_feedback(workflow_id: str, feedback: dict[str, Any]) -> dict[str, Any] | None:
    workflow = get_workflow_run(workflow_id)
    if workflow is None:
        return None
    output = workflow.get("output") if isinstance(workflow.get("output"), dict) else {}
    cleaned = {"rating": int(feedback.get("rating", 0)), "helpful": feedback.get("helpful"), "comment": str(feedback.get("comment") or "")}
    provenance = output.get("provenance") if isinstance(output.get("provenance"), dict) else {}
    provenance["user_feedback"] = cleaned
    output["provenance"] = provenance
    output["user_feedback"] = cleaned
    store_workflow_output(workflow_id, output)
    return cleaned
