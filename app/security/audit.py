"""Security audit event logging."""

from __future__ import annotations

import json
from typing import Any

from app.core.logging import get_logger
from app.memory.postgres import execute, fetch_all
from app.security.identity import Identity, get_local_identity
from app.security.tenant_context import current_tenant_id

logger = get_logger(__name__)


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
    try:
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
    except Exception as exc:  # pragma: no cover - depends on external DB state
        # Security audit should never block core API flows in local/dev/test mode.
        logger.warning(
            "security_audit_write_failed action=%s resource=%s reason=%s",
            action,
            resource,
            exc.__class__.__name__,
        )
    return event


def list_security_events(limit: int = 100, tenant_id: str | None = None) -> list[dict[str, Any]]:
    """List recent security audit events."""
    tenant = current_tenant_id(tenant_id)
    try:
        return fetch_all(
            """
            SELECT id, "user", role, action, resource, decision, risk_level, metadata, timestamp
            FROM security_audit_events
            WHERE COALESCE(metadata->>'tenant_id', 'local') = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (tenant, int(limit)),
        )
    except Exception as exc:  # pragma: no cover - depends on external DB state
        logger.warning("security_audit_read_failed reason=%s", exc.__class__.__name__)
        return []
