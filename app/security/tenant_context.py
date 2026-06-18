"""Tenant context helpers for request-scoped data isolation."""

from __future__ import annotations

import os
from contextvars import ContextVar, Token
from typing import Any

_TENANT_CONTEXT: ContextVar[str | None] = ContextVar("projectrag_tenant_id", default=None)


def set_request_tenant(tenant_id: str) -> Token:
    """Set the current request tenant id in context-local storage."""
    value = str(tenant_id or "").strip() or default_tenant_id()
    return _TENANT_CONTEXT.set(value)


def reset_request_tenant(token: Token) -> None:
    """Reset tenant context to previous value."""
    _TENANT_CONTEXT.reset(token)


def default_tenant_id() -> str:
    """Return the default tenant id for non-request contexts."""
    return str(os.getenv("PROJECTRAG_LOCAL_TENANT", "local")).strip() or "local"


def current_tenant_id(explicit_tenant_id: str | None = None) -> str:
    """Resolve tenant id with explicit override, request context, and local fallback."""
    if explicit_tenant_id is not None:
        candidate = str(explicit_tenant_id).strip()
        if candidate:
            return candidate
    contextual = _TENANT_CONTEXT.get()
    if contextual:
        return contextual
    return default_tenant_id()


def with_tenant_metadata(metadata: dict[str, Any] | None, tenant_id: str | None = None) -> dict[str, Any]:
    """Return metadata enriched with tenant id."""
    merged = dict(metadata or {})
    merged["tenant_id"] = current_tenant_id(tenant_id)
    return merged
