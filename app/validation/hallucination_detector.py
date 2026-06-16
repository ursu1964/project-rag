"""Deterministic hallucination checks for grounded answers."""

from __future__ import annotations

import re
from typing import Any

from app.graph.ontology import RELATION_TYPES


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"\b[A-Z][A-Za-z0-9_]*\b", text)}


def _relations(text: str) -> set[str]:
    return {relation for relation in RELATION_TYPES if relation in text}


def _evidence_text(*evidence_parts: Any) -> str:
    return " ".join(str(part) for part in evidence_parts if part)


def detect_hallucinations(
    answer: str,
    retrieved_evidence: list[dict] | None = None,
    graph_evidence: list[dict] | dict | None = None,
    memory_evidence: list[dict] | None = None,
) -> dict[str, Any]:
    """Detect unsupported entities, relationships, and claims.

    Returns a confidence score where 1.0 means no unsupported items were found.
    """
    evidence_text = _evidence_text(retrieved_evidence or [], graph_evidence or [], memory_evidence or [])
    answer_entities = _tokens(answer)
    evidence_entities = _tokens(evidence_text)
    answer_relationships = _relations(answer)
    evidence_relationships = _relations(evidence_text)

    unsupported_entities = sorted(answer_entities - evidence_entities)
    unsupported_relationships = sorted(answer_relationships - evidence_relationships)

    unsupported_claims: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", answer.strip()):
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_terms = {term.lower() for term in re.findall(r"[A-Za-z0-9_]+", sentence) if len(term) > 3}
        evidence_terms = {term.lower() for term in re.findall(r"[A-Za-z0-9_]+", evidence_text) if len(term) > 3}
        if sentence_terms and not sentence_terms.intersection(evidence_terms):
            unsupported_claims.append(sentence)

    issue_count = len(unsupported_entities) + len(unsupported_relationships) + len(unsupported_claims)
    confidence = max(0.0, round(1.0 - min(issue_count, 10) / 10, 3))
    return {
        "unsupported_entities": unsupported_entities,
        "unsupported_relationships": unsupported_relationships,
        "unsupported_claims": unsupported_claims,
        "confidence": confidence,
    }
