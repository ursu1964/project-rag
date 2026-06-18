
from app.repositories import workflow_repository


def test_store_workflow_output_updates_json(monkeypatch):
    calls = []
    monkeypatch.setattr(workflow_repository, "execute", lambda query, params=(): calls.append((query, params)))

    workflow_repository.store_workflow_output("wf-1", {"answer": "ok"})

    assert "UPDATE workflow_runs" in calls[0][0]
    assert calls[0][1][1] == "wf-1"
    assert '"answer": "ok"' in calls[0][1][0]


def test_save_workflow_checkpoint_upserts(monkeypatch):
    calls = []
    monkeypatch.setattr(workflow_repository, "execute", lambda query, params=(): calls.append((query, params)))

    workflow_repository.save_workflow_checkpoint(
        "wf-1",
        "workflow_start",
        {"question": "hello"},
        status="running",
    )

    assert "INSERT INTO workflow_checkpoints" in calls[0][0]
    assert calls[0][1][0] == "wf-1"
    assert calls[0][1][1] == "workflow_start"
    assert calls[0][1][3] == "running"


def test_list_workflow_checkpoints_returns_rows(monkeypatch):
    monkeypatch.setattr(
        workflow_repository,
        "fetch_all",
        lambda query, params=(): [{"workflow_id": params[0], "step_name": "workflow_start"}],
    )

    rows = workflow_repository.list_workflow_checkpoints("wf-1")

    assert rows == [{"workflow_id": "wf-1", "step_name": "workflow_start"}]


def test_latest_workflow_checkpoint_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(workflow_repository, "fetch_all", lambda query, params=(): [])

    checkpoint = workflow_repository.latest_workflow_checkpoint("wf-missing")

    assert checkpoint is None
