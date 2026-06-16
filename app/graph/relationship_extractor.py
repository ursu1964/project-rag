"""Deterministic relationship extraction for GraphRAG."""

from __future__ import annotations

import re

_RELATION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("dependsOn", "depends on"),
    ("connectedTo", "is connected to"),
    ("uses", "uses"),
    ("protectedBy", "is protected by"),
    ("runsOn", "runs on"),
    ("belongsTo", "belongs to"),
    ("calls", "calls"),
    ("readsFrom", "reads from"),
    ("writesTo", "writes to"),
)

_BOUNDARY = r"(?=\s*(?:[.;,]|\band\b|\n|$))"
_ARTICLES = re.compile(r"^(?:the|a|an)\s+", flags=re.IGNORECASE)
_ENTITY_PREFIX = re.compile(r"^(?:vm|virtual machine|database|db|subnet|firewall|vnet|virtual network|service|api)\s+", flags=re.IGNORECASE)


def _clean_entity(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" .,:;()[]{}\n\t")
    value = _ARTICLES.sub("", value)
    value = _ENTITY_PREFIX.sub("", value)
    return value.strip()


def extract_relationships(text: str) -> list[dict[str, str]]:
    """Extract supported subject-predicate-object relationships."""
    relationships: list[dict[str, str]] = []
    for predicate, phrase in _RELATION_PATTERNS:
        pattern = rf"([A-Za-z0-9_.-][A-Za-z0-9_.\- ]*?)\s+{re.escape(phrase)}\s+([A-Za-z0-9_.-][A-Za-z0-9_.\- ]*?){_BOUNDARY}"
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            subject = _clean_entity(match.group(1))
            obj = _clean_entity(match.group(2))
            if subject and obj:
                relationships.append({"subject": subject, "predicate": predicate, "object": obj})
    return relationships
