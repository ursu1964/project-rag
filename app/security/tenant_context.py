"""Request-local tenant context helpers."""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Any

_TENANT_ID: ContextVar[str] = ContextVar("projectrag_tenant_id", default="local")


def set_request_tenant(tenant_id: str | None) -> Token[str]:
    tenant = str(tenant_id or "local").strip() or "local"
    return _TENANT_ID.set(tenant)


def reset_request_tenant(token: Token[str]) -> None:
    _TENANT_ID.reset(token)


def current_tenant_id(tenant_id: str | None = None) -> str:
    return str(tenant_id or _TENANT_ID.get() or "local")


def with_tenant_metadata(metadata: dict[str, Any] | None = None, tenant_id: str | None = None) -> dict[str, Any]:
    return {**(metadata or {}), "tenant_id": current_tenant_id(tenant_id)}
