import json

from app.devops.inventory_importer import import_inventory_from_json
from app.devops.models import InfrastructureEntity, InfrastructureRelationship


def test_infrastructure_models_defaults():
    entity = InfrastructureEntity(name="VM1", entity_type="VM")
    relationship = InfrastructureRelationship(source="VM1", relationship="dependsOn", target="DB1")

    assert entity.provider == "local"
    assert entity.region == "unknown"
    assert relationship.metadata == {}


def test_import_inventory_from_json_creates_triples_and_stores_facts(tmp_path, monkeypatch):
    path = tmp_path / "inventory.json"
    path.write_text(
        json.dumps(
            {
                "entities": [{"name": "VM1", "entity_type": "VM", "provider": "local", "region": "dev"}],
                "relationships": [{"source": "VM1", "relationship": "dependsOn", "target": "Database01"}],
            }
        ),
        encoding="utf-8",
    )
    stored = []
    inserted = []
    monkeypatch.setattr("app.devops.inventory_importer.store_graph_fact", lambda *args, **kwargs: stored.append((args, kwargs)))
    monkeypatch.setattr("app.devops.inventory_importer.insert_turtle", inserted.append)

    result = import_inventory_from_json(path)

    assert result["triple_count"] == 2
    assert "project:VM1 project:dependsOn project:Database01" in result["turtle"]
    assert inserted == [result["turtle"]]
    assert len(stored) == 2
