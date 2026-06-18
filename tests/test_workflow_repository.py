
from app.repositories import workflow_repository


def test_store_workflow_output_updates_json(monkeypatch):
    calls = []
    monkeypatch.setattr(workflow_repository, "execute", lambda query, params=(): calls.append((query, params)))

    workflow_repository.store_workflow_output("wf-1", {"answer": "ok"})

    assert "UPDATE workflow_runs" in calls[0][0]
    assert calls[0][1][1] == "wf-1"
    assert '"answer": "ok"' in calls[0][1][0]
