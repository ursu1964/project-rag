"""Read-only Docker discovery and inventory persistence."""

from __future__ import annotations

import json
import re
import socket
import subprocess
from typing import Any

from app.graph.graphdb_client import insert_turtle
from app.graph.triple_builder import build_triple, build_turtle, sanitize_entity
from app.memory.postgres import get_connection

_DOCKER_TIMEOUT_SECONDS = 30


def _run_docker(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a read-only Docker command with explicit arguments only."""
    return subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=_DOCKER_TIMEOUT_SECONDS,
    )


def _health_from_status(status: str) -> str:
    normalized = status.lower()
    if "healthy" in normalized and "unhealthy" not in normalized:
        return "healthy"
    if "unhealthy" in normalized:
        return "unhealthy"
    if normalized.startswith("up"):
        return "running"
    if "exited" in normalized:
        return "exited"
    return "unknown"


def _split_networks(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def _extract_ports(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def discover_containers() -> list[dict[str, Any]]:
    """Discover Docker containers using read-only `docker ps`."""
    result = _run_docker(["ps", "--all", "--format", "{{json .}}"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "docker ps failed")

    containers: list[dict[str, Any]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        containers.append(
            {
                "id": item.get("ID"),
                "name": item.get("Names") or item.get("Name") or item.get("ID"),
                "image": item.get("Image"),
                "ports": _extract_ports(item.get("Ports", "")),
                "networks": _split_networks(item.get("Networks", "")),
                "status": item.get("Status"),
                "health_status": _health_from_status(str(item.get("Status") or "")),
                "raw": item,
            }
        )
    return containers


def _safe_entity_name(prefix: str, value: str) -> str:
    clean = sanitize_entity(value)
    return f"{prefix}_{clean}" if not clean.startswith(prefix) else clean


def docker_inventory() -> dict[str, Any]:
    """Return normalized Docker inventory entities and relationships."""
    host = socket.gethostname()
    containers = discover_containers()
    entities: list[dict[str, Any]] = [
        {"name": host, "entity_type": "Host", "metadata": {"source": "docker"}}
    ]
    relationships: list[dict[str, Any]] = []
    seen_entities = {(host, "Host")}

    def add_entity(name: str, entity_type: str, metadata: dict[str, Any] | None = None) -> None:
        key = (name, entity_type)
        if key not in seen_entities:
            seen_entities.add(key)
            entities.append({"name": name, "entity_type": entity_type, "metadata": metadata or {}})

    for container in containers:
        container_name = _safe_entity_name("DockerContainer", str(container["name"]))
        add_entity(
            container_name,
            "DockerContainer",
            {
                "docker_id": container.get("id"),
                "image": container.get("image"),
                "ports": container.get("ports", []),
                "status": container.get("status"),
                "health_status": container.get("health_status"),
            },
        )
        relationships.append({"source": container_name, "relationship": "runsOn", "target": host})

        if container.get("image"):
            image_name = _safe_entity_name("Service", re.sub(r"[:/@.-]+", "_", str(container["image"])))
            add_entity(image_name, "Service", {"kind": "DockerImage", "image": container["image"]})
            relationships.append({"source": container_name, "relationship": "uses", "target": image_name})

        for network in container.get("networks", []):
            network_name = _safe_entity_name("Network", network)
            add_entity(network_name, "Network", {"kind": "DockerNetwork"})
            relationships.append({"source": container_name, "relationship": "connectedTo", "target": network_name})

    return {"source": "docker", "entities": entities, "relationships": relationships}


def _create_discovery_run(source: str, metadata: dict[str, Any]) -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO discovery_runs (source, status, metadata)
                VALUES (%s, %s, %s::jsonb)
                RETURNING id
                """,
                (source, "completed", json.dumps(metadata)),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def _store_entity(discovery_run_id: str, entity: dict[str, Any]) -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO inventory_entities (
                    discovery_run_id, entity_name, entity_type, provider, region, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                RETURNING id
                """,
                (
                    discovery_run_id,
                    entity["name"],
                    entity["entity_type"],
                    entity.get("provider", "local"),
                    entity.get("region"),
                    json.dumps(entity.get("metadata") or {}),
                ),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def _store_relationship(
    discovery_run_id: str,
    relationship: dict[str, Any],
    entity_ids: dict[str, str],
) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO inventory_relationships (
                    discovery_run_id, source_entity_id, target_entity_id,
                    source_entity_name, relationship, target_entity_name, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                """,
                (
                    discovery_run_id,
                    entity_ids.get(relationship["source"]),
                    entity_ids.get(relationship["target"]),
                    relationship["source"],
                    relationship["relationship"],
                    relationship["target"],
                    json.dumps(relationship.get("metadata") or {}),
                ),
            )
        connection.commit()


def _insert_graph_triples(inventory: dict[str, Any]) -> int:
    triples: list[str] = []
    for entity in inventory["entities"]:
        triples.append(build_triple(entity["name"], "type", entity["entity_type"]))
    for relationship in inventory["relationships"]:
        triples.append(
            build_triple(
                relationship["source"],
                relationship["relationship"],
                relationship["target"],
            )
        )
    if triples:
        insert_turtle(build_turtle(triples))
    return len(triples)


def persist_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    """Persist normalized inventory to PostgreSQL and GraphDB."""
    discovery_run_id = _create_discovery_run(
        str(inventory.get("source", "docker")),
        {"entity_count": len(inventory.get("entities", [])), "relationship_count": len(inventory.get("relationships", []))},
    )
    entity_ids = {
        entity["name"]: _store_entity(discovery_run_id, entity)
        for entity in inventory.get("entities", [])
    }
    for relationship in inventory.get("relationships", []):
        _store_relationship(discovery_run_id, relationship, entity_ids)
    triple_count = _insert_graph_triples(inventory)
    return {
        "discovery_run_id": discovery_run_id,
        "entities": len(entity_ids),
        "relationships": len(inventory.get("relationships", [])),
        "triples": triple_count,
    }


def discover_and_persist() -> dict[str, Any]:
    """Run read-only Docker discovery and persist results."""
    inventory = docker_inventory()
    persisted = persist_inventory(inventory)
    return {"inventory": inventory, "persisted": persisted}
