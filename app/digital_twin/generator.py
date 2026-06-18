"""Generate digital twin topology from ProjectRAG stores."""

from __future__ import annotations

from typing import Any

from app.digital_twin.topology_builder import build_topology
from app.memory.postgres import fetch_all


def load_inventory_entities() -> list[dict[str, Any]]:
    """Load discovered inventory entities."""
    return fetch_all(
        """
        SELECT id, discovery_run_id, entity_name, entity_type, provider, region, metadata, created_at
        FROM inventory_entities
        ORDER BY created_at DESC
        """
    )


def load_inventory_relationships() -> list[dict[str, Any]]:
    """Load discovered inventory relationships."""
    return fetch_all(
        """
        SELECT id, discovery_run_id, source_entity_name, relationship, target_entity_name, metadata, created_at
        FROM inventory_relationships
        ORDER BY created_at DESC
        """
    )


def load_graph_facts() -> list[dict[str, Any]]:
    """Load graph fact provenance rows."""
    return fetch_all(
        """
        SELECT id, subject, predicate, object, confidence, metadata, created_at
        FROM graph_facts
        ORDER BY created_at DESC
        """
    )


def generate_digital_twin() -> dict[str, Any]:
    """Generate a digital twin from inventory entities, relationships, and graph facts."""
    return build_topology(
        load_inventory_entities(),
        load_inventory_relationships(),
        load_graph_facts(),
    )
