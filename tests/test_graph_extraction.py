from app.graph.entity_extractor import extract_entities
from app.graph.graph_ingestion import ingest_graph_from_text, normalize_relationships
from app.graph.relationship_extractor import extract_relationships


def test_extract_entities_detects_infrastructure_types():
    text = "VM web01 uses database pg01. Subnet private is protected by firewall fw01. API billing calls service auth. VNet prod contains resources."
    entities = extract_entities(text)
    types = {entity["type"] for entity in entities}

    assert {"VM", "Database", "Subnet", "Firewall", "API", "Service", "VNet"}.issubset(types)


def test_extract_relationships_detects_supported_predicates():
    text = (
        "web01 depends on pg01. web01 is connected to private. api uses database. "
        "subnet is protected by fw01. app runs on vm01. nic belongs to vnet1. "
        "api calls service. worker reads from queue. worker writes to database."
    )
    predicates = {relationship["predicate"] for relationship in extract_relationships(text)}

    assert {
        "dependsOn",
        "connectedTo",
        "uses",
        "protectedBy",
        "runsOn",
        "belongsTo",
        "calls",
        "readsFrom",
        "writesTo",
    }.issubset(predicates)


def test_normalize_relationships_deduplicates_and_sanitizes():
    relationships = normalize_relationships(
        [
            {"subject": "web 01", "predicate": "dependsOn", "object": "pg-01"},
            {"subject": "web 01", "predicate": "dependsOn", "object": "pg-01"},
        ]
    )

    assert relationships == [{"subject": "web_01", "predicate": "dependsOn", "object": "pg_01"}]


def test_ingest_graph_from_text_builds_and_inserts_turtle(monkeypatch):
    inserted = []
    stored = []
    monkeypatch.setattr("app.graph.graph_ingestion.insert_turtle", inserted.append)
    monkeypatch.setattr("app.graph.graph_ingestion.store_graph_fact", lambda *args, **kwargs: stored.append((args, kwargs)))

    result = ingest_graph_from_text("VM web01 depends on database pg01.", source_document_id="doc-1")

    assert result["inserted_count"] >= 1
    assert inserted
    assert "project:web01 project:dependsOn project:pg01" in inserted[0]
    assert stored
    assert stored[0][1]["source_document_id"] == "doc-1"


def test_ingest_graph_rejects_invalid_empty_duplicate_facts(monkeypatch):
    monkeypatch.setattr("app.graph.graph_ingestion.extract_entities", lambda text: [])
    monkeypatch.setattr(
        "app.graph.graph_ingestion.extract_relationships",
        lambda text: [
            {"subject": "A", "predicate": "uses", "object": "B"},
            {"subject": "A", "predicate": "uses", "object": "B"},
            {"subject": "A", "predicate": "unknown", "object": "B"},
            {"subject": "", "predicate": "uses", "object": "B"},
        ],
    )
    inserted = []
    monkeypatch.setattr("app.graph.graph_ingestion.insert_turtle", inserted.append)
    monkeypatch.setattr("app.graph.graph_ingestion.store_graph_fact", lambda *args, **kwargs: None)

    result = ingest_graph_from_text("ignored")

    assert result["inserted_count"] == 1
    assert len(result["rejected"]) == 3
    assert {item["reason"] for item in result["rejected"]} == {"duplicate", "unsupported_predicate", "empty_value"}
    assert "project:A project:uses project:B" in inserted[0]
