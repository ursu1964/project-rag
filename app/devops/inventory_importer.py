"""JSON inventory importer for future DevOps integrations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.devops.models import InfrastructureEntity, InfrastructureRelationship
from app.graph.graphdb_client import insert_turtle
from app.graph.triple_builder import build_triple, build_turtle, sanitize_entity
from app.memory.graph_fact_store import store_graph_fact


def _load_inventory(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def import_inventory_from_json(path: Path) -> dict[str, Any]:
    """Import local JSON inventory into graph triples and graph_facts."""
    inventory = _load_inventory(path)
    entities = [InfrastructureEntity(**item) for item in inventory.get("entities", [])]
    relationships = [InfrastructureRelationship(**item) for item in inventory.get("relationships", [])]

    triples: list[str] = []
    for entity in entities:
        subject = sanitize_entity(entity.name)
        entity_type = sanitize_entity(entity.entity_type)
        triples.append(build_triple(subject, "type", entity_type))
        store_graph_fact(
            subject,
            "type",
            entity_type,
            confidence=0.9,
            metadata={"source": "inventory_import", "provider": entity.provider, "region": entity.region, **entity.metadata},
        )

    for relationship in relationships:
        source = sanitize_entity(relationship.source)
        predicate = sanitize_entity(relationship.relationship)
        target = sanitize_entity(relationship.target)
        triples.append(build_triple(source, predicate, target))
        store_graph_fact(
            source,
            predicate,
            target,
            confidence=0.9,
            metadata={"source": "inventory_import", **relationship.metadata},
        )

    turtle = build_turtle(triples) if triples else ""
    if turtle:
        insert_turtle(turtle)

    return {
        "entities": [entity.model_dump() for entity in entities],
        "relationships": [relationship.model_dump() for relationship in relationships],
        "turtle": turtle,
        "triple_count": len(triples),
    }
