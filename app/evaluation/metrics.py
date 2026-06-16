"""Deterministic MVP evaluation metrics."""

from __future__ import annotations

import re
from typing import Any


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z0-9_]+", text) if len(token) > 2}


def groundedness(answer: str, evidence: dict[str, Any] | list[Any]) -> float:
    evidence_text = str(evidence)
    answer_terms = _tokens(answer)
    if not answer_terms:
        return 0.0
    evidence_terms = _tokens(evidence_text)
    return round(len(answer_terms & evidence_terms) / len(answer_terms), 3)


def answer_completeness(answer: str, expected_answer: str = "") -> float:
    if not answer.strip():
        return 0.0
    if not expected_answer.strip():
        return 0.5
    expected_terms = _tokens(expected_answer)
    if not expected_terms:
        return 0.5
    return round(len(_tokens(answer) & expected_terms) / len(expected_terms), 3)


def graph_usage(evidence: dict[str, Any] | list[Any]) -> float:
    if isinstance(evidence, dict):
        graph = evidence.get("graph") or evidence.get("graph_context") or []
        return 1.0 if graph else 0.0
    return 0.0


def hallucination_rate(answer: str, evidence: dict[str, Any] | list[Any]) -> float:
    return round(1.0 - groundedness(answer, evidence), 3)


def citation_coverage(answer: str) -> float:
    if not answer.strip():
        return 0.0
    citation_markers = ("Evidence Used:", "Vector evidence", "Graph evidence", "Memory evidence")
    present = sum(1 for marker in citation_markers if marker.lower() in answer.lower())
    return round(present / len(citation_markers), 3)


def evaluate_answer(answer: str, evidence: dict[str, Any] | list[Any], expected_answer: str = "") -> dict[str, float]:
    return {
        "groundedness": groundedness(answer, evidence),
        "answer_completeness": answer_completeness(answer, expected_answer),
        "graph_usage": graph_usage(evidence),
        "hallucination_rate": hallucination_rate(answer, evidence),
        "citation_coverage": citation_coverage(answer),
    }
