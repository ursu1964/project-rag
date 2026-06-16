from app.api.routes_documents import ingest_raw_documents, list_documents
from app.api.routes_graph import graph_query
from app.api.routes_health import health
from app.core.schemas import GraphQueryRequest, QueryRequest
from app.api.routes_query import query
from app.main import create_app


def test_health():
    assert health() == {"status": "ok", "service": "ProjectRAG"}


def test_query_runs_workflow(monkeypatch):
    class Workflow:
        def invoke(self, state):
            return {**state, "answer": "ok", "validation": {"grounded": True}}

    monkeypatch.setattr("app.api.routes_query.create_workflow_run", lambda question: "wf-1")
    monkeypatch.setattr("app.api.routes_query.complete_workflow_run", lambda workflow_id, status="completed": None)
    monkeypatch.setattr("app.api.routes_query.store_validation_result", lambda workflow_id, validation: None)
    monkeypatch.setattr("app.api.routes_query.build_workflow", lambda: Workflow())
    result = query(QueryRequest(question="hello"))
    assert result["answer"] == "ok"
    assert result["metrics"]["workflow_id"] == "wf-1"
    assert "duration_ms" in result["metrics"]


def test_list_documents(monkeypatch):
    monkeypatch.setattr("app.api.routes_documents.repository_list_documents", lambda: [{"id": "1"}] )
    assert list_documents() == [{"id": "1"}]


def test_ingest_raw_documents(monkeypatch):
    monkeypatch.setattr("app.api.routes_documents.ingest_directory", lambda directory: [{"status": "ingested"}])
    assert ingest_raw_documents() == {"status": "ok", "results": [{"status": "ingested"}]}


def test_graph_query(monkeypatch):
    monkeypatch.setattr("app.api.routes_graph.sparql_query", lambda sparql: {"query": sparql})
    assert graph_query(GraphQueryRequest(query="SELECT * WHERE {}")) == {"query": "SELECT * WHERE {}"}


def test_create_app_registers_routes():
    paths = {route.path for route in create_app().routes}
    assert {"/health", "/health/deep", "/query", "/documents", "/documents/upload", "/ingest", "/graph/query", "/memory", "/memory/search", "/devops/inventory/import", "/cognitive/query"}.issubset(paths)


def test_query_debug_returns_full_state(monkeypatch):
    class Workflow:
        def invoke(self, state):
            return {**state, "answer": "ok", "validation": {"grounded": True}, "internal": "value"}

    monkeypatch.setattr("app.api.routes_query.create_workflow_run", lambda question: "wf-1")
    monkeypatch.setattr("app.api.routes_query.complete_workflow_run", lambda workflow_id, status="completed": None)
    monkeypatch.setattr("app.api.routes_query.store_validation_result", lambda workflow_id, validation: None)
    monkeypatch.setattr("app.api.routes_query.build_workflow", lambda: Workflow())

    result = query(QueryRequest(question="hello"), debug=True)

    assert result["internal"] == "value"
    assert result["workflow_id"] == "wf-1"
