from unittest.mock import MagicMock

import app.graph.graphdb_client as graphdb_client
from app.graph.sparql_templates import (
    dependency_query,
    impact_query,
    incoming_relationships_query,
    outgoing_relationships_query,
    reverse_dependency_query,
    two_hop_dependency_query,
)
from app.graph.triple_builder import build_triple, build_turtle, sanitize_entity
from app.ragos.cognitive_cache import clear_cache


def test_sparql_query_posts_expected_request(monkeypatch):
    clear_cache()
    graphdb_client._repository_ready = True
    response = MagicMock()
    response.json.return_value = {"results": {"bindings": []}}
    get = MagicMock(return_value=response)
    monkeypatch.setattr(graphdb_client.requests, "get", get)

    result = graphdb_client.sparql_query("SELECT * WHERE {}")

    assert result == {"results": {"bindings": []}}
    response.raise_for_status.assert_called_once()
    assert get.call_args.kwargs["headers"]["Accept"] == "application/sparql-results+json"
    assert get.call_args.kwargs["params"]["default-graph-uri"] == "urn:projectrag:tenant:local"


def test_sparql_query_uses_cache(monkeypatch):
    clear_cache()
    graphdb_client._repository_ready = True
    response = MagicMock()
    response.json.return_value = {"results": {"bindings": [{"subject": "VM1"}]}}
    get = MagicMock(return_value=response)
    monkeypatch.setattr(graphdb_client.requests, "get", get)

    first = graphdb_client.sparql_query("SELECT * WHERE {}")
    first["results"]["bindings"][0]["subject"] = "mutated"
    second = graphdb_client.sparql_query("SELECT * WHERE {}")

    assert get.call_count == 1
    assert second["results"]["bindings"][0]["subject"] == "VM1"


def test_insert_turtle_posts_turtle(monkeypatch):
    clear_cache()
    graphdb_client._repository_ready = True
    response = MagicMock()
    post = MagicMock(return_value=response)
    monkeypatch.setattr(graphdb_client.requests, "post", post)

    graphdb_client.insert_turtle("@prefix project: <http://projectrag.local/> .")

    response.raise_for_status.assert_called_once()
    assert post.call_args.kwargs["headers"]["Content-Type"] == "text/turtle"
    assert post.call_args.kwargs["params"]["context"] == "<urn:projectrag:tenant:local>"


def test_insert_turtle_invalidates_graph_cache(monkeypatch):
    clear_cache()
    graphdb_client._repository_ready = True
    get_response = MagicMock()
    get_response.json.return_value = {"results": {"bindings": []}}
    get = MagicMock(return_value=get_response)
    post_response = MagicMock()
    post = MagicMock(return_value=post_response)
    monkeypatch.setattr(graphdb_client.requests, "get", get)
    monkeypatch.setattr(graphdb_client.requests, "post", post)

    graphdb_client.sparql_query("SELECT * WHERE {}")
    graphdb_client.insert_turtle("@prefix project: <http://projectrag.local/> .")
    graphdb_client.sparql_query("SELECT * WHERE {}")

    assert get.call_count == 2


def test_sparql_update_posts_update(monkeypatch):
    clear_cache()
    graphdb_client._repository_ready = True
    response = MagicMock()
    post = MagicMock(return_value=response)
    monkeypatch.setattr(graphdb_client.requests, "post", post)

    graphdb_client.sparql_update("DELETE DATA {}")

    response.raise_for_status.assert_called_once()
    assert post.call_args.kwargs["data"] == {"update": "DELETE DATA {}"}
    assert post.call_args.kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"


def test_delete_graph_facts_builds_delete_data(monkeypatch):
    updates = []
    monkeypatch.setattr(graphdb_client, "sparql_update", updates.append)

    deleted = graphdb_client.delete_graph_facts(
        [{"subject": "VM1", "predicate": "dependsOn", "object": "Database01"}]
    )

    assert deleted == 1
    assert "DELETE DATA" in updates[0]
    assert "GRAPH <urn:projectrag:tenant:local>" in updates[0]
    assert "project:VM1 project:dependsOn project:Database01 ." in updates[0]


def test_sparql_templates_include_project_prefix():
    assert "PREFIX project: <http://projectrag.local/>" in dependency_query("A")
    assert "project:A project:dependsOn ?dependency" in dependency_query("A")
    assert "?dependent project:dependsOn project:A" in reverse_dependency_query("A")
    assert "project:A ?predicate ?object" in outgoing_relationships_query("A")
    assert "?subject ?predicate project:A" in incoming_relationships_query("A")
    assert "?middle project:dependsOn ?dependency" in two_hop_dependency_query("A")
    assert "?impacted ?predicate project:A" in impact_query("A")


def test_sanitize_entity():
    assert sanitize_entity("My Entity!") == "My_Entity"
    assert sanitize_entity("123") == "Entity_123"


def test_build_triple_and_turtle():
    triple = build_triple("A Thing", "depends on", "B")
    turtle = build_turtle([triple])

    assert triple == "project:A_Thing project:depends_on project:B ."
    assert turtle.startswith("@prefix project: <http://projectrag.local/> .")
    assert triple in turtle
