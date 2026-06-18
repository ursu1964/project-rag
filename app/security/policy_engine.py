"""Simple local policy engine for ProjectRAG permissions."""

from __future__ import annotations

from typing import Any

from app.security.identity import Identity, get_local_identity
from app.security.rbac import has_permission


def evaluate_permission(
    permission: str,
    identity: Identity | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a permission for a local development identity."""
    actor = identity or get_local_identity()
    allowed = has_permission(actor.role, permission)
    return {
        "allowed": allowed,
        "permission": permission,
        "subject": actor.subject,
        "role": actor.role,
        "tenant_id": actor.tenant_id,
        "context": context or {},
        "reason": "permission granted by local RBAC" if allowed else "permission denied by local RBAC",
    }


def require_permission(
    permission: str,
    identity: Identity | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return policy decision; callers decide how to surface denial."""
    return evaluate_permission(permission, identity=identity, context=context)
