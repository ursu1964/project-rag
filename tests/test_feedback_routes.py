import pytest
from fastapi import HTTPException

from app.api import routes_feedback
from app.api.routes_feedback import FeedbackRequest, submit_feedback
from app.repositories import workflow_repository


def test_submit_feedback_stores_workflow_feedback(monkeypatch):
    stored = []
    monkeypatch.setattr(
        routes_feedback,
        "store_workflow_feedback",
        lambda workflow_id, feedback: stored.append((workflow_id, feedback)) or feedback,
    )

    result = submit_feedback("wf-1", FeedbackRequest(rating=5, helpful=True, comment="good"))

    assert result == {
        "status": "stored",
        "workflow_id": "wf-1",
        "feedback": {"rating": 5, "helpful": True, "comment": "good"},
    }
    assert stored == [("wf-1", {"rating": 5, "helpful": True, "comment": "good"})]


def test_submit_feedback_404_when_workflow_missing(monkeypatch):
    monkeypatch.setattr(routes_feedback, "store_workflow_feedback", lambda workflow_id, feedback: None)

    with pytest.raises(HTTPException) as exc:
        submit_feedback("missing", FeedbackRequest(rating=1))

    assert exc.value.status_code == 404


def test_store_workflow_feedback_updates_output_and_trend(monkeypatch):
    workflow = {
        "id": "wf-1",
        "input": {"question": "What does VM1 depend on?"},
        "output": {"answer": "VM1 depends on Database01.", "provenance": {"user_feedback": None}},
    }
    outputs = []
    sql_calls = []
    monkeypatch.setattr(workflow_repository, "get_workflow_run", lambda workflow_id: workflow)
    monkeypatch.setattr(workflow_repository, "store_workflow_output", lambda workflow_id, output: outputs.append((workflow_id, output)))
    monkeypatch.setattr(workflow_repository, "execute", lambda query, params=(): sql_calls.append((query, params)))

    feedback = workflow_repository.store_workflow_feedback("wf-1", {"rating": 4, "helpful": True, "comment": "useful"})

    assert feedback == {"rating": 4, "helpful": True, "comment": "useful"}
    assert outputs[0][0] == "wf-1"
    assert outputs[0][1]["provenance"]["user_feedback"] == feedback
    assert outputs[0][1]["user_feedback"] == feedback
    assert sql_calls[0][1][0] == "user_feedback"
    assert sql_calls[0][1][1] == "What does VM1 depend on?"
