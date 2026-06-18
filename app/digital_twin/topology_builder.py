"""Build digital twin topology payloads from inventory and graph facts."""

from __future__ import annotations

import hashlib
from typing import Any


def _node_id(name: str) -> str:
    return str(name).strip()


def _edge_id(source: str, relationship: str, target: str) -> str:
    raw = f"{source}|{relationship}|{target}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _metadata(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _add_node(
    nodes: dict[str, dict[str, Any]],
    name: str,
    entity_type: str = "Unknown",
    metadata: dict[str, Any] | None = None,
    source: str = "unknown",
) -> None:
    node_id = _node_id(name)
    if not node_id:
        return
    existing = nodes.get(node_id)
    if existing:
        if existing.get("type") == "Unknown" and entity_type != "Unknown":
            existing["type"] = entity_type
        existing.setdefault("sources", [])
        if source not in existing["sources"]:
            existing["sources"].append(source)
        existing.setdefault("metadata", {}).update(metadata or {})
        return
    nodes[node_id] = {
        "id": node_id,
        "name": name,
        "type": entity_type,
        "metadata": metadata or {},
        "sources": [source],
    }


def _add_edge(
    edges: dict[str, dict[str, Any]],
    source: str,
    relationship: str,
    target: str,
    metadata: dict[str, Any] | None = None,
    source_type: str = "unknown",
) -> None:
    if not source or not relationship or not target:
        return
    edge_id = _edge_id(source, relationship, target)
    if edge_id in edges:
        edges[edge_id].setdefault("sources", [])
        if source_type not in edges[edge_id]["sources"]:
            edges[edge_id]["sources"].append(source_type)
        edges[edge_id].setdefault("metadata", {}).update(metadata or {})
        return
    edges[edge_id] = {
        "id": edge_id,
        "source": source,
        "target": target,
        "relationship": relationship,
        "metadata": metadata or {},
        "sources": [source_type],
    }


def build_topology(
    inventory_entities: list[dict[str, Any]],
    inventory_relationships: list[dict[str, Any]],
    graph_facts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a normalized digital twin graph with nodes, edges, and metadata."""
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, Any]] = {}

    for entity in inventory_entities:
        name = str(entity.get("entity_name") or entity.get("name") or "")
        entity_type = str(entity.get("entity_type") or "Unknown")
        _add_node(nodes, name, entity_type, _metadata(entity.get("metadata")), "inventory")

    for relationship in inventory_relationships:
        source = str(relationship.get("source_entity_name") or relationship.get("source") or "")
        target = str(relationship.get("target_entity_name") or relationship.get("target") or "")
        relation = str(relationship.get("relationship") or relationship.get("predicate") or "")
        _add_node(nodes, source, "Unknown", source="inventory_relationship")
        _add_node(nodes, target, "Unknown", source="inventory_relationship")
        _add_edge(edges, source, relation, target, _metadata(relationship.get("metadata")), "inventory")

    for fact in graph_facts:
        subject = str(fact.get("subject") or "")
        predicate = str(fact.get("predicate") or "")
        obj = str(fact.get("object") or "")
        _add_node(nodes, subject, "Unknown", source="graph_fact")
        _add_node(nodes, obj, "Unknown", source="graph_fact")
        _add_edge(edges, subject, predicate, obj, _metadata(fact.get("metadata")), "graph_fact")

    return {
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
        "metadata": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "inventory_entity_count": len(inventory_entities),
            "inventory_relationship_count": len(inventory_relationships),
            "graph_fact_count": len(graph_facts),
        },
    }
