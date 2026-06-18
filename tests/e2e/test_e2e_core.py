"""E2E-style tests for the local ProjectRAG MVP using safe fakes.

These tests exercise API and pipeline boundaries without requiring live Docker,
GraphDB, PostgreSQL, or Ollama services.
"""

import app.agents.vector_retriever as vector_retriever
import app.api.routes_graph as routes_graph
import app.api.routes_query as routes_query
import app.graph.graph_ingestion as graph_ingestion
import app.rag.ingestion as ingestion
from app.api.routes_health import health
from app.core.schemas import GraphQueryRequest, QueryRequest
from app.tools import docker_tool, graphdb_tool, postgres_tool


def test_e2e_health_endpoint():
    assert health() == {"status": "ok", "service": "ProjectRAG"}


def test_e2e_document_ingestion_pipeline(tmp_path, monkeypatch):
    file_path = tmp_path / "topology.txt"
    file_path.write_text("VM1 depends on Database01.", encoding="utf-8")
    inserted_chunks = []

    monkeypatch.setattr(ingestion, "get_document_by_hash", lambda file_hash: None)
    monkeypatch.setattr(ingestion, "count_graph_facts_for_document", lambda document_id: 0)
    monkeypatch.setattr(ingestion, "register_document", lambda *args, **kwargs: "doc-1")
    monkeypatch.setattr(ingestion, "create_embedding", lambda text: [0.1] * 768)
    monkeypatch.setattr(ingestion, "insert_chunk", lambda **kwargs: inserted_chunks.append(kwargs))
    monkeypatch.setattr(
        ingestion,
        "ingest_graph_from_text",
        lambda text, source_document_id=None: {"inserted_count": 1},
    )

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "ingested"
    assert result["document_id"] == "doc-1"
    assert inserted_chunks
    assert inserted_chunks[0]["document_id"] == "doc-1"


def test_e2e_vector_retrieval(monkeypatch):
    monkeypatch.setattr(vector_retriever, "create_embedding", lambda question: [0.2] * 768)
    monkeypatch.setattr(
        vector_retriever,
        "similarity_search",
        lambda embedding, top_k: [{"content": "VM1 depends on Database01", "distance": 0.1}],
    )

    state = vector_retriever.run({"question": "What does VM1 depend on?", "top_k": 1})

    assert state["question_embedding"] == [0.2] * 768
    assert state["vector_context"][0]["content"] == "VM1 depends on Database01"
    assert "vector_retrieval_ms" in state["metrics"]


def test_e2e_graph_extraction(monkeypatch):
    inserted_turtle = []
    stored_facts = []
    monkeypatch.setattr(graph_ingestion, "insert_turtle", inserted_turtle.append)
    monkeypatch.setattr(
        graph_ingestion,
        "store_graph_fact",
        lambda subject, predicate, obj, **kwargs: stored_facts.append((subject, predicate, obj)),
    )

    result = graph_ingestion.ingest_graph_from_text("VM1 depends on Database01.")

    assert result["inserted_count"] >= 1
    assert any(rel["predicate"] == "dependsOn" for rel in result["relationships"])
    assert inserted_turtle
    assert ("VM1", "dependsOn", "Database01") in stored_facts


def test_e2e_graph_query_endpoint(monkeypatch):
    monkeypatch.setattr(
        routes_graph,
        "sparql_query",
        lambda query: {"results": {"bindings": [{"query": {"value": query}}]}},
    )
    response = routes_graph.graph_query(GraphQueryRequest(query="SELECT * WHERE { ?s ?p ?o }"))

    assert "results" in response


def test_e2e_hybrid_query_and_validation_output(monkeypatch):
    class Workflow:
        def invoke(self, state):
            return {
                **state,
                "route": "hybrid",
                "answer": "VM1 depends on Database01.",
                "vector_context": [{"content": "VM1 depends on Database01"}],
                "graph_context": {"entity": "VM1", "outgoing": [{"object": "Database01"}]},
                "memory_context": [],
                "validation": {
                    "grounded": True,
                    "confidence": 0.9,
                    "warnings": [],
                    "requires_human_approval": False,
                },
                "metrics": {"vector_retrieval_ms": 1, "graph_retrieval_ms": 1},
            }

    monkeypatch.setattr(routes_query, "create_workflow_run", lambda question: "wf-1")
    monkeypatch.setattr(routes_query, "complete_workflow_run", lambda workflow_id, status="completed": None)
    monkeypatch.setattr(routes_query, "store_validation_result", lambda workflow_id, validation: None)
    monkeypatch.setattr(routes_query, "store_workflow_output", lambda workflow_id, output: None)
    monkeypatch.setattr(routes_query, "build_workflow", lambda: Workflow())
    body = routes_query.query(QueryRequest(question="What does VM1 depend on?"))
    assert body["route"] == "hybrid"
    assert body["validation"]["grounded"] is True
    assert body["metrics"]["workflow_id"] == "wf-1"
    assert body["evidence"]["vector"]
    assert body["evidence"]["graph"]


def test_e2e_tool_governance_blocks_dangerous_commands():
    assert postgres_tool.postgres_select("DROP TABLE documents")["status"] == "blocked"
    assert graphdb_tool.graphdb_select("DELETE WHERE { ?s ?p ?o }")["status"] == "blocked"
    assert docker_tool.docker_logs("docker rm projectrag-postgres")["status"] == "blocked"
