"""Workflow, agent run, and validation persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.core.metrics import observe_agent_run, observe_workflow_transition
from app.memory.postgres import execute, fetch_all, get_connection
from app.security.tenant_context import current_tenant_id


def create_workflow_run(question: str, route: str = "", tenant_id: str | None = None) -> str:
    tenant = current_tenant_id(tenant_id)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO workflow_runs (workflow_name, status, input)
                VALUES (%s, %s, %s::jsonb)
                RETURNING id
                """,
                (
                    "rag_query",
                    "running",
                    json.dumps({"question": question, "route": route, "tenant_id": tenant}),
                ),
            )
            row = cursor.fetchone()
        connection.commit()
    observe_workflow_transition("running")
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
    observe_workflow_transition(status)


def save_workflow_checkpoint(
    workflow_id: str,
    step_name: str,
    state: dict[str, Any],
    status: str = "running",
    error: str | None = None,
) -> None:
    """Persist or update a workflow checkpoint for durable resume/audit."""
    execute(
        """
        INSERT INTO workflow_checkpoints (workflow_id, step_name, state, status, error)
        VALUES (%s, %s, %s::jsonb, %s, %s)
        ON CONFLICT (workflow_id, step_name)
        DO UPDATE SET
            state = EXCLUDED.state,
            status = EXCLUDED.status,
            error = EXCLUDED.error,
            updated_at = now()
        """,
        (workflow_id, step_name, json.dumps(state), status, error),
    )


def list_workflow_checkpoints(workflow_id: str) -> list[dict[str, Any]]:
    """List checkpoints for a workflow ordered by latest update."""
    return fetch_all(
        """
        SELECT id, workflow_id, step_name, state, status, error, created_at, updated_at
        FROM workflow_checkpoints
        WHERE workflow_id = %s
        ORDER BY updated_at DESC, created_at DESC
        """,
        (workflow_id,),
    )


def latest_workflow_checkpoint(workflow_id: str) -> dict[str, Any] | None:
    """Return latest checkpoint for a workflow if present."""
    rows = fetch_all(
        """
        SELECT id, workflow_id, step_name, state, status, error, created_at, updated_at
        FROM workflow_checkpoints
        WHERE workflow_id = %s
        ORDER BY updated_at DESC, created_at DESC
        LIMIT 1
        """,
        (workflow_id,),
    )
    return rows[0] if rows else None


def store_workflow_output(workflow_id: str, output: dict[str, Any]) -> None:
    """Persist workflow output for audit/replay views."""
    execute(
        """
        UPDATE workflow_runs
        SET output = %s::jsonb, updated_at = now()
        WHERE id = %s
        """,
        (json.dumps(output), workflow_id),
    )


def store_workflow_feedback(
    workflow_id: str,
    feedback: dict[str, Any],
    tenant_id: str | None = None,
) -> dict[str, Any] | None:
    """Attach user feedback to workflow output and trend storage."""
    workflow = (
        get_workflow_run(workflow_id)
        if tenant_id is None
        else get_workflow_run(workflow_id, tenant_id=tenant_id)
    )
    if workflow is None:
        return None

    output = workflow.get("output") if isinstance(workflow.get("output"), dict) else {}
    updated_feedback = {
        "rating": int(feedback.get("rating", 0)),
        "helpful": feedback.get("helpful"),
        "comment": str(feedback.get("comment") or ""),
    }
    provenance = output.get("provenance") if isinstance(output.get("provenance"), dict) else {}
    provenance["user_feedback"] = updated_feedback
    output["provenance"] = provenance
    output["user_feedback"] = updated_feedback
    store_workflow_output(workflow_id, output)

    input_payload = workflow.get("input") if isinstance(workflow.get("input"), dict) else {}
    execute(
        """
        INSERT INTO evaluation_results (dataset_name, question, answer, metrics)
        VALUES (%s, %s, %s, %s::jsonb)
        """,
        (
            "user_feedback",
            str(input_payload.get("question") or output.get("question") or ""),
            str(output.get("answer") or ""),
            json.dumps({"workflow_id": workflow_id, **updated_feedback}),
        ),
    )
    return updated_feedback


