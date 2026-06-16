import app.agents.topology_agent as topology_agent


def test_topology_agent_reverse_dependencies(monkeypatch):
    monkeypatch.setattr(topology_agent, "get_reverse_dependencies", lambda entity: {"entity": entity, "reverse_dependencies": []})

    state = topology_agent.run({"question": "What depends on VM1?"})

    assert state["topology_context"]["entity"] == "VM1"
    assert state["topology_context"]["intent"] == "reverse_dependencies"


def test_topology_agent_impact_analysis(monkeypatch):
    monkeypatch.setattr(topology_agent, "get_impact_path", lambda entity: {"entity": entity, "paths": []})

    state = topology_agent.run({"question": "What breaks if Database01 fails?"})

    assert state["topology_context"]["entity"] == "Database01"
    assert state["topology_context"]["intent"] == "impact_analysis"


def test_topology_agent_services_use_api(monkeypatch):
    monkeypatch.setattr(topology_agent, "get_reverse_dependencies", lambda entity: {"entity": entity, "reverse_dependencies": []})

    state = topology_agent.run({"question": "Which services use API01?"})

    assert state["topology_context"]["entity"] == "API01"
    assert state["topology_context"]["intent"] == "reverse_dependencies"


def test_topology_agent_dependencies(monkeypatch):
    monkeypatch.setattr(topology_agent, "get_dependencies", lambda entity: {"entity": entity, "dependencies": []})

    state = topology_agent.run({"question": "What does VM1 depend on?"})

    assert state["topology_context"]["entity"] == "VM1"
    assert state["topology_context"]["intent"] == "dependencies"
