"""Integration tests for rate limiting enforcement."""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.config import settings
from app.gateway import middleware


def test_gateway_rate_limit_returns_429_when_exceeded(monkeypatch):
    """Verify that the gateway returns 429 when rate limit is exceeded."""
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 1)
    monkeypatch.setattr(settings, "rate_limit_per_endpoint", "{}")
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "enforce_rbac", False)
    
    # Reset all rate limit tracking state
    middleware._REQUEST_TIMESTAMPS.clear()

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/ratelimit-test-endpoint-1")
    async def ratelimit_test_1(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # First request succeeds
    response1 = client.get("/ratelimit-test-endpoint-1")
    assert response1.status_code == 200
    
    # Second request (within same minute) is rate-limited
    response2 = client.get("/ratelimit-test-endpoint-1")
    assert response2.status_code == 429
    assert response2.json()["detail"] == "Rate limit exceeded"


def test_gateway_rate_limit_per_endpoint_overrides_global(monkeypatch):
    """Verify that per-endpoint rate limits override global limits."""
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 10)
    monkeypatch.setattr(settings, "rate_limit_per_endpoint", '{"GET /ratelimit-test-endpoint-2": 1}')
    monkeypatch.setattr(settings, "request_audit_enabled", False)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "enforce_rbac", False)
    
    # Reset all rate limit tracking state
    middleware._REQUEST_TIMESTAMPS.clear()

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/ratelimit-test-endpoint-2")
    async def ratelimit_test_2(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # First request succeeds
    response1 = client.get("/ratelimit-test-endpoint-2")
    assert response1.status_code == 200
    
    # Second request (within same minute) is rate-limited by endpoint-specific limit
    response2 = client.get("/ratelimit-test-endpoint-2")
    assert response2.status_code == 429
