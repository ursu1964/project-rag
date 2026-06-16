from app.graph.entity_extractor import extract_entities


def test_vm1_detected_as_vm():
    entities = extract_entities("VM VM1 is connected to SubnetA.")
    assert {"name": "VM1", "type": "VM"} in entities


def test_database01_detected_as_database():
    entities = extract_entities("Database Database01 is protected by Firewall01.")
    assert {"name": "Database01", "type": "Database"} in entities
