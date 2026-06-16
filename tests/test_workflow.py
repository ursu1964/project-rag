from app.workflows.rag_workflow import build_workflow


def test_workflow_can_be_built():
    workflow = build_workflow()
    assert hasattr(workflow, "invoke")
