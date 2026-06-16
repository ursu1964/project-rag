from unittest.mock import MagicMock

import app.graph.graphdb_client as graphdb_client
from app.graph.sparql_templates import dependency_query, impact_query, incoming_relationships_query, outgoing_relationships_query, reverse_dependency_query, two_hop_dependency_query
from app.graph.triple_builder import build_triple, build_turtle, sanitize_entity


def test_sparql_query_posts_expected_request(monkeypatch):
    response = MagicMock()
    response.json.return_value = {"results": {"bindings": []}}
    get = MagicMock(return_value=response)
    monkeypatch.setattr(graphdb_client.requests, "get", get)

    result = graphdb_client.sparql_query("SELECT * WHERE {}")

    assert result == {"results": {"bindings": []}}
    response.raise_for_status.assert_called_once()
    assert get.call_args.kwargs["headers"]["Accept"] == "application/sparql-results+json"


def test_insert_turtle_posts_turtle(monkeypatch):
    response = MagicMock()
    post = MagicMock(return_value=response)
    monkeypatch.setattr(graphdb_client.requests, "post", post)

    graphdb_client.insert_turtle("@prefix project: <http://projectrag.local/> .")

    response.raise_for_status.assert_called_once()
    assert post.call_args.kwargs["headers"]["Content-Type"] == "text/turtle"


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
