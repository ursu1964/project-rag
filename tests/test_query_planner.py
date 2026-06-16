from app.agents.query_planner import run


def test_query_planner_vector_strategy():
    state = run({"question": "Summarize the document", "top_k": 3})
    plan = state["query_plan"]
    assert plan["route"] == "vector"
    assert plan["graph_depth"] == 0
    assert plan["top_k"] == 3
    assert plan["use_memory"] is True
    assert plan["use_reranking"] is True


def test_query_planner_impact_uses_graph_depth():
    plan = run({"question": "What breaks if Database01 fails?"})["query_plan"]
    assert plan["route"] == "hybrid"
    assert plan["graph_depth"] >= 1
    assert plan["token_budget"] > 0


def test_query_planner_action_disables_memory_and_reranking():
    plan = run({"question": "delete this document"})["query_plan"]
    assert plan["route"] == "action"
    assert plan["use_memory"] is False
    assert plan["use_reranking"] is False
