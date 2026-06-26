"""Simple relationship extraction and GraphDB ingestion."""

from __future__ import annotations

import re
from typing import Any

from app.graph.graphdb_client import insert_turtle
from app.graph.triple_builder import build_triple, build_turtle
from app.memory.graph_fact_store import store_graph_fact

_REL_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b([A-Za-z0-9_.-]+)\s+depends\s+on\s+([A-Za-z0-9_.-]+)", re.I), "dependsOn"),
    (re.compile(r"\b([A-Za-z0-9_.-]+)\s+is\s+connected\s+to\s+([A-Za-z0-9_.-]+)", re.I), "connectedTo"),
    (re.compile(r"\b([A-Za-z0-9_.-]+)\s+uses\s+([A-Za-z0-9_.-]+)", re.I), "uses"),
    (re.compile(r"\b([A-Za-z0-9_.-]+)\s+calls\s+([A-Za-z0-9_.-]+)", re.I), "calls"),
    (re.compile(r"\b([A-Za-z0-9_.-]+)\s+runs\s+on\s+([A-Za-z0-9_.-]+)", re.I), "runsOn"),
    (re.compile(r"\b([A-Za-z0-9_.-]+)\s+belongs\s+to\s+([A-Za-z0-9_.-]+)", re.I), "belongsTo"),
    (re.compile(r"\b([A-Za-z0-9_.-]+)\s+is\s+protected\s+by\s+([A-Za-z0-9_.-]+)", re.I), "protectedBy"),
)


def extract_relationships(text: str) -> list[dict[str, str]]:
    facts: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for pattern, predicate in _REL_PATTERNS:
        for match in pattern.finditer(text):
            subject, obj = match.group(1), match.group(2).rstrip(".,;")
            key = (subject, predicate, obj)
            if key in seen:
                continue
            seen.add(key)
            facts.append({"subject": subject, "predicate": predicate, "object": obj})
    return facts


def ingest_graph_from_text(text: str, source_document_id: str | None = None, source_chunk_id: str | None = None) -> dict[str, Any]:
    facts = extract_relationships(text)
    triples = []
    for fact in facts:
        store_graph_fact(
            fact["subject"],
            fact["predicate"],
            fact["object"],
            source_document_id=source_document_id,
            source_chunk_id=source_chunk_id,
            metadata={"source": "graph_ingestion"},
        )
        triples.append(build_triple(fact["subject"], fact["predicate"], fact["object"]))
    if triples:
        insert_turtle(build_turtle(triples))
    return {"status": "ingested", "facts": facts, "triple_count": len(triples)}
