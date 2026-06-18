from unittest.mock import MagicMock

import app.graph.graphdb_client as graphdb_client


def test_ensure_repository_ready_creates_when_missing(monkeypatch):
    graphdb_client._repository_ready = False

    not_found = MagicMock()
    not_found.status_code = 404

    create_calls = []
    monkeypatch.setattr(graphdb_client.requests, "get", lambda *args, **kwargs: not_found)
    monkeypatch.setattr(graphdb_client, "create_repository", lambda: create_calls.append(True))

    graphdb_client.ensure_repository_ready()

    assert create_calls == [True]
    assert graphdb_client._repository_ready is True


def test_ensure_repository_ready_is_memoized(monkeypatch):
    graphdb_client._repository_ready = False

    ok = MagicMock()
    ok.status_code = 200
    get = MagicMock(return_value=ok)
    monkeypatch.setattr(graphdb_client.requests, "get", get)

    graphdb_client.ensure_repository_ready()
    graphdb_client.ensure_repository_ready()

    assert get.call_count == 1
