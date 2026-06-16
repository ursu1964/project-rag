from unittest.mock import MagicMock

import app.api.routes_health as routes_health


def _mock_connection():
    cursor = MagicMock()
    cursor_ctx = MagicMock()
    cursor_ctx.__enter__.return_value = cursor
    connection = MagicMock()
    connection.cursor.return_value = cursor_ctx
    connection_ctx = MagicMock()
    connection_ctx.__enter__.return_value = connection
    return connection_ctx


def test_deep_health_ok(monkeypatch):
    response = MagicMock()
    response.raise_for_status.return_value = None
    monkeypatch.setattr(routes_health, "get_connection", _mock_connection)
    monkeypatch.setattr(routes_health.requests, "get", MagicMock(return_value=response))

    result = routes_health.deep_health()

    assert result == {"status": "ok", "postgres": "ok", "graphdb": "ok", "ollama": "ok"}


def test_deep_health_degraded_with_error_messages(monkeypatch):
    response = MagicMock()
    response.raise_for_status.side_effect = RuntimeError("down")
    monkeypatch.setattr(routes_health, "get_connection", _mock_connection)
    monkeypatch.setattr(routes_health.requests, "get", MagicMock(return_value=response))

    result = routes_health.deep_health()

    assert result["status"] == "degraded"
    assert result["postgres"] == "ok"
    assert result["graphdb"] == "failed"
    assert result["ollama"] == "failed"
    assert "graphdb" in result["errors"]
    assert "ollama" in result["errors"]


def test_deep_health_failed_when_all_dependencies_fail(monkeypatch):
    monkeypatch.setattr(routes_health, "get_connection", MagicMock(side_effect=RuntimeError("pg down")))
    monkeypatch.setattr(routes_health.requests, "get", MagicMock(side_effect=RuntimeError("http down")))

    result = routes_health.deep_health()

    assert result["status"] == "failed"
    assert result["postgres"] == "failed"
    assert result["graphdb"] == "failed"
    assert result["ollama"] == "failed"
