"""Supported infrastructure entity types for discovery and digital twin data."""

ENTITY_TYPES = {
    "DockerContainer",
    "VM",
    "Host",
    "Network",
    "Subnet",
    "Database",
    "Service",
    "API",
    "Cluster",
    "Namespace",
    "Pod",
}


def is_supported_entity_type(entity_type: str) -> bool:
    """Return whether an entity type is supported."""
    return entity_type in ENTITY_TYPES
