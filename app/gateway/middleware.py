"""Local API gateway middleware.

This module intentionally keeps gateway controls dependency-free for the local MVP:
- API key authentication is optional and disabled unless PROJECTRAG_API_KEY is set.
- Rate limiting is optional and disabled unless PROJECTRAG_RATE_LIMIT_PER_MINUTE > 0.
- Request audit is logger-based so it does not make API availability depend on the database.
"""

from __future__ import annotations

import json
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.core.correlation import reset_request_id, set_request_id
from app.core.logging import get_logger
from app.core.metrics import observe_http_request
from app.services.cache import increment_window_counter
from app.security.api_key_manager import compare_tokens_timing_safe, verify_api_key
from app.security.audit import record_security_event
from app.security.identity import IdentityResolutionError, resolve_request_identity
from app.security.policy_engine import evaluate_permission
from app.security.tenant_context import reset_request_tenant, set_request_tenant

logger = get_logger(__name__)

_PUBLIC_PATHS = {
    "/",
    "/health",
    "/health/live",
    "/health/deep",
    "/health/ready",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
}
_PROBE_PUBLIC_PATHS = {
    "/",
    "/health",
    "/health/live",
    "/health/deep",
    "/health/ready",
}
_REQUEST_TIMESTAMPS: dict[str, deque[float]] = defaultdict(deque)
_REQUEST_ID_HEADER = "x-request-id"
_TENANT_ID_HEADER = "x-tenant-id"
_VERSION_PREFIX = "/api/v1"

_PERMISSION_BY_PREFIX: tuple[tuple[str, str, str], ...] = (
    ("GET", "/audit/events", "admin"),
    ("GET", "/operations/jobs/retry-queue", "admin"),
    ("POST", "/workflows/", "admin"),
    ("GET", "/documents", "read"),
    ("GET", "/documents/", "read"),
    ("POST", "/documents/upload", "ingest"),
    ("POST", "/documents/", "ingest"),
    ("DELETE", "/documents/", "ingest"),
    ("POST", "/ingest", "ingest"),
    ("POST", "/devops/inventory/import", "ingest"),
    ("GET", "/connectors", "read"),
    ("GET", "/connectors/", "read"),
    ("POST", "/connectors/", "ingest"),
    ("GET", "/memory", "read"),
    ("GET", "/memory/", "read"),
    ("POST", "/memory", "ingest"),
    ("POST", "/memory/", "ingest"),
    ("POST", "/query", "query"),
    ("POST", "/embeddings", "query"),
    ("POST", "/retrieval", "query"),
    ("POST", "/graph/query", "query"),
    ("GET", "/graph/export", "read"),
    ("POST", "/cognitive/query", "query"),
    ("GET", "/workflows", "read"),
    ("GET", "/workflows/", "read"),
    ("GET", "/agents/runs", "read"),
    ("GET", "/validation/results", "read"),
    ("GET", "/evaluation/report", "read"),
    ("GET", "/sources/catalog", "read"),
    ("GET", "/embeddings/models", "read"),
    ("POST", "/feedback/", "query"),
)


def _strip_version_prefix(path: str) -> str:
    """Normalize versioned routes so gateway policy stays identical."""
    if path == _VERSION_PREFIX:
        return "/"
    if path.startswith(f"{_VERSION_PREFIX}/"):
        return path[len(_VERSION_PREFIX) :] or "/"
    return path


def _is_public_path(path: str) -> bool:
    normalized_path = _strip_version_prefix(path)
    app_env = str(getattr(settings, "app_env", "local") or "local").lower()
    public_paths = _PUBLIC_PATHS if app_env == "local" else _PROBE_PUBLIC_PATHS
    return normalized_path in public_paths or (
        app_env == "local" and normalized_path.startswith("/docs/")
    )


def _extract_api_key(request: Request) -> str:
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return request.headers.get("x-projectrag-api-key", "").strip()


def _request_id(request: Request) -> str:
    """Return caller-provided request id or generate a safe trace id."""
    provided = str(request.headers.get(_REQUEST_ID_HEADER, "")).strip()
    if (
        provided
        and len(provided) <= 128
        and all(char.isalnum() or char in "-_." for char in provided)
    ):
        return provided
    return str(uuid.uuid4())


def _required_permission(method: str, path: str) -> str | None:
    normalized_method = method.upper()
    normalized_path = _strip_version_prefix(path)
    for route_method, prefix, permission in _PERMISSION_BY_PREFIX:
        if normalized_method == route_method and normalized_path.startswith(prefix):
            return permission
    return None


