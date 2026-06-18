from app.brain.infrastructure_brain import combine_contexts, run
from app.brain.knowledge_pyramid import build_knowledge_pyramid
from app.brain.model_matrix import get_model_matrix


def test_infrastructure_brain_combines_contexts():
    result = combine_contexts({"graph_context": {"entity": "VM1"}, "prediction_context": {"risk": "low"}})

    assert "graph" in result["available_contexts"]
    assert "prediction" in result["available_contexts"]
    assert result["execution"] == "disabled"


def test_infrastructure_brain_run_adds_state_key():
    state = run({"memory_context": [{"content": "x"}]})

    assert "infrastructure_brain" in state
    assert "memory" in state["infrastructure_brain"]["available_contexts"]


def test_knowledge_pyramid_levels():
    result = build_knowledge_pyramid({"memory": {"fact": "x"}})

    assert result["levels"]["knowledge"] == {"fact": "x"}
    assert result["execution"] == "disabled"


def test_model_matrix_overrides():
    result = get_model_matrix({"reasoning": "medium"})

    assert result["matrix"]["reasoning"] == "medium"
    assert result["execution"] == "disabled"
