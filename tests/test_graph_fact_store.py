from unittest.mock import MagicMock

import app.memory.graph_fact_store as graph_fact_store


def test_store_graph_fact_inserts_provenance(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(graph_fact_store, "execute", execute)

    graph_fact_store.store_graph_fact("A", "dependsOn", "B", source_document_id="doc-1", confidence=0.9)

    params = execute.call_args.args[1]
    assert params[:6] == ("A", "dependsOn", "B", "doc-1", None, 0.9)
    assert '"tenant_id": "local"' in params[6]


def test_list_graph_facts_filters_subject_or_object(monkeypatch):
    fetch_all = MagicMock(return_value=[{"subject": "A", "object": "B"}])
    monkeypatch.setattr(graph_fact_store, "fetch_all", fetch_all)

    assert graph_fact_store.list_graph_facts("A") == [{"subject": "A", "object": "B"}]
    assert fetch_all.call_args.args[1] == ("A", "A", "local")
    assert "metadata->>'tenant_id'" in fetch_all.call_args.args[0]
