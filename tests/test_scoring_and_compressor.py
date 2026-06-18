from app.agents.context_compressor import run as compress
from app.rag.scoring import (
    score_graph_result,
    score_memory_result,
    score_vector_result,
    weighted_score,
)
from app.workflows.rag_workflow import build_workflow


def test_score_vector_result_converts_distance():
    assert score_vector_result(0) == 1.0
    assert 0 < score_vector_result(1) < 1
    assert score_vector_result(None) == 0.0


def test_score_graph_and_memory_results():
    assert score_graph_result({"results": {"bindings": [{"x": 1}]}}) == 1.0
    assert score_graph_result({"results": {"bindings": []}}) == 0.0
    assert score_memory_result({"key": "k"}) == 1.0


def test_weighted_score_uses_route_weights():
    assert weighted_score("graph", 0, 1, 0, 0) == 0.55
    assert weighted_score("vector", 1, 0, 0, 0) == 0.60
    assert weighted_score("hybrid", 1, 1, 1, 1) == 1.0


def test_context_compressor_preserves_required_fields():
    state = compress(
        {
            "merged_context": {
                "memory": [{"key": "m"}],
                "vector": [{"content": "x" * 1000, "distance": 0.2, "metadata": {"filename": "a.txt"}}],
                "graph": {"facts": ["a dependsOn b"]},
            }
        }
    )

    compressed = state["compressed_context"]
    assert compressed["memory"] == [{"key": "m"}]
    assert compressed["vector"][0]["filename"] == "a.txt"
    assert compressed["vector"][0]["distance"] == 0.2
    assert compressed["vector"][0]["content"].endswith("...")
    assert compressed["graph_facts"] == {"facts": ["a dependsOn b"]}


def test_workflow_includes_compress_node():
    workflow = build_workflow()
    assert hasattr(workflow, "invoke")
