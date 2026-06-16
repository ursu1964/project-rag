from app.graph.graph_ingestion import normalize_relationships


def test_duplicate_relationships_are_removed():
    relationships = normalize_relationships(
        [
            {"subject": "VM1", "predicate": "dependsOn", "object": "Database01"},
            {"subject": "VM1", "predicate": "dependsOn", "object": "Database01"},
        ]
    )
    assert relationships == [{"subject": "VM1", "predicate": "dependsOn", "object": "Database01"}]
