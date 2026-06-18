from unittest.mock import MagicMock

import app.repositories.experience_repository as repo


def _mock_connection(row=None):
    cursor = MagicMock()
    cursor.fetchone.return_value = row or {"id": "exp-1"}
    cursor_ctx = MagicMock()
    cursor_ctx.__enter__.return_value = cursor
    connection = MagicMock()
    connection.cursor.return_value = cursor_ctx
    connection_ctx = MagicMock()
    connection_ctx.__enter__.return_value = connection
    return connection_ctx, connection, cursor


def test_create_experience_run(monkeypatch):
    connection_ctx, connection, cursor = _mock_connection()
    monkeypatch.setattr(repo, "get_connection", lambda: connection_ctx)

    assert repo.create_experience_run("goal", {"steps": []}) == "exp-1"
    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()


def test_add_experience_step(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(repo, "execute", execute)

    repo.add_experience_step("exp-1", 1, {"do": "x"}, {"ok": True})

    assert execute.call_args.args[1][0:2] == ("exp-1", 1)


def test_store_experience_outcome(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(repo, "execute", execute)

    repo.store_experience_outcome("exp-1", "completed", {"ok": True}, ["lesson"])

    assert execute.call_count == 2
    assert execute.call_args_list[0].args[1][0:2] == ("exp-1", "completed")


def test_get_experience_run(monkeypatch):
    monkeypatch.setattr(repo, "fetch_all", lambda query, params: [{"id": "exp-1"}])
    assert repo.get_experience_run("exp-1") == {"id": "exp-1"}


def test_list_recent_experience_runs(monkeypatch):
    fetch_all = MagicMock(return_value=[])
    monkeypatch.setattr(repo, "fetch_all", fetch_all)
    assert repo.list_recent_experience_runs(3) == []
    assert fetch_all.call_args.args[1] == ("local", 3)