def log_agent_run(
    workflow_id: str,
    agent_name: str,
    status: str,
    latency_ms: int = 0,
    input_summary: str = "",
    output_summary: str = "",
    tenant_id: str | None = None,
) -> None:
    tenant = current_tenant_id(tenant_id)
    execute(
        """
        INSERT INTO agent_runs (workflow_id, agent_name, status, input, output)
        VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
        """,
        (
            workflow_id,
            agent_name,
            status,
            json.dumps({"summary": input_summary, "latency_ms": latency_ms, "tenant_id": tenant}),
            json.dumps({"summary": output_summary}),
        ),
    )
    observe_agent_run(agent_name=agent_name, status=status, latency_ms=latency_ms)


def store_validation_result(
    workflow_id: str,
    validation: dict[str, Any],
    tenant_id: str | None = None,
) -> None:
    tenant = current_tenant_id(tenant_id)
    execute(
        """
        INSERT INTO validation_results (workflow_id, validator_name, passed, details)
        VALUES (%s, %s, %s, %s::jsonb)
        """,
        (
            workflow_id,
            "validator",
            bool(validation.get("grounded")),
            json.dumps({**validation, "tenant_id": tenant}),
        ),
    )


def list_workflow_runs(limit: int = 100, tenant_id: str | None = None) -> list[dict[str, Any]]:
    """List recent workflow runs."""
    return fetch_all(
        """
        SELECT id, workflow_name, status, input, output, error, created_at, updated_at
        FROM workflow_runs
        WHERE COALESCE(input->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (current_tenant_id(tenant_id), limit),
    )


def get_workflow_run(workflow_id: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    """Return a workflow run with related agent and validation records."""
    tenant = current_tenant_id(tenant_id)
    rows = fetch_all(
        """
        SELECT id, workflow_name, status, input, output, error, created_at, updated_at
        FROM workflow_runs
        WHERE id = %s
          AND COALESCE(input->>'tenant_id', 'local') = %s
        LIMIT 1
        """,
        (workflow_id, tenant),
    )
    if not rows:
        return None
    workflow = rows[0]
    workflow["agent_runs"] = list_agent_runs(workflow_id=workflow_id, limit=500, tenant_id=tenant)
    workflow["validation_results"] = list_validation_results(
        workflow_id=workflow_id,
        limit=500,
        tenant_id=tenant,
    )
    return workflow


def list_agent_runs(
    workflow_id: str | None = None,
    limit: int = 100,
    tenant_id: str | None = None,
) -> list[dict[str, Any]]:
    """List recent agent runs."""
    tenant = current_tenant_id(tenant_id)
    if workflow_id:
        return fetch_all(
            """
            SELECT ar.id, ar.workflow_id, ar.agent_name, ar.status,
                   ar.input, ar.output, ar.error, ar.created_at, ar.updated_at
            FROM agent_runs ar
            JOIN workflow_runs wr ON wr.id = ar.workflow_id
            WHERE ar.workflow_id = %s
              AND COALESCE(wr.input->>'tenant_id', 'local') = %s
                        ORDER BY ar.created_at DESC
            LIMIT %s
            """,
            (workflow_id, tenant, limit),
        )
    return fetch_all(
        """
        SELECT id, workflow_id, agent_name, status, input, output, error, created_at, updated_at
        FROM agent_runs
        WHERE COALESCE(input->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (tenant, limit),
    )


def list_validation_results(
    workflow_id: str | None = None,
    limit: int = 100,
    tenant_id: str | None = None,
) -> list[dict[str, Any]]:
    """List recent validation results."""
    tenant = current_tenant_id(tenant_id)
    if workflow_id:
        return fetch_all(
            """
            SELECT vr.id, vr.workflow_id, vr.agent_run_id,
                   vr.validator_name, vr.passed, vr.details, vr.created_at
            FROM validation_results vr
            JOIN workflow_runs wr ON wr.id = vr.workflow_id
            WHERE vr.workflow_id = %s
              AND COALESCE(wr.input->>'tenant_id', 'local') = %s
            ORDER BY vr.created_at DESC
            LIMIT %s
            """,
            (workflow_id, tenant, limit),
        )
    return fetch_all(
        """
        SELECT id, workflow_id, agent_run_id, validator_name, passed, details, created_at
        FROM validation_results
        WHERE COALESCE(details->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (tenant, limit),
    )
