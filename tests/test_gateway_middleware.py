from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.config import settings
from app.gateway import middleware


def _request(path: str = "/documents", headers: dict[str, str] | None = None):
    return SimpleNamespace(
        headers=headers or {},
        client=SimpleNamespace(host="127.0.0.1"),
        url=SimpleNamespace(path=path),
    )


def test_gateway_public_paths():
    assert middleware._is_public_path("/health") is True
    assert middleware._is_public_path("/metrics") is True
    assert middleware._is_public_path("/documents") is False


def test_gateway_extracts_api_key_from_custom_header():
    request = _request(headers={"x-projectrag-api-key": "secret"})

    assert middleware._extract_api_key(request) == "secret"


def test_gateway_extracts_api_key_from_bearer_header():
    request = _request(headers={"authorization": "Bearer secret"})

    assert middleware._extract_api_key(request) == "secret"


def test_gateway_uses_safe_caller_request_id():
    request = _request(headers={"x-request-id": "trace-123"})

    assert middleware._request_id(request) == "trace-123"


def test_gateway_generates_request_id_for_unsafe_value():
    request = _request(headers={"x-request-id": "bad value with spaces"})

    request_id = middleware._request_id(request)

    assert request_id != "bad value with spaces"
    assert len(request_id) == 36


def test_gateway_rate_limit_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    middleware._REQUEST_TIMESTAMPS.clear()

    assert middleware._rate_limit_exceeded(_request(), 1000.0) is False


def test_gateway_rate_limit_blocks_after_limit(monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_per_minute", 1)
    middleware._REQUEST_TIMESTAMPS.clear()
    request = _request()

    assert middleware._rate_limit_exceeded(request, 1000.0) is False
    assert middleware._rate_limit_exceeded(request, 1001.0) is True


def test_gateway_required_permission_map():
    assert middleware._required_permission("GET", "/documents") == "read"
    assert middleware._required_permission("POST", "/query") == "query"
    assert middleware._required_permission("DELETE", "/documents/doc-1") == "ingest"
    assert middleware._required_permission("GET", "/health") is None


def test_gateway_rbac_decision_allows_admin(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "admin")
    request = _request(path="/query")
    request.method = "POST"

    decision = middleware._rbac_decision(request)

    assert decision is not None
    assert decision["allowed"] is True
    assert decision["permission"] == "query"


def test_gateway_rbac_decision_denies_viewer_query(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "viewer")
    request = _request(path="/query")
    request.method = "POST"

    decision = middleware._rbac_decision(request)

    assert decision is not None
    assert decision["allowed"] is False
    assert decision["permission"] == "query"


def test_gateway_rbac_uses_request_state_identity():
    request = _request(path="/query")
    request.method = "POST"
    request.state = SimpleNamespace(
        identity=SimpleNamespace(subject="user-1", role="viewer", tenant_id="tenant-a"),
        tenant_id="tenant-a",
    )

    decision = middleware._rbac_decision(request)

    assert decision is not None
    assert decision["allowed"] is False
    assert decision["tenant_id"] == "tenant-a"


def test_gateway_rate_limit_uses_redis_counter(monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_per_minute", 2)
    counts = iter([1, 3])
    monkeypatch.setattr(middleware, "increment_window_counter", lambda key, ttl_seconds: next(counts))
    request = _request()

    assert middleware._rate_limit_exceeded(request, 1000.0) is False
    assert middleware._rate_limit_exceeded(request, 1001.0) is True


def test_gateway_permission_map_includes_platform_routes():
    assert middleware._required_permission("POST", "/embeddings") == "query"
    assert middleware._required_permission("POST", "/retrieval/vector") == "query"
    assert middleware._required_permission("GET", "/connectors") == "read"
    assert middleware._required_permission("GET", "/audit/events") == "read"


def _build_gateway_test_client() -> TestClient:
    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/documents/ping")
    async def documents_ping(request: Request):
        return {
            "ok": True,
            "tenant_id": getattr(request.state, "tenant_id", None),
        }

    return TestClient(app)


def test_gateway_auth_required_oidc_denies_without_identity(monkeypatch):
    monkeypatch.setattr(settings, "auth_required", True)
    monkeypatch.setattr(settings, "auth_mode", "oidc")
    monkeypatch.setattr(settings, "oidc_issuer", "https://issuer.example.com")
    monkeypatch.setattr(settings, "oidc_audience", "projectrag-api")
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "enforce_rbac", False)
    recorded = []
    monkeypatch.setattr(middleware, "record_security_event", lambda **kwargs: recorded.append(kwargs) or kwargs)

    client = _build_gateway_test_client()
    response = client.get("/documents/ping")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
    assert recorded[0]["action"] == "gateway_auth"
    assert recorded[0]["decision"] == "deny"
    assert recorded[0]["risk_level"] == "high"


def test_gateway_local_mode_allows_trusted_header_and_sets_tenant(monkeypatch):
    monkeypatch.setattr(settings, "auth_required", True)
    monkeypatch.setattr(settings, "auth_mode", "local")
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "enforce_rbac", False)

    client = _build_gateway_test_client()
    response = client.get(
        "/documents/ping",
        headers={
            "x-projectrag-user": "alice",
            "x-projectrag-role": "analyst",
            "x-projectrag-tenant-id": "tenant-77",
        },
    )

    assert response.status_code == 200
    assert response.json()["tenant_id"] == "tenant-77"
    assert response.headers["x-tenant-id"] == "tenant-77"
