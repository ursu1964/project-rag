from app.agents.cost_agent import run


def test_cost_agent_estimates_gpu_warning():
    state = run({"question": "impact", "query_plan": {"token_budget": 4000}})
    assert state["cost"]["inference_cost"]["gpu_memory_warning"] is True


def test_cost_agent_estimates_graph_context_growth():
    state = run({"graph_context": {"incoming": [{}, {}], "outgoing": [{}], "paths": [{}]}})
    assert state["cost"]["graph_growth"]["facts"] == 4
