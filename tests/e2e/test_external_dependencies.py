"""External dependency E2E checks.

Run explicitly with:
    RUN_EXTERNAL_E2E=1 pytest tests/e2e/test_external_dependencies.py
"""

import os

import pytest

from app.api.routes_health import deep_health

pytestmark = pytest.mark.external_dependency


def _require_external_e2e():
    if os.getenv("RUN_EXTERNAL_E2E") != "1":
        pytest.skip("External dependency E2E tests require RUN_EXTERNAL_E2E=1")


def test_external_deep_health_dependencies():
    _require_external_e2e()
    body = deep_health()
    assert body["postgres"] == "ok"
    assert body["graphdb"] == "ok"
    assert body["ollama"] == "ok"
