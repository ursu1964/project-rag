import app.graph.traversal as traversal


def _result(bindings):
    return {"results": {"bindings": bindings}}


def test_get_neighbors_returns_incoming_and_outgoing(monkeypatch):
    calls = []

    def fake_query(query):
        calls.append(query)
        if len(calls) == 1:
            return _result([{"predicate": {"value": "project:uses"}, "object": {"value": "project:DB"}}])
        return _result([{"subject": {"value": "project:API"}, "predicate": {"value": "project:dependsOn"}}])

    monkeypatch.setattr(traversal, "sparql_query", fake_query)

    result = traversal.get_neighbors("VM1")

    assert result["entity"] == "VM1"
    assert result["neighbors"]["outgoing"][0]["object"] == "project:DB"
    assert result["neighbors"]["incoming"][0]["subject"] == "project:API"


def test_get_dependencies_filters_depends_on(monkeypatch):
    monkeypatch.setattr(
        traversal,
        "sparql_query",
        lambda query: _result(
            [
                {"predicate": {"value": "project:dependsOn"}, "object": {"value": "project:DB"}},
                {"predicate": {"value": "project:uses"}, "object": {"value": "project:API"}},
            ]
        ),
    )

    result = traversal.get_dependencies("VM1")

    assert result["dependencies"] == [{"predicate": "project:dependsOn", "target": "project:DB"}]


def test_get_reverse_dependencies_filters_depends_on(monkeypatch):
    monkeypatch.setattr(
        traversal,
        "sparql_query",
        lambda query: _result([{"subject": {"value": "project:API"}, "predicate": {"value": "project:dependsOn"}}]),
    )

    result = traversal.get_reverse_dependencies("DB")

    assert result["reverse_dependencies"] == [{"source": "project:API", "predicate": "project:dependsOn"}]


def test_get_impact_path_caps_depth(monkeypatch):
    monkeypatch.setattr(traversal, "sparql_query", lambda query: _result([]))
    monkeypatch.setattr(traversal.settings, "graph_max_depth", 2)

    result = traversal.get_impact_path("DB", depth=10)

    assert result["depth"] == 2
    assert result["paths"] == []
