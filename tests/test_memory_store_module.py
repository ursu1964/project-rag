from unittest.mock import MagicMock

import pytest

import app.memory.memory_store as memory_store


def _mock_connection(row=None):
    cursor = MagicMock()
    cursor.fetchone.return_value = row or {"id": "mem-1"}
    cursor_ctx = MagicMock()
    cursor_ctx.__enter__.return_value = cursor
    connection = MagicMock()
    connection.cursor.return_value = cursor_ctx
    connection_ctx = MagicMock()
    connection_ctx.__enter__.return_value = connection
    return connection_ctx, connection, cursor


def test_add_memory_inserts_supported_type(monkeypatch):
    add_memory_item = MagicMock(return_value="mem-1")
    monkeypatch.setattr(memory_store, "add_memory_item", add_memory_item)

    memory_id = memory_store.add_memory("project", "ProjectRAG note", {"source": "test"})

    assert memory_id == "mem-1"
    add_memory_item.assert_called_once_with(
        "project", "ProjectRAG note", {"content": "ProjectRAG note", "metadata": {"source": "test"}}
    )


def test_add_memory_rejects_unsupported_type():
    with pytest.raises(ValueError):
        memory_store.add_memory("bad", "content")


def test_search_memory_uses_limit(monkeypatch):
    search_memory_items = MagicMock(return_value=[{"id": "mem-1"}])
    monkeypatch.setattr(memory_store, "search_memory_items", search_memory_items)

    assert memory_store.search_memory("rag", limit=3) == [{"id": "mem-1"}]
    search_memory_items.assert_called_once_with("rag", 3)


def test_list_recent_memories_uses_limit(monkeypatch):
    list_recent_memory_items = MagicMock(return_value=[])
    monkeypatch.setattr(memory_store, "list_recent_memory_items", list_recent_memory_items)

    assert memory_store.list_recent_memories(limit=7) == []
    list_recent_memory_items.assert_called_once_with(7)
