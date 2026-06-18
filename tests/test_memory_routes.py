from app.api.routes_memory import (
    MemoryCreateRequest,
    create_memory,
    list_memory,
    search_memory_route,
)


def test_list_memory(monkeypatch):
    monkeypatch.setattr("app.api.routes_memory.list_recent_memories", lambda limit: [{"id": "1"}])
    assert list_memory(limit=10) == [{"id": "1"}]


def test_create_memory(monkeypatch):
    monkeypatch.setattr("app.api.routes_memory.add_memory", lambda memory_type, content, metadata: "mem-1")
    result = create_memory(MemoryCreateRequest(memory_type="project", content="note", metadata={}))
    assert result == {"id": "mem-1", "status": "created"}


def test_search_memory_route(monkeypatch):
    monkeypatch.setattr("app.api.routes_memory.search_memory", lambda query, limit: [{"key": query}])
    assert search_memory_route(q="rag", limit=3) == [{"key": "rag"}]
