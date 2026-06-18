import app.digital_twin.generator as generator
from app.digital_twin.topology_builder import build_topology


def test_build_topology_merges_inventory_and_graph_facts():
    result = build_topology(
        [{"entity_name": "VM1", "entity_type": "VM", "metadata": {"region": "local"}}],
        [{"source_entity_name": "App1", "relationship": "runsOn", "target_entity_name": "VM1"}],
        [{"subject": "VM1", "predicate": "dependsOn", "object": "Database01"}],
    )

    node_ids = {node["id"] for node in result["nodes"]}
    relationships = {edge["relationship"] for edge in result["edges"]}

    assert {"VM1", "App1", "Database01"}.issubset(node_ids)
    assert {"runsOn", "dependsOn"}.issubset(relationships)
    assert result["metadata"]["node_count"] == 3
    assert result["metadata"]["edge_count"] == 2


def test_generate_digital_twin_loads_all_sources(monkeypatch):
    monkeypatch.setattr(generator, "load_inventory_entities", lambda: [{"entity_name": "API01", "entity_type": "API"}])
    monkeypatch.setattr(
        generator,
        "load_inventory_relationships",
        lambda: [{"source_entity_name": "ServiceA", "relationship": "calls", "target_entity_name": "API01"}],
    )
    monkeypatch.setattr(generator, "load_graph_facts", lambda: [])

    result = generator.generate_digital_twin()

    assert result["metadata"]["inventory_entity_count"] == 1
    assert result["metadata"]["inventory_relationship_count"] == 1
    assert result["nodes"]
    assert result["edges"]
