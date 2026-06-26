from app.agents import graph_retriever, vector_retriever
from app.agents.context_merger import run as merge_context
from app.rag.citations import build_citations


def test_vector_retriever_skips_graph_route(monkeypatch):
    monkeypatch.setattr(vector_retriever, "create_embedding", lambda _: (_ for _ in ()).throw(AssertionError("called")))

    result = vector_retriever.run({"route": "graph", "question": "what depends on VM1"})

    assert result["vector_context"] == []


def test_graph_retriever_skips_vector_route(monkeypatch):
    monkeypatch.setattr(graph_retriever, "sparql_query", lambda _: (_ for _ in ()).throw(AssertionError("called")))

    result = graph_retriever.run({"route": "vector", "question": "summarize docs"})

    assert result["graph_context"] == {"incoming": [], "outgoing": [], "paths": []}


def test_context_merger_filters_low_score_and_attaches_citation_ids():
    result = merge_context(
        {
            "question": "database dependency",
            "route": "vector",
            "vector_context": [
                {"content": "database dependency details", "distance": 0.2},
                {"content": "noise", "distance": 999},
            ],
            "graph_context": {},
            "memory_context": [],
            "min_evidence_score": 0.1,
        }
    )

    assert len(result["merged_context"]["vector"]) == 1
    assert result["merged_context"]["vector"][0]["citation_id"] == "V1"
    assert result["evidence_summary"]["min_evidence_score"] == 0.1


def test_build_citations_preserves_context_citation_ids_for_graph_lists():
    citations = build_citations(
        {
            "vector": [{"citation_id": "V7", "content": "chunk", "metadata": {"filename": "a.md"}}],
            "graph": [{"citation_id": "G3", "subject": "A", "predicate": "dependsOn", "object": "B"}],
            "memory": [],
        }
    )

    assert [item["id"] for item in citations] == ["V7", "G3"]
