from app.agents.router import run


def test_router_detects_graph_question():
    assert run({"question": "What dependencies does API have?"})["route"] in {"graph", "hybrid"}


def test_router_detects_vector_question():
    assert run({"question": "What does this document say?"})["route"] == "vector"
