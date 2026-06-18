import app.agents.rca_agent as rca_agent
import app.simulation.simulation_engine as simulation_engine


def test_rca_agent_proposes_root_cause(monkeypatch):
    monkeypatch.setattr(rca_agent, "get_dependencies", lambda entity: {"dependencies": [{"target": "Database01"}]})
    monkeypatch.setattr(rca_agent, "get_reverse_dependencies", lambda entity: {"reverse_dependencies": [{"source": "ServiceA"}]})
    monkeypatch.setattr(rca_agent, "get_neighbors", lambda entity: {"neighbors": {"incoming": [], "outgoing": []}})

    state = rca_agent.run({"symptoms": ["ServiceA outage on API01"], "entity": "API01"})

    assert state["rca_context"]["probable_root_causes"][0]["entity"] == "API01"
    assert state["rca_context"]["confidence"] > 0


def test_simulate_failure_returns_impacted_nodes(monkeypatch):
    graph = {
        "VM1": {"neighbors": {"incoming": [{"subject": "ApplicationA"}], "outgoing": [{"object": "SubnetA"}]}},
        "ApplicationA": {"neighbors": {"incoming": [], "outgoing": []}},
        "SubnetA": {"neighbors": {"incoming": [], "outgoing": []}},
    }
    monkeypatch.setattr(simulation_engine, "get_neighbors", lambda entity: graph[entity])

    result = simulation_engine.simulate_failure("VM1", depth=2)

    assert sorted(result["impacted_nodes"]) == ["ApplicationA", "SubnetA"]
    assert result["execution"] == "disabled"
    assert "No real actions" in result["risk_explanation"]
