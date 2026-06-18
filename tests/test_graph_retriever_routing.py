from app.agents import graph_retriever


def test_graph_retriever_detects_incoming(monkeypatch):
    queries = []
    monkeypatch.setattr(graph_retriever, "sparql_query", lambda query: queries.append(query) or {"results": {"bindings": []}})

    state = graph_retriever.run({"question": "what depends on Database01"})

    assert state["graph_context"]["entity"] == "Database01"
    assert state["graph_context"]["query_type"] == "incoming"
    assert len(queries) == 1
    assert "?subject ?predicate project:Database01" in queries[0]


def test_graph_retriever_detects_outgoing(monkeypatch):
    queries = []
    monkeypatch.setattr(graph_retriever, "sparql_query", lambda query: queries.append(query) or {"results": {"bindings": []}})

    state = graph_retriever.run({"question": "what does VM1 depend on"})

    assert state["graph_context"]["entity"] == "VM1"
    assert state["graph_context"]["query_type"] == "outgoing"
    assert len(queries) == 2
    assert "project:VM1 ?predicate ?object" in queries[0]


def test_graph_retriever_normalizes_outgoing_fact_text(monkeypatch):
    def fake_query(query):
        if "project:VM1 ?predicate ?object" in query:
            return {
                "results": {
                    "bindings": [
                        {
                            "predicate": {"value": "http://projectrag.local/dependsOn"},
                            "object": {"value": "http://projectrag.local/Database01"},
                        }
                    ]
                }
            }
        return {"results": {"bindings": []}}

    monkeypatch.setattr(graph_retriever, "sparql_query", fake_query)

    state = graph_retriever.run({"question": "what does VM1 depend on"})

    fact = state["graph_context"]["outgoing"][0]
    assert fact["subject"] == "VM1"
    assert fact["predicate"] == "dependsOn"
    assert fact["object"] == "Database01"
    assert fact["fact_text"] == "VM1 dependsOn Database01"


def test_graph_retriever_detects_impact(monkeypatch):
    queries = []
    monkeypatch.setattr(graph_retriever, "sparql_query", lambda query: queries.append(query) or {"results": {"bindings": []}})

    state = graph_retriever.run({"question": "what breaks if Firewall01 fails"})

    assert state["graph_context"]["entity"] == "Firewall01"
    assert state["graph_context"]["query_type"] == "impact"
    assert len(queries) == 2
    assert "?impacted ?predicate project:Firewall01" in queries[1]
