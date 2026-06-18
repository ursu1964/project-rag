from app.api import routes_retrieval


class _MetricRecorder:
    def __init__(self):
        self.calls = []

    def labels(self, *args):
        self.calls.append(("labels", args))
        return self

    def inc(self):
        self.calls.append(("inc",))


def test_vector_retrieval_uses_cache(monkeypatch):
    calls = {"embedding": 0}
    monkeypatch.setattr(routes_retrieval, "get_json", lambda key: None)
    stored = []
    monkeypatch.setattr(routes_retrieval, "set_json", lambda key, value, ttl_seconds=300: stored.append(value))

    def fake_embedding(query):
        calls["embedding"] += 1
        return [0.1, 0.2]

    monkeypatch.setattr(routes_retrieval, "create_embedding", fake_embedding)
    monkeypatch.setattr(routes_retrieval, "current_tenant_id", lambda: "tenant-a")
    monkeypatch.setattr(routes_retrieval, "qdrant_search", lambda embedding, top_k=5, filters=None: [])
    monkeypatch.setattr(
        routes_retrieval,
        "similarity_search",
        lambda embedding, top_k=5, tenant_id=None, metadata_filters=None: [{"content": "evidence"}],
    )

    result = routes_retrieval.vector_retrieval(routes_retrieval.RetrievalRequest(query="VM1", top_k=1))

    assert result["backend"] == "pgvector"
    assert result["cached"] is False
    assert result["results"] == [{"content": "evidence"}]
    assert calls["embedding"] == 1
    assert stored[0]["results"] == [{"content": "evidence"}]


def test_vector_retrieval_returns_cached_without_embedding(monkeypatch):
    monkeypatch.setattr(routes_retrieval, "get_json", lambda key: {"backend": "pgvector", "results": []})
    monkeypatch.setattr(
        routes_retrieval,
        "create_embedding",
        lambda query: (_ for _ in ()).throw(AssertionError("embedding should not be called")),
    )

    result = routes_retrieval.vector_retrieval(routes_retrieval.RetrievalRequest(query="VM1"))

    assert result == {"backend": "pgvector", "results": [], "cached": True}


def test_graph_retrieval_uses_bounded_depth_and_cache(monkeypatch):
    monkeypatch.setattr(routes_retrieval, "get_json", lambda key: None)
    monkeypatch.setattr(routes_retrieval, "set_json", lambda key, value, ttl_seconds=120: None)
    monkeypatch.setattr(routes_retrieval.settings, "graph_max_depth", 2)
    monkeypatch.setattr(routes_retrieval, "get_impact_path", lambda entity, depth=1: {"entity": entity, "depth": depth, "paths": []})

    result = routes_retrieval.graph_retrieval(routes_retrieval.GraphRetrievalRequest(entity="VM1", depth=5))

    assert result == {"entity": "VM1", "depth": 2, "paths": [], "cached": False}


def test_hybrid_retrieval_handles_whitespace_query(monkeypatch):
    monkeypatch.setattr(routes_retrieval, "vector_retrieval", lambda request: {"results": [{"id": "v1"}]})
    monkeypatch.setattr(routes_retrieval, "graph_retrieval", lambda request: {"paths": [{"source": request.entity}]})

    result = routes_retrieval.hybrid_retrieval(routes_retrieval.RetrievalRequest(query="   ", top_k=1))

    assert result["vector"] == [{"id": "v1"}]
    assert result["graph"] == [{"source": "unknown"}]


def test_hybrid_retrieval_uses_first_query_token_for_graph(monkeypatch):
    monkeypatch.setattr(routes_retrieval, "vector_retrieval", lambda request: {"results": []})
    monkeypatch.setattr(routes_retrieval, "graph_retrieval", lambda request: {"paths": [{"entity": request.entity}]})

    result = routes_retrieval.hybrid_retrieval(routes_retrieval.RetrievalRequest(query="VM1 depends on db", top_k=3))

    assert result["graph"] == [{"entity": "VM1"}]


