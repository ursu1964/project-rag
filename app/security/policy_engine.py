"""Simple RBAC policy decision helper."""

from __future__ import annotations

from typing import Any

from app.security.identity import Identity, get_local_identity
from app.security.rbac import has_permission


def evaluate_permission(
    permission: str,
    identity: Identity | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actor = identity or get_local_identity()
    allowed = has_permission(actor.role, permission)
    return {
        "allowed": allowed,
        "permission": permission,
        "subject": actor.subject,
        "role": actor.role,
        "tenant_id": actor.tenant_id,
        "context": context or {},
        "reason": "allowed" if allowed else "insufficient_role_permission",
    }
