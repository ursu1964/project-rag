from unittest.mock import MagicMock

import app.repositories.workflow_repository as agent_store
import app.repositories.workflow_repository as validation_store
import app.repositories.workflow_repository as workflow_store


def _mock_connection(row=None):
    cursor = MagicMock()
    cursor.fetchone.return_value = row or {"id": "wf-1"}
    cursor_ctx = MagicMock()
    cursor_ctx.__enter__.return_value = cursor
    connection = MagicMock()
    connection.cursor.return_value = cursor_ctx
    connection_ctx = MagicMock()
    connection_ctx.__enter__.return_value = connection
    return connection_ctx, connection, cursor


def test_create_workflow_run_returns_id(monkeypatch):
    connection_ctx, connection, cursor = _mock_connection()
    monkeypatch.setattr(workflow_store, "get_connection", lambda: connection_ctx)

    workflow_id = workflow_store.create_workflow_run("question", "vector")

    assert workflow_id == "wf-1"
    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()


def test_complete_workflow_run_updates_status(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(workflow_store, "execute", execute)

    workflow_store.complete_workflow_run("wf-1", "completed")

    assert execute.call_args.args[1] == ("completed", "wf-1")


def test_save_workflow_checkpoint_calls_repository(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(workflow_store, "execute", execute)

    workflow_store.save_workflow_checkpoint("wf-1", "workflow_start", {"question": "q"})

    assert "workflow_checkpoints" in execute.call_args.args[0]


def test_log_agent_run_inserts_summary(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(agent_store, "execute", execute)

    agent_store.log_agent_run("wf-1", "router", "completed", 3, "in", "out")

    params = execute.call_args.args[1]
    assert params[:3] == ("wf-1", "router", "completed")


def test_store_validation_result_inserts_details(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(validation_store, "execute", execute)

    validation_store.store_validation_result("wf-1", {"grounded": True})

    params = execute.call_args.args[1]
    assert params[0] == "wf-1"
    assert params[2] is True
