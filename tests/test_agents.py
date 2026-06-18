from unittest.mock import MagicMock

from app.agents import (
    context_merger,
    graph_retriever,
    memory_agent,
    reasoner,
    router,
    validator,
    vector_retriever,
)


def test_router_classifies_routes():
    assert router.run({"question": "what is in the docs?"})["route"] == "vector"
    assert router.run({"question": "dependencies of API"})["route"] == "graph"
    assert router.run({"question": "explain graph dependencies"})["route"] == "hybrid"
    assert router.run({"question": "ingest this file"})["route"] == "action"


def test_memory_agent_searches_memory_items(monkeypatch):
    search_memory = MagicMock(return_value=[{"key": "k"}])
    monkeypatch.setattr(memory_agent, "search_memory", search_memory)

    state = memory_agent.run({"question": "abc", "memory_top_k": 2})

    assert state["memory_context"] == [{"key": "k"}]
    search_memory.assert_called_once_with("abc", 2)


def test_vector_retriever_embeds_and_searches(monkeypatch):
    monkeypatch.setattr(vector_retriever, "create_embedding", lambda text: [0.1])
    search = MagicMock(return_value=[{"content": "hit"}])
    monkeypatch.setattr(vector_retriever, "similarity_search", search)

    state = vector_retriever.run({"question": "hello", "top_k": 3})

    assert state["question_embedding"] == [0.1]
    assert state["vector_context"] == [{"content": "hit"}]
    assert "vector_retrieval_ms" in state["metrics"]
    search.assert_called_once_with([0.1], 3)


def test_graph_retriever_queries_dependencies(monkeypatch):
    queries = []

    def fake_query(query):
        queries.append(query)
        return {"results": {"bindings": [{"x": {"value": "y"}}]}}

    monkeypatch.setattr(graph_retriever, "sparql_query", fake_query)

    state = graph_retriever.run({"question": "dependencies of API"})

    assert state["graph_entity"] == "API"
    assert state["graph_context"]["query_type"] == "both"
    assert state["graph_context"]["incoming"]
    assert state["graph_context"]["outgoing"]
    assert "graph_retrieval_ms" in state["metrics"]
    assert len(queries) == 2


def test_context_merger_combines_context():
    state = context_merger.run(
        {
            "memory_context": [{"m": 1}],
            "vector_context": [{"v": 1}],
            "graph_context": {"g": 1},
        }
    )

    assert state["merged_context"]["memory"][0]["m"] == 1
    assert "evidence_score" in state["merged_context"]["memory"][0]
    assert len(state["evidence"]) == 3
    assert state["evidence_summary"]["total_evidence"] == 3


def test_reasoner_generates_answer_from_context(monkeypatch):
    generate = MagicMock(return_value="answer")
    monkeypatch.setattr(reasoner, "generate", generate)

    state = reasoner.run({"question": "q", "merged_context": {"vector": [{"content": "c"}]}})

    assert state["answer"] == "answer"
    assert "llm_generation_ms" in state["metrics"]
    assert "Return structured Markdown" in generate.call_args.args[0]
    assert "Direct Answer:" in generate.call_args.args[0]
    assert "If graph evidence is empty, say so." in generate.call_args.args[0]


def test_validator_requires_evidence_and_answer():
    invalid = validator.run({"answer": "", "evidence": []})["validation"]
    # Provide evidence_summary so calibration can score properly
    valid = validator.run({
        "answer": "supported",
        "evidence": [{"content": "supported"}],
        "evidence_summary": {"top_score": 0.85, "total_evidence": 1, "vector_count": 1, "graph_count": 0},
    })["validation"]

    assert invalid["requires_human_approval"] is True
    assert "missing_answer" in invalid["warnings"]
    assert valid["grounded"] is True
    assert valid["requires_human_approval"] is False


def test_validator_ignores_prompt_rules_when_checking_uncertainty():
    answer = "Direct Answer:\nVM1 depends on Database01.\n\nRules:\nIf the context is insufficient, say you do not know."

    result = validator.run({"answer": answer, "evidence": [{"fact_text": "VM1 dependsOn Database01"}]})

    assert result["validation"]["grounded"] is True
