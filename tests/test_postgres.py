from unittest.mock import MagicMock

import app.memory.postgres as postgres


class DummyRealDictCursor:
    pass


def _mock_connection(rows=None):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows or []
    cursor_ctx = MagicMock()
    cursor_ctx.__enter__.return_value = cursor

    connection = MagicMock()
    connection.cursor.return_value = cursor_ctx
    connection_ctx = MagicMock()
    connection_ctx.__enter__.return_value = connection
    return connection_ctx, connection, cursor


def test_get_connection_uses_settings(monkeypatch):
    fake_psycopg2 = MagicMock()
    monkeypatch.setattr(postgres, "psycopg2", fake_psycopg2)
    monkeypatch.setattr(postgres, "RealDictCursor", DummyRealDictCursor)

    postgres.get_connection()

    fake_psycopg2.connect.assert_called_once()
    assert fake_psycopg2.connect.call_args.kwargs["dbname"] == postgres.settings.postgres_db
    assert fake_psycopg2.connect.call_args.kwargs["cursor_factory"] is DummyRealDictCursor


def test_fetch_all_returns_rows(monkeypatch):
    connection_ctx, _connection, cursor = _mock_connection([{"id": 1}])
    monkeypatch.setattr(postgres, "get_connection", lambda: connection_ctx)

    rows = postgres.fetch_all("SELECT 1", ())

    assert rows == [{"id": 1}]
    cursor.execute.assert_called_once_with("SELECT 1", ())


def test_execute_commits(monkeypatch):
    connection_ctx, connection, cursor = _mock_connection()
    monkeypatch.setattr(postgres, "get_connection", lambda: connection_ctx)

    postgres.execute("SELECT 1", ())

    cursor.execute.assert_called_once_with("SELECT 1", ())
    connection.commit.assert_called_once()
