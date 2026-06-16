"""Reusable topology import pipeline for cloud and virtualization inventories."""

from __future__ import annotations

from typing import Any

from app.graph.graphdb_client import insert_turtle
from app.graph.triple_builder import build_triple, build_turtle, sanitize_entity
from app.memory.graph_fact_store import store_graph_fact


def _normalize_entity(item: dict[str, Any], provider: str) -> dict[str, Any]:
    return {
        "name": sanitize_entity(str(item.get("name") or item.get("id") or "Entity")),
        "entity_type": sanitize_entity(str(item.get("entity_type") or item.get("type") or "Resource")),
        "provider": str(item.get("provider") or provider),
        "region": str(item.get("region") or "unknown"),
        "metadata": dict(item.get("metadata") or {}),
    }


def _normalize_relationship(item: dict[str, Any]) -> dict[str, Any]:
    source = str(item.get("source") or "").strip()
    target = str(item.get("target") or "").strip()
    return {
        "source": sanitize_entity(source) if source else "",
        "relationship": sanitize_entity(str(item.get("relationship") or item.get("predicate") or "relatedTo")),
        "target": sanitize_entity(target) if target else "",
        "metadata": dict(item.get("metadata") or {}),
    }


def _import_topology(provider: str, inventory: dict[str, Any]) -> dict[str, Any]:
    entities = [_normalize_entity(item, provider) for item in inventory.get("entities", [])]
    relationships = [_normalize_relationship(item) for item in inventory.get("relationships", [])]

    triples: list[str] = []
    for entity in entities:
        triples.append(build_triple(entity["name"], "type", entity["entity_type"]))
        store_graph_fact(
            entity["name"],
            "type",
            entity["entity_type"],
            confidence=0.9,
            metadata={
                "source": "topology_import",
                "provider": entity["provider"],
                "region": entity["region"],
                **entity["metadata"],
            },
        )

    for relationship in relationships:
        if not relationship["source"] or not relationship["target"]:
            continue
        triples.append(build_triple(relationship["source"], relationship["relationship"], relationship["target"]))
        store_graph_fact(
            relationship["source"],
            relationship["relationship"],
            relationship["target"],
            confidence=0.9,
            metadata={"source": "topology_import", "provider": provider, **relationship["metadata"]},
        )

    turtle = build_turtle(triples) if triples else ""
    if turtle:
        insert_turtle(turtle)

    return {
        "provider": provider,
        "entities": entities,
        "relationships": relationships,
        "turtle": turtle,
        "entity_count": len(entities),
        "relationship_count": len(relationships),
        "triple_count": len(triples),
    }


def import_aws_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    """Convert AWS inventory into graph entities, relationships, and graph facts."""
    return _import_topology("aws", inventory)


def import_azure_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    """Convert Azure inventory into graph entities, relationships, and graph facts."""
    return _import_topology("azure", inventory)


def import_vmware_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    """Convert VMware inventory into graph entities, relationships, and graph facts."""
    return _import_topology("vmware", inventory)
