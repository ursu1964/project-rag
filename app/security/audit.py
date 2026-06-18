"""Security audit event logging."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, fetch_all
from app.security.identity import Identity, get_local_identity


def record_security_event(
    action: str,
    resource: str,
    decision: str,
    risk_level: str = "low",
    identity: Identity | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record a security audit event."""
    actor = identity or get_local_identity()
    merged_metadata = {"tenant_id": actor.tenant_id, **(metadata or {})}
    event = {
        "user": actor.subject,
        "role": actor.role,
        "action": action,
        "resource": resource,
        "decision": decision,
        "risk_level": risk_level,
        "metadata": merged_metadata,
    }
    execute(
        """
        INSERT INTO security_audit_events (
            "user", role, action, resource, decision, risk_level, metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
        """,
        (
            event["user"],
            event["role"],
            event["action"],
            event["resource"],
            event["decision"],
            event["risk_level"],
            json.dumps(event["metadata"]),
        ),
    )
    return event


def list_security_events(limit: int = 100) -> list[dict[str, Any]]:
    """List recent security audit events."""
    return fetch_all(
        """
        SELECT id, "user", role, action, resource, decision, risk_level, metadata, timestamp
        FROM security_audit_events
        ORDER BY timestamp DESC
        LIMIT %s
        """,
        (int(limit),),
    )