def _rbac_decision(request: Request) -> dict | None:
    permission = _required_permission(request.method, request.url.path)
    if permission is None:
        return None
    identity = getattr(getattr(request, "state", object()), "identity", None)
    tenant_id = getattr(getattr(request, "state", object()), "tenant_id", None)
    return evaluate_permission(
        permission,
        identity=identity,
        context={
            "method": request.method,
            "path": request.url.path,
            "tenant_id": tenant_id,
        },
    )


def _client_key(request: Request) -> str:
    host = request.client.host if request.client else "unknown"
    return f"{host}:{request.url.path}"


def _rate_limit_exceeded(request: Request, now: float) -> bool:
    # Check per-endpoint limit first (method may not exist in test mocks)
    method = getattr(request, "method", "GET")
    path = getattr(request.url, "path", "/")
    method_path = f"{method} {path}"
    try:
        per_endpoint = json.loads(settings.rate_limit_per_endpoint or "{}")
        endpoint_limit = per_endpoint.get(method_path)
        if endpoint_limit is not None and endpoint_limit > 0:
            limit = int(endpoint_limit)
        else:
            limit = int(settings.rate_limit_per_minute or 0)
    except (json.JSONDecodeError, TypeError, ValueError):
        limit = int(settings.rate_limit_per_minute or 0)
    if limit <= 0:
        return False

    window = int(now // 60)
    redis_key = f"ratelimit:{_client_key(request)}:{window}"
    count = increment_window_counter(redis_key, ttl_seconds=70)
    if count is not None:
        return count > limit

    window_start = now - 60.0
    timestamps = _REQUEST_TIMESTAMPS[_client_key(request)]
    while timestamps and timestamps[0] < window_start:
        timestamps.popleft()
    if len(timestamps) >= limit:
        return True
    timestamps.append(now)
    return False


def _audit_denial(
    request: Request, action: str, resource: str, reason: str, risk_level: str
) -> None:
    record_security_event(
        action=action,
        resource=resource,
        decision="deny",
        risk_level=risk_level,
        identity=getattr(getattr(request, "state", object()), "identity", None),
        metadata={
            "method": request.method,
            "path": request.url.path,
            "reason": reason,
            "tenant_id": getattr(
                getattr(request, "state", object()), "tenant_id", None
            ),
            "request_id": getattr(
                getattr(request, "state", object()), "request_id", None
            ),
        },
    )


def _verify_configured_api_key(provided_key: str) -> bool:
    """Verify API key against configured key (bcrypt hash or plaintext for backward compat).

    Uses timing-safe comparison to prevent timing attacks.
    Prefers bcrypt hash if available; falls back to plaintext comparison.

    Args:
        provided_key: The API key provided in the request

    Returns:
        True if key is valid, False otherwise
    """
    if not provided_key:
        return False

    # Try bcrypt hash first (preferred)
    configured_hash = str(settings.api_key_hash or "").strip()
    if configured_hash:
        try:
            return verify_api_key(provided_key, configured_hash)
        except Exception as exc:
            logger.warning(
                "api_key_hash verification failed: %s", exc.__class__.__name__
            )
            return False

    # Fall back to plaintext comparison (deprecated, only for backward compat)
    configured_plaintext = str(settings.api_key or "").strip()
    if configured_plaintext:
        # Use timing-safe comparison to prevent timing attacks
        return compare_tokens_timing_safe(provided_key, configured_plaintext)

    # No API key configured
    return False


def install_gateway_middleware(app: FastAPI) -> None:
    """Install optional local gateway controls on a FastAPI app."""

    @app.middleware("http")
    async def projectrag_gateway(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = time.perf_counter()
        path = request.url.path
        request_id = _request_id(request)
        request.state.request_id = request_id
        request_id_token = set_request_id(request_id)

        try:
            # Public paths (health probes, metrics, docs) must never require auth
            # so that load-balancers and Prometheus can reach them unconditionally.
            is_public = _is_public_path(path)
            auth_mode = str(getattr(settings, "auth_mode", "local") or "local").lower()
            app_env = str(getattr(settings, "app_env", "local") or "local").lower()
            trusted_headers_allowed = app_env == "local" and auth_mode == "local"
            configured_api_key = str(settings.api_key or "").strip()
            configured_api_key_hash = str(settings.api_key_hash or "").strip()
            has_trusted_identity_header = bool(
                trusted_headers_allowed
                and str(request.headers.get("x-projectrag-user", "")).strip()
            )
            if (
                bool(settings.auth_required)
                and auth_mode == "local"
                and not is_public
                and not (configured_api_key or configured_api_key_hash)
                and not has_trusted_identity_header
            ):
                raise IdentityResolutionError("API key is required for local auth mode")
            identity = resolve_request_identity(
                request.headers,
                enforce_auth=bool(settings.auth_required)
                and not is_public
                and auth_mode != "local",
                auth_mode=auth_mode,
                oidc_issuer=str(getattr(settings, "oidc_issuer", "")),
                oidc_audience=str(getattr(settings, "oidc_audience", "")),
                allow_trusted_headers=trusted_headers_allowed,
            )
        except IdentityResolutionError:
            logger.warning(
                "gateway_denied request_id=%s auth_required path=%s", request_id, path
            )
            _audit_denial(
                request, "gateway_auth", path, "authentication_required", "high"
            )
            observe_http_request(
                request.method,
                path,
                401,
                (time.perf_counter() - started) * 1000,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"},
                headers={_REQUEST_ID_HEADER: request_id},
            )
        request.state.identity = identity
        request.state.tenant_id = identity.tenant_id
        tenant_token = set_request_tenant(identity.tenant_id)

        try:
            # Explicit tenant-identity cross-validation: ensure tenant from identity matches request state
            # This prevents middleware state mutation attacks
            if identity.tenant_id != request.state.tenant_id:
                logger.warning(
                    "gateway_denied request_id=%s tenant_mismatch identity_tenant=%s request_tenant=%s path=%s",
                    request_id,
                    identity.tenant_id,
                    request.state.tenant_id,
                    path,
                )
                _audit_denial(
                    request,
                    "gateway_tenant_mismatch",
                    path,
                    "tenant_identity_mismatch",
                    "high",
                )
                observe_http_request(
                    request.method, path, 403, (time.perf_counter() - started) * 1000
                )
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Forbidden"},
                    headers={_REQUEST_ID_HEADER: request_id},
                )

            if _rate_limit_exceeded(request, time.time()):
                logger.warning(
                    "gateway_denied request_id=%s rate_limited path=%s",
                    request_id,
                    path,
                )
                _audit_denial(
                    request, "gateway_rate_limit", path, "rate_limited", "medium"
                )
                observe_http_request(
                    request.method,
                    path,
                    429,
                    (time.perf_counter() - started) * 1000,
                )
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={_REQUEST_ID_HEADER: request_id},
                )

            if (configured_api_key or configured_api_key_hash) and not _is_public_path(
                path
            ):
                provided_api_key = _extract_api_key(request)
                if not _verify_configured_api_key(provided_api_key):
                    logger.warning(
                        "gateway_denied request_id=%s unauthorized path=%s",
                        request_id,
                        path,
                    )
                    _audit_denial(
                        request,
                        "gateway_api_key",
                        path,
                        "unauthorized_api_key",
                        "medium",
                    )
                    observe_http_request(
                        request.method,
                        path,
                        401,
                        (time.perf_counter() - started) * 1000,
                    )
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Unauthorized"},
                        headers={_REQUEST_ID_HEADER: request_id},
                    )

            if settings.enforce_rbac and not _is_public_path(path):
                decision = _rbac_decision(request)
                if decision is not None and not decision["allowed"]:
                    logger.warning(
                        "gateway_denied request_id=%s rbac path=%s permission=%s role=%s",
                        request_id,
                        path,
                        decision["permission"],
                        decision["role"],
                    )
                    _audit_denial(
                        request, "gateway_rbac", path, "rbac_denied", "medium"
                    )
                    observe_http_request(
                        request.method,
                        path,
                        403,
                        (time.perf_counter() - started) * 1000,
                    )
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Forbidden", "policy_decision": decision},
                        headers={_REQUEST_ID_HEADER: request_id},
                    )

            response = await call_next(request)
            duration_ms = (time.perf_counter() - started) * 1000
            observe_http_request(
                request.method, path, response.status_code, duration_ms
            )
            response.headers[_REQUEST_ID_HEADER] = request_id
            response.headers[_TENANT_ID_HEADER] = str(
                getattr(request.state, "tenant_id", "default")
            )
            if settings.request_audit_enabled:
                duration_ms_int = int(duration_ms)
                logger.info(
                    "gateway_request request_id=%s tenant_id=%s method=%s path=%s status=%s duration_ms=%s",
                    request_id,
                    getattr(request.state, "tenant_id", "default"),
                    request.method,
                    path,
                    response.status_code,
                    duration_ms_int,
                )
            return response
        finally:
            reset_request_tenant(tenant_token)
            reset_request_id(request_id_token)
