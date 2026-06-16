"""Workflow, agent run, and validation persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, get_connection


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
    execute(
        """
        UPDATE workflow_runs
        SET status = %s, updated_at = now()
        WHERE id = %s
        """,
        (status, workflow_id),
    )


def log_agent_run(
    workflow_id: str,
    agent_name: str,
    status: str,
    latency_ms: int = 0,
    input_summary: str = "",
    output_summary: str = "",
) -> None:
    execute(
        """
        INSERT INTO agent_runs (workflow_id, agent_name, status, input, output)
        VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
        """,
        (
            workflow_id,
            agent_name,
            status,
            json.dumps({"summary": input_summary, "latency_ms": latency_ms}),
            json.dumps({"summary": output_summary}),
        ),
    )


def store_validation_result(workflow_id: str, validation: dict[str, Any]) -> None:
    execute(
        """
        INSERT INTO validation_results (workflow_id, validator_name, passed, details)
        VALUES (%s, %s, %s, %s::jsonb)
        """,
        (workflow_id, "validator", bool(validation.get("grounded")), json.dumps(validation)),
    )
