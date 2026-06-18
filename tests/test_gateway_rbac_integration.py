"""Integration tests for endpoint-level RBAC enforcement."""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.config import settings
from app.gateway import middleware


def test_gateway_rbac_denies_viewer_on_ingest_endpoint(monkeypatch):
    """Verify that viewers are denied access to ingest endpoints."""
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "viewer")
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "enforce_rbac", True)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "request_audit_enabled", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.delete("/documents/doc-id")
    async def delete_document(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # Viewer role cannot delete documents (ingest permission required)
    response = client.delete("/documents/doc-id")
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
    assert response.json()["policy_decision"]["permission"] == "ingest"
    assert response.json()["policy_decision"]["role"] == "viewer"
    assert response.json()["policy_decision"]["allowed"] is False


def test_gateway_rbac_denies_analyst_on_approve_endpoint(monkeypatch):
    """Verify that analysts are denied access to ingest endpoints."""
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "analyst")
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "enforce_rbac", True)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "request_audit_enabled", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.post("/ingest")
    async def ingest_documents(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # Analyst role cannot ingest documents (ingest permission required)
    response = client.post("/ingest", json={"file": "test"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
    assert response.json()["policy_decision"]["permission"] == "ingest"
    assert response.json()["policy_decision"]["role"] == "analyst"
    assert response.json()["policy_decision"]["allowed"] is False


def test_gateway_rbac_allows_admin_on_all_endpoints(monkeypatch):
    """Verify that admin role has access to all endpoints."""
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "admin")
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "enforce_rbac", True)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "request_audit_enabled", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.delete("/documents/doc-id")
    async def delete_document(request: Request):
        return {"ok": True}

    @app.post("/feedback")
    async def send_feedback(request: Request):
        return {"ok": True}

    @app.post("/query")
    async def query(request: Request):
        return {"results": []}

    client = TestClient(app)
    
    # Admin can delete (ingest permission)
    response = client.delete("/documents/doc-id")
    assert response.status_code == 200
    
    # Admin can send feedback (approve permission)
    response = client.post("/feedback", json={"feedback": "test"})
    assert response.status_code == 200
    
    # Admin can query
    response = client.post("/query", json={"query": "test"})
    assert response.status_code == 200


def test_gateway_rbac_allows_analyst_on_read_endpoint(monkeypatch):
    """Verify that analysts can read documents."""
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "analyst")
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "enforce_rbac", True)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "request_audit_enabled", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.get("/documents")
    async def list_documents(request: Request):
        return {"documents": []}

    client = TestClient(app)
    
    # Analyst can read documents
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json()["documents"] == []


def test_gateway_rbac_disabled_allows_all(monkeypatch):
    """Verify that RBAC enforcement can be disabled."""
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "viewer")
    monkeypatch.setattr(settings, "auth_required", False)
    monkeypatch.setattr(settings, "enforce_rbac", False)
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(settings, "api_key", "")
    monkeypatch.setattr(settings, "request_audit_enabled", False)

    app = FastAPI()
    middleware.install_gateway_middleware(app)

    @app.delete("/documents/doc-id")
    async def delete_document(request: Request):
        return {"ok": True}

    client = TestClient(app)
    
    # When RBAC is disabled, even viewers can delete
    response = client.delete("/documents/doc-id")
    assert response.status_code == 200
