"""Integration tests for API key validation."""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.config import settings
from app.gateway import middleware


def test_gateway_rejects_request_with_wrong_api_key(monkeypatch):
    """Verify that requests with incorrect API keys are rejected with 401."""
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "api_key", "correct-secret-key")
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "enforce_rbac", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/api-test-endpoint")
    async def api_test_endpoint(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # Request with missing API key is rejected
    response = client.get("/api-test-endpoint")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    
    # Request with wrong API key is rejected
    response = client.get(
        "/api-test-endpoint",
        headers={"x-projectrag-api-key": "wrong-key"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_gateway_accepts_request_with_correct_api_key(monkeypatch):
    """Verify that requests with correct API keys are accepted."""
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "api_key", "correct-secret-key")
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "enforce_rbac", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/api-test-endpoint-2")
    async def api_test_endpoint_2(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # Request with correct API key (custom header) succeeds
    response = client.get(
        "/api-test-endpoint-2",
        headers={"x-projectrag-api-key": "correct-secret-key"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_gateway_accepts_bearer_token_as_api_key(monkeypatch):
    """Verify that Bearer tokens are accepted as API keys."""
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "api_key", "correct-secret-key")
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "enforce_rbac", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/api-test-endpoint-3")
    async def api_test_endpoint_3(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # Request with correct API key (Bearer token) succeeds
    response = client.get(
        "/api-test-endpoint-3",
        headers={"authorization": "Bearer correct-secret-key"}
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_gateway_allows_public_paths_without_api_key(monkeypatch):
    """Verify that public paths don't require API keys."""
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "api_key", "required-for-protected")
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "enforce_rbac", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/health")
    async def health(request: Request):
        return {"status": "ok"}

    client = TestClient(app)
    
    # Public path allows request without API key
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_gateway_disables_api_key_validation_when_not_set(monkeypatch):
    """Verify that API key validation is disabled when api_key is empty."""
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "enforce_rbac", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/api-test-endpoint-4")
    async def api_test_endpoint_4(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # Request without API key succeeds when api_key is not set
    response = client.get("/api-test-endpoint-4")
    assert response.status_code == 200
    assert response.json()["ok"] is True