def test_vector_retrieval_emits_cache_miss_metric(monkeypatch):
    recorder = _MetricRecorder()
    monkeypatch.setattr(routes_retrieval, "RETRIEVAL_CACHE_COUNTER", recorder)
    monkeypatch.setattr(routes_retrieval, "get_json", lambda key: None)
    monkeypatch.setattr(routes_retrieval, "set_json", lambda key, value, ttl_seconds=300: None)
    monkeypatch.setattr(routes_retrieval, "current_tenant_id", lambda: "tenant-a")
    monkeypatch.setattr(routes_retrieval, "create_embedding", lambda query: [0.1])
    monkeypatch.setattr(routes_retrieval, "qdrant_search", lambda embedding, top_k=5, filters=None: [])
    monkeypatch.setattr(
        routes_retrieval,
        "similarity_search",
        lambda embedding, top_k=5, tenant_id=None, metadata_filters=None: [],
    )

    routes_retrieval.vector_retrieval(routes_retrieval.RetrievalRequest(query="vm", top_k=1))

    assert ("labels", ("/retrieval/vector", "miss")) in recorder.calls
    assert ("inc",) in recorder.calls


def test_graph_retrieval_emits_cache_hit_metric(monkeypatch):
    recorder = _MetricRecorder()
    monkeypatch.setattr(routes_retrieval, "RETRIEVAL_CACHE_COUNTER", recorder)
    monkeypatch.setattr(routes_retrieval, "get_json", lambda key: {"entity": "VM1", "paths": []})

    routes_retrieval.graph_retrieval(routes_retrieval.GraphRetrievalRequest(entity="VM1", depth=1))

    assert ("labels", ("/retrieval/graph", "hit")) in recorder.calls
    assert ("inc",) in recorder.calls


def test_vector_retrieval_passes_tenant_filters(monkeypatch):
    monkeypatch.setattr(routes_retrieval, "current_tenant_id", lambda: "tenant-z")
    monkeypatch.setattr(routes_retrieval, "get_json", lambda key: None)
    monkeypatch.setattr(routes_retrieval, "set_json", lambda key, value, ttl_seconds=300: None)
    monkeypatch.setattr(routes_retrieval, "create_embedding", lambda query: [0.1])
    monkeypatch.setattr(routes_retrieval, "qdrant_search", lambda embedding, top_k=5, filters=None: [])

    captured = {}

    def _similarity(embedding, top_k=5, tenant_id=None, metadata_filters=None):
        captured["tenant_id"] = tenant_id
        captured["metadata_filters"] = metadata_filters
        return []

    monkeypatch.setattr(routes_retrieval, "similarity_search", _similarity)
    routes_retrieval.vector_retrieval(
        routes_retrieval.RetrievalRequest(query="vm", top_k=3, filters={"source": "runbook"})
    )

    assert captured["tenant_id"] == "tenant-z"
    assert captured["metadata_filters"]["tenant_id"] == "tenant-z"
    assert captured["metadata_filters"]["source"] == "runbook"


def test_vector_retrieval_cache_key_is_tenant_partitioned(monkeypatch):
    tenants = iter(["tenant-a", "tenant-b"])
    keys = []
    monkeypatch.setattr(routes_retrieval, "current_tenant_id", lambda: next(tenants))
    monkeypatch.setattr(routes_retrieval, "get_json", lambda key: keys.append(key) or None)
    monkeypatch.setattr(routes_retrieval, "set_json", lambda key, value, ttl_seconds=300: None)
    monkeypatch.setattr(routes_retrieval, "create_embedding", lambda query: [0.1])
    monkeypatch.setattr(routes_retrieval, "qdrant_search", lambda embedding, top_k=5, filters=None: [])
    monkeypatch.setattr(
        routes_retrieval,
        "similarity_search",
        lambda embedding, top_k=5, tenant_id=None, metadata_filters=None: [],
    )

    payload = routes_retrieval.RetrievalRequest(query="same", top_k=1, filters={"source": "a"})
    routes_retrieval.vector_retrieval(payload)
    routes_retrieval.vector_retrieval(payload)

    assert len(keys) == 2
    assert keys[0] != keys[1]
