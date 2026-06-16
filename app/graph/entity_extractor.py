"""Deterministic entity extraction for infrastructure GraphRAG."""

from __future__ import annotations

import re

_STOP_ENTITY_NAMES = {"on", "to", "from", "by", "the", "a", "an", "uses", "calls", "reads", "writes", "depends"}

_ENTITY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("VM", (r"\b(?:vm|virtual machine)\s+([A-Za-z0-9_.-]+)", r"\b([A-Za-z0-9_.-]+)\s+(?:vm|virtual machine)\b")),
    ("Database", (r"\b(?:database|db)\s+([A-Za-z0-9_.-]+)", r"\b([A-Za-z0-9_.-]+)\s+(?:database|db)\b")),
    ("Subnet", (r"\bsubnet\s+([A-Za-z0-9_.-]+)", r"\b([A-Za-z0-9_.-]+)\s+subnet\b")),
    ("Firewall", (r"\bfirewall\s+([A-Za-z0-9_.-]+)", r"\b([A-Za-z0-9_.-]+)\s+firewall\b")),
    ("VNet", (r"\b(?:vnet|virtual network)\s+([A-Za-z0-9_.-]+)", r"\b([A-Za-z0-9_.-]+)\s+(?:vnet|virtual network)\b")),
    ("Service", (r"\bservice\s+([A-Za-z0-9_.-]+)", r"\b([A-Za-z0-9_.-]+)\s+service\b")),
    ("API", (r"\bapi\s+([A-Za-z0-9_.-]+)", r"\b([A-Za-z0-9_.-]+)\s+api\b")),
)


def extract_entities(text: str) -> list[dict[str, str]]:
    """Extract known infrastructure entities using deterministic regex patterns."""
    entities: dict[tuple[str, str], dict[str, str]] = {}
    for entity_type, patterns in _ENTITY_PATTERNS:
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                name = match.group(1).strip(" .,:;()[]{}\n\t")
                if not name or name.lower() in _STOP_ENTITY_NAMES:
                    continue
                key = (name.lower(), entity_type)
                entities[key] = {"name": name, "type": entity_type}
    return list(entities.values())
