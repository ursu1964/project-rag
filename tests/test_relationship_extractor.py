from app.graph.relationship_extractor import extract_relationships


def test_depends_on_relationship():
    relationships = extract_relationships("VM1 depends on Database01.")
    assert {"subject": "VM1", "predicate": "dependsOn", "object": "Database01"} in relationships


def test_protected_by_relationship():
    relationships = extract_relationships("Database01 is protected by Firewall01.")
    assert {"subject": "Database01", "predicate": "protectedBy", "object": "Firewall01"} in relationships
