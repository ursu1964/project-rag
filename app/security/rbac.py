"""Role-based access control definitions for local development."""

from __future__ import annotations

from fastapi import HTTPException, Request

ROLES = {"admin", "operator", "analyst", "viewer", "agent"}
PERMISSIONS = {"admin", "read", "query", "ingest", "approve", "execute_disabled"}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"admin", "read", "query", "ingest", "approve", "execute_disabled"},
    "operator": {"read", "query", "ingest", "approve", "execute_disabled"},
    "analyst": {"read", "query", "execute_disabled"},
    "viewer": {"read", "execute_disabled"},
    "agent": {"read", "query", "execute_disabled"},
}


def permissions_for_role(role: str) -> set[str]:
    """Return permissions for a role."""
    normalized = str(role or "").lower()
    if normalized not in ROLES:
        return set()
    return set(ROLE_PERMISSIONS[normalized])


def has_permission(role: str, permission: str) -> bool:
    """Return whether a role has a permission."""
    normalized_permission = str(permission or "").lower()
    if normalized_permission not in PERMISSIONS:
        return False
    return normalized_permission in permissions_for_role(role)


def permission_dependency(permission: str):
    """Return a FastAPI dependency that enforces a permission using request.state.identity.

    The gateway middleware is the primary enforcement layer, but route-level dependencies
    provide defense in depth and fail closed if middleware is bypassed.
    """

    normalized_permission = str(permission or "").lower()

    def _dependency(request: Request) -> None:
        identity = getattr(getattr(request, "state", object()), "identity", None)
        if identity is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        if not has_permission(getattr(identity, "role", ""), normalized_permission):
            raise HTTPException(status_code=403, detail="Forbidden")

    return _dependency
