from unittest.mock import MagicMock

from app.agents import learning_agent


def test_learning_agent_stores_experience(monkeypatch):
    create = MagicMock(return_value="exp-1")
    add_step = MagicMock()
    outcome = MagicMock()
    monkeypatch.setattr(learning_agent, "create_experience_run", create)
    monkeypatch.setattr(learning_agent, "add_experience_step", add_step)
    monkeypatch.setattr(learning_agent, "store_experience_outcome", outcome)

    state = learning_agent.run(
        {
            "objective": "Improve topology",
            "plan": [{"step": 1, "action": "review graph"}],
            "security": {"blocked": False},
            "cost": {"estimate": "placeholder"},
            "validation": {"grounded": True},
        }
    )

    assert state["experience_run_id"] == "exp-1"
    assert "Created a recommendation plan." in state["learning"]["successes"]
    create.assert_called_once()
    add_step.assert_called_once()
    outcome.assert_called_once()


def test_learning_agent_does_not_crash_on_persistence_failure(monkeypatch):
    monkeypatch.setattr(learning_agent, "create_experience_run", MagicMock(side_effect=RuntimeError("db")))

    state = learning_agent.run({"objective": "Assess", "security": {"blocked": True}})

    assert state["experience_run_id"] is None
    assert state["learning"]["persistence_error"] == "RuntimeError"
