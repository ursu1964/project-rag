from app.rag.reranker import rerank_context


def test_rerank_context_orders_vector_by_overlap_and_distance():
    result = rerank_context(
        "database dependency",
        [
            {"content": "unrelated", "distance": 0.1},
            {"content": "database dependency details", "distance": 0.5},
        ],
        [],
    )

    assert result["vector"][0]["content"] == "database dependency details"
    assert "keyword overlap" in result["explanation"]


def test_rerank_context_adds_graph_presence_bonus():
    result = rerank_context(
        "what depends on VM1",
        [],
        [
            {"subject": "API01", "predicate": "dependsOn", "object": "VM1"},
            {"subject": "Other", "predicate": "uses", "object": "Thing"},
        ],
    )

    assert result["graph"][0]["object"] == "VM1"
    assert result["graph"][0]["rerank_score"] > 0
