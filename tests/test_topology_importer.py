import app.devops.topology_importer as importer


def test_import_aws_inventory_converts_to_graph(monkeypatch):
    stored = []
    inserted = []
    monkeypatch.setattr(importer, "store_graph_fact", lambda *args, **kwargs: stored.append((args, kwargs)))
    monkeypatch.setattr(importer, "insert_turtle", inserted.append)

    result = importer.import_aws_inventory(
        {
            "entities": [{"name": "i-123", "entity_type": "EC2Instance", "region": "us-east-1"}],
            "relationships": [{"source": "i-123", "relationship": "connectedTo", "target": "subnet-1"}],
        }
    )

    assert result["provider"] == "aws"
    assert result["entity_count"] == 1
    assert result["relationship_count"] == 1
    assert "project:i_123 project:connectedTo project:subnet_1" in result["turtle"]
    assert inserted == [result["turtle"]]
    assert len(stored) == 2


def test_import_azure_inventory_defaults_provider(monkeypatch):
    monkeypatch.setattr(importer, "store_graph_fact", lambda *args, **kwargs: None)
    monkeypatch.setattr(importer, "insert_turtle", lambda turtle: None)

    result = importer.import_azure_inventory({"entities": [{"name": "vm1", "type": "VM"}]})

    assert result["entities"][0]["provider"] == "azure"
    assert result["entities"][0]["entity_type"] == "VM"


def test_import_vmware_inventory_skips_empty_relationship(monkeypatch):
    monkeypatch.setattr(importer, "store_graph_fact", lambda *args, **kwargs: None)
    monkeypatch.setattr(importer, "insert_turtle", lambda turtle: None)

    result = importer.import_vmware_inventory(
        {"relationships": [{"source": "", "relationship": "runsOn", "target": "host1"}]}
    )

    assert result["relationship_count"] == 1
    assert result["triple_count"] == 0
