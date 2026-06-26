import pytest
from fastapi import HTTPException
from types import SimpleNamespace

from app.security.identity import Identity, get_local_identity
from app.security.identity import IdentityResolutionError, resolve_request_identity
from app.security.policy_engine import evaluate_permission
from app.security.rbac import has_permission, permission_dependency, permissions_for_role


def test_role_permissions():
    assert has_permission("admin", "admin") is True
    assert has_permission("admin", "approve") is True
    assert has_permission("viewer", "ingest") is False
    assert "execute_disabled" in permissions_for_role("agent")


def test_local_identity_defaults(monkeypatch):
    monkeypatch.delenv("PROJECTRAG_LOCAL_USER", raising=False)
    monkeypatch.delenv("PROJECTRAG_LOCAL_ROLE", raising=False)
    monkeypatch.delenv("PROJECTRAG_LOCAL_TENANT", raising=False)

    identity = get_local_identity()

    assert identity.subject == "local-dev"
    assert identity.role == "admin"
    assert identity.tenant_id == "local"
    assert identity.metadata["authenticated"] is False


def test_policy_engine_allows_and_denies():
    analyst = Identity(subject="a", role="analyst")
    viewer = Identity(subject="v", role="viewer")

    assert evaluate_permission("query", analyst)["allowed"] is True
    assert evaluate_permission("approve", viewer)["allowed"] is False


def test_permission_dependency_allows_verified_admin():
    dependency = permission_dependency("admin")
    request = SimpleNamespace(state=SimpleNamespace(identity=Identity(subject="a", role="admin")))

    assert dependency(request) is None


def test_permission_dependency_rejects_anonymous_request():
    dependency = permission_dependency("query")
    request = SimpleNamespace(state=SimpleNamespace())

    with pytest.raises(HTTPException) as exc_info:
        dependency(request)

    assert exc_info.value.status_code == 401


def test_permission_dependency_rejects_insufficient_role():
    dependency = permission_dependency("ingest")
    request = SimpleNamespace(state=SimpleNamespace(identity=Identity(subject="v", role="viewer")))

    with pytest.raises(HTTPException) as exc_info:
        dependency(request)

    assert exc_info.value.status_code == 403


def test_resolve_request_identity_from_trusted_headers():
    identity = resolve_request_identity(
        {
            "x-projectrag-user": "alice",
            "x-projectrag-role": "analyst",
            "x-projectrag-tenant-id": "tenant-1",
        }
    )

    assert identity.subject == "alice"
    assert identity.role == "analyst"
    assert identity.tenant_id == "tenant-1"
    assert identity.metadata["authenticated"] is True


def test_resolve_request_identity_falls_back_to_local(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_LOCAL_USER", "fallback-user")
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "viewer")
    monkeypatch.setenv("PROJECTRAG_LOCAL_TENANT", "fallback-tenant")

    identity = resolve_request_identity({})

    assert identity.subject == "fallback-user"
    assert identity.role == "viewer"
    assert identity.tenant_id == "fallback-tenant"


def test_resolve_request_identity_requires_auth():
    with pytest.raises(IdentityResolutionError):
        resolve_request_identity({}, enforce_auth=True)


def test_resolve_request_identity_rejects_unverified_bearer_when_auth_enforced():
    with pytest.raises(IdentityResolutionError):
        resolve_request_identity({"authorization": "Bearer local.token.value"}, enforce_auth=True)


def test_resolve_request_identity_uses_verified_claims_in_oidc_mode(monkeypatch):
    def _mock_verify(token: str, issuer: str, audience: str = "", jwks_url: str = "") -> dict:
        assert token == "token-123"
        assert issuer == "https://issuer.example.com"
        assert audience == "projectrag-api"
        return {"sub": "oidc-user", "role": "admin", "tid": "tenant-z"}

    monkeypatch.setattr("app.security.identity._verify_oidc_claims", _mock_verify)

    identity = resolve_request_identity(
        {"authorization": "Bearer token-123"},
        auth_mode="oidc",
        oidc_issuer="https://issuer.example.com",
        oidc_audience="projectrag-api",
    )

    assert identity.subject == "oidc-user"
    assert identity.role == "admin"
    assert identity.tenant_id == "tenant-z"
    assert identity.metadata["provider"] == "oidc_bearer_verified"


def test_resolve_request_identity_ignores_trusted_header_in_oidc_mode(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_LOCAL_USER", "fallback")
    monkeypatch.setenv("PROJECTRAG_LOCAL_ROLE", "viewer")
    monkeypatch.setenv("PROJECTRAG_LOCAL_TENANT", "local-tenant")

    identity = resolve_request_identity(
        {"x-projectrag-user": "header-user", "x-projectrag-role": "admin"},
        auth_mode="oidc",
    )

    assert identity.subject == "fallback"
    assert identity.role == "viewer"
    assert identity.tenant_id == "local-tenant"
