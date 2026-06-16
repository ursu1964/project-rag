from unittest.mock import MagicMock

import app.memory.knowledge_store as knowledge_store


def test_store_fact_uses_knowledge_memory(monkeypatch):
    add_memory = MagicMock(return_value="mem-1")
    monkeypatch.setattr(knowledge_store, "add_memory", add_memory)

    assert knowledge_store.store_fact("fact", {"source": "test"}) == "mem-1"
    add_memory.assert_called_once_with("knowledge", "fact", {"source": "test"})


def test_search_fact_filters_knowledge(monkeypatch):
    monkeypatch.setattr(
        knowledge_store,
        "search_memory",
        lambda query, limit: [
            {"memory_type": "knowledge", "key": "a"},
            {"memory_type": "conversation", "key": "b"},
        ],
    )

    assert knowledge_store.search_fact("a") == [{"memory_type": "knowledge", "key": "a"}]


def test_link_fact_to_graph_entity(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(knowledge_store, "execute", execute)

    knowledge_store.link_fact_to_graph_entity("mem-1", "Database 01", {"confidence": 0.9})

    params = execute.call_args.args[1]
    assert params[0] == "Database_01"
    assert params[2] == "mem-1"
