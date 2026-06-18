"""Role-based access control definitions for local development."""

from __future__ import annotations

ROLES = {"admin", "operator", "analyst", "viewer", "agent"}
PERMISSIONS = {"read", "query", "ingest", "approve", "execute_disabled"}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"read", "query", "ingest", "approve", "execute_disabled"},
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
