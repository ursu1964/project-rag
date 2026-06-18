from app.agents import (
    chief_agent,
    cost_agent,
    execution_agent,
    learning_agent,
    planning_agent,
    security_agent,
)
from app.workflows.cognitive_workflow import build_workflow


def test_chief_agent_decomposes_objective():
    state = chief_agent.run({"objective": "Assess database. Recommend firewall."})
    assert state["tasks"] == ["Assess database", "Recommend firewall"]
    assert "planning" in state["needed_agents"]


def test_planning_agent_creates_safe_recommendation_plan():
    state = planning_agent.run({"objective": "Improve API", "tasks": ["Improve API"]})
    assert state["plan"][0]["mode"] == "recommendation_only"
    assert state["plan"][0]["requires_approval"] is True


def test_security_agent_blocks_execution_by_default():
    state = security_agent.run({"objective": "deploy firewall"})
    assert state["security"]["blocked"] is True
    assert state["security"]["execution_allowed"] is False
    assert state["security"]["risk"] == "high"


def test_cost_agent_returns_local_estimates():
    state = cost_agent.run({"estimated_chunks": 10, "estimated_graph_facts": 5, "query_plan": {"token_budget": 1200}})
    assert state["cost"]["impact"] == "local_resource_estimate"
    assert state["cost"]["assumptions"] == {"ram_gb": 32, "storage_gb": 1024, "gpu_gb": 4}
    assert state["cost"]["storage_growth"]["chunks"] == 10
    assert state["cost"]["graph_growth"]["facts"] == 5
    assert state["cost"]["embedding_growth"]["dimensions"] == 768
    assert state["cost"]["inference_cost"]["currency_cost"] == 0.0


def test_execution_agent_does_not_execute():
    state = execution_agent.run({"objective": "run action"})
    assert state["execution"]["status"] == "execution_disabled"
    assert state["execution"]["executed"] is False


def test_learning_agent_summarizes_lessons(monkeypatch):
    monkeypatch.setattr(learning_agent, "create_experience_run", lambda goal, plan: "exp-1")
    monkeypatch.setattr(learning_agent, "add_experience_step", lambda *args, **kwargs: None)
    monkeypatch.setattr(learning_agent, "store_experience_outcome", lambda *args, **kwargs: None)

    state = learning_agent.run({"objective": "Assess VM1", "plan": [{"step": 1}], "security": {"blocked": True}})

    assert "Review validation warnings and blocked execution before acting." in state["lessons_learned"]
    assert state["learning"]["experience_run_id"] == "exp-1"
    assert "Execution was blocked by security policy." in state["learning"]["mistakes"]


def test_cognitive_workflow_can_be_built():
    workflow = build_workflow()
    assert hasattr(workflow, "invoke")
