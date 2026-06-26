"""Security coverage checks for public routes and RBAC classification."""

from __future__ import annotations

from app.gateway.middleware import _is_public_path, _required_permission
from app.main import app


def test_all_non_public_routes_have_gateway_rbac_classification():
    missing: list[str] = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set()) or set()
        for method in sorted(methods - {"HEAD", "OPTIONS"}):
            if path and not _is_public_path(path) and _required_permission(method, path) is None:
                missing.append(f"{method} {path}")

    assert missing == []


def test_readiness_and_liveness_are_public_for_platform_probes():
    assert _is_public_path("/health/live")
    assert _is_public_path("/health/ready")
    assert _is_public_path("/api/v1/health/live")
    assert _is_public_path("/api/v1/health/ready")
