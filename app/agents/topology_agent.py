"""Topology agent for graph traversal, dependency expansion, and impact analysis."""

from __future__ import annotations

import re

from app.graph.traversal import (
    get_dependencies,
    get_impact_path,
    get_neighbors,
    get_reverse_dependencies,
)
from app.graph.triple_builder import sanitize_entity

_STOP_WORDS = {
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
    "depends",
    "depend",
    "breaks",
    "fails",
    "services",
    "service",
    "use",
    "uses",
    "on",
    "if",
}


def _extract_entity(question: str) -> str:
    patterns = (
        r"\bwhat\s+depends\s+on\s+([A-Za-z0-9_.-]+)",
        r"\bwhat\s+breaks\s+if\s+([A-Za-z0-9_.-]+)\s+fails\b",
        r"\bwhich\s+services\s+use\s+([A-Za-z0-9_.-]+)",
        r"\bwhat\s+does\s+([A-Za-z0-9_.-]+)\s+depend\s+on\b",
    )
    for pattern in patterns:
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match:
            return sanitize_entity(match.group(1))
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_.-]*", question)
    candidates = [token for token in tokens if token.lower() not in _STOP_WORDS]
    return sanitize_entity(candidates[-1] if candidates else question)


def _intent(question: str) -> str:
    normalized = question.lower()
    if "breaks" in normalized or "fails" in normalized or "impact" in normalized:
        return "impact_analysis"
    if re.search(r"\bwhat\s+depends\s+on\b", normalized) or re.search(r"\bwhich\s+services\s+use\b", normalized):
        return "reverse_dependencies"
    if re.search(r"\bwhat\s+does\b.+\bdepend\s+on\b", normalized):
        return "dependencies"
    return "topology_explanation"


def run(state: dict) -> dict:
    question = str(state.get("question") or state.get("objective") or state.get("query") or "")
    entity = _extract_entity(question)
    intent = _intent(question)

    if intent == "impact_analysis":
        result = get_impact_path(entity)
        explanation = f"Impact analysis for {entity}; graph paths show potentially affected dependencies."
    elif intent == "reverse_dependencies":
        result = get_reverse_dependencies(entity)
        explanation = f"Reverse dependency expansion for {entity}; sources depend on or use this entity."
    elif intent == "dependencies":
        result = get_dependencies(entity)
        explanation = f"Dependency expansion for {entity}; targets are required by this entity."
    else:
        result = get_neighbors(entity)
        explanation = f"Topology explanation for {entity}; includes incoming and outgoing neighbors."

    topology_context = {
        "entity": entity,
        "intent": intent,
        "result": result,
        "explanation": explanation,
    }
    return {**state, "topology_context": topology_context}
