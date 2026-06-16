from unittest.mock import MagicMock

import app.memory.ontology_store as ontology_store


def test_store_entity_definition(monkeypatch):
    add_memory = MagicMock(return_value="ont-1")
    monkeypatch.setattr(ontology_store, "add_memory", add_memory)

    assert ontology_store.store_entity_definition("Database", "A data store") == "ont-1"
    args = add_memory.call_args.args
    assert args[0] == "ontology"
    assert args[2]["kind"] == "entity_definition"
    assert args[2]["entity_type"] == "Database"


def test_store_relationship_definition(monkeypatch):
    add_memory = MagicMock(return_value="ont-2")
    monkeypatch.setattr(ontology_store, "add_memory", add_memory)

    assert ontology_store.store_relationship_definition("dependsOn", "Requires target") == "ont-2"
    assert add_memory.call_args.args[2]["kind"] == "relationship_definition"


def test_store_ontology_version(monkeypatch):
    add_memory = MagicMock(return_value="ont-3")
    monkeypatch.setattr(ontology_store, "add_memory", add_memory)

    assert ontology_store.store_ontology_version("0.1.0", "initial") == "ont-3"
    assert add_memory.call_args.args[2]["version"] == "0.1.0"


def test_search_ontology_filters_type(monkeypatch):
    monkeypatch.setattr(
        ontology_store,
        "search_memory",
        lambda query, limit: [
            {"memory_type": "ontology", "key": "entity:VM"},
            {"memory_type": "knowledge", "key": "VM"},
        ],
    )

    assert ontology_store.search_ontology("VM") == [{"memory_type": "ontology", "key": "entity:VM"}]
