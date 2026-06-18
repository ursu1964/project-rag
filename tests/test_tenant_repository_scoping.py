from app.repositories import chunks_repository, documents_repository, memory_repository, workflow_repository
from app.security.tenant_context import reset_request_tenant, set_request_tenant


def test_documents_list_scoped_by_context_tenant(monkeypatch):
    captured = {}

    def _fetch_all(query, params=()):
        captured["params"] = params
        return []

    token = set_request_tenant("tenant-a")
    try:
        monkeypatch.setattr(documents_repository, "fetch_all", _fetch_all)
        assert documents_repository.list_documents() == []
    finally:
        reset_request_tenant(token)

    assert captured["params"] == ("tenant-a",)


def test_chunks_similarity_search_scoped_by_tenant_and_filters(monkeypatch):
    captured = {}

    def _fetch_all(query, params=()):
        captured["query"] = query
        captured["params"] = params
        return []

    token = set_request_tenant("tenant-b")
    try:
        monkeypatch.setattr(chunks_repository, "fetch_all", _fetch_all)
        assert (
            chunks_repository.similarity_search(
                [0.1, 0.2],
                top_k=2,
                metadata_filters={"source": "runbook"},
            )
            == []
        )
    finally:
        reset_request_tenant(token)

    assert "COALESCE(c.metadata->>'tenant_id'" in captured["query"]
    assert captured["params"][1] == "tenant-b"
    assert "source" in captured["params"]
    assert "runbook" in captured["params"]


def test_memory_search_scoped_by_context_tenant(monkeypatch):
    captured = {}

    def _fetch_all(query, params=()):
        captured["params"] = params
        return []

    token = set_request_tenant("tenant-c")
    try:
        monkeypatch.setattr(memory_repository, "fetch_all", _fetch_all)
        assert memory_repository.search_memory_items("incident") == []
    finally:
        reset_request_tenant(token)

    assert captured["params"][0] == "tenant-c"


def test_workflow_list_scoped_by_context_tenant(monkeypatch):
    captured = {}

    def _fetch_all(query, params=()):
        captured["params"] = params
        return []

    token = set_request_tenant("tenant-d")
    try:
        monkeypatch.setattr(workflow_repository, "fetch_all", _fetch_all)
        assert workflow_repository.list_workflow_runs(limit=7) == []
    finally:
        reset_request_tenant(token)

    assert captured["params"] == ("tenant-d", 7)
