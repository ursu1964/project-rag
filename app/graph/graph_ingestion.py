"""Graph ingestion helpers for extracted entities and relationships."""

from __future__ import annotations

from app.graph.entity_extractor import extract_entities
from app.graph.graphdb_client import insert_turtle
from app.graph.ontology import RELATION_TYPES
from app.graph.relationship_extractor import extract_relationships
from app.graph.triple_builder import build_triple, build_turtle, sanitize_entity
from app.memory.graph_fact_store import store_graph_fact


def _normalize_value(value: str) -> str:
    return sanitize_entity(value) if str(value).strip() else ""


def _normalize_fact(subject: str, predicate: str, obj: str) -> dict[str, str]:
    return {
        "subject": _normalize_value(subject),
        "predicate": _normalize_value(predicate),
        "object": _normalize_value(obj),
    }


def _validate_fact(fact: dict[str, str]) -> str | None:
    if not fact["subject"] or not fact["predicate"] or not fact["object"]:
        return "empty_value"
    if fact["predicate"] not in RELATION_TYPES:
        return "unsupported_predicate"
    return None


def normalize_relationships(relationships: list[dict[str, str]]) -> list[dict[str, str]]:
    """Normalize, validate, and deduplicate relationship values."""
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for relationship in relationships:
        fact = _normalize_fact(relationship.get("subject", ""), relationship.get("predicate", ""), relationship.get("object", ""))
        if _validate_fact(fact):
            continue
        key = (fact["subject"], fact["predicate"], fact["object"])
        if key in seen:
            continue
        seen.add(key)
        normalized.append(fact)
    return normalized


def _prepare_facts(entities: list[dict[str, str]], relationships: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    accepted: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    raw_facts = [
        {"subject": entity.get("name", ""), "predicate": "type", "object": entity.get("type", "")}
        for entity in entities
    ]
    raw_facts.extend(relationships)

    for raw_fact in raw_facts:
        fact = _normalize_fact(raw_fact.get("subject", ""), raw_fact.get("predicate", ""), raw_fact.get("object", ""))
        reason = _validate_fact(fact)
        key = (fact["subject"], fact["predicate"], fact["object"])
        if reason is None and key in seen:
            reason = "duplicate"
        if reason:
            rejected.append({**fact, "reason": reason})
            continue
        seen.add(key)
        accepted.append(fact)

    return accepted, rejected


def ingest_graph_from_text(
    text: str,
    source_document_id: str | None = None,
    source_chunk_id: str | None = None,
) -> dict[str, object]:
    """Extract entities/relationships from text and insert valid facts into GraphDB and PostgreSQL."""
    entities = extract_entities(text)
    relationships = extract_relationships(text)
    facts, rejected = _prepare_facts(entities, relationships)
    normalized_relationships = [fact for fact in facts if fact["predicate"] != "type"]

    triples = [build_triple(fact["subject"], fact["predicate"], fact["object"]) for fact in facts]

    if triples:
        insert_turtle(build_turtle(triples))
        for fact in facts:
            store_graph_fact(
                fact["subject"],
                fact["predicate"],
                fact["object"],
                source_document_id=source_document_id,
                source_chunk_id=source_chunk_id,
                confidence=0.8,
                metadata={"source": "graph_ingestion"},
            )

    return {
        "entities": entities,
        "relationships": normalized_relationships,
        "inserted_count": len(facts),
        "rejected": rejected,
        "triple_count": len(facts),
    }
