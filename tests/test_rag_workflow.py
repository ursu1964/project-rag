from app.workflows.rag_workflow import RAGState, build_workflow


def test_rag_state_allows_required_fields():
    state: RAGState = {"question": "hello"}
    assert state["question"] == "hello"


def test_build_workflow_returns_compiled_graph():
    workflow = build_workflow()
    assert hasattr(workflow, "invoke")
