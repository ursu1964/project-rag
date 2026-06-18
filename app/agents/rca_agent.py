"""Root-cause analysis agent using incident symptoms and graph dependencies."""

from __future__ import annotations

import re
from typing import Any

from app.graph.traversal import get_dependencies, get_neighbors, get_reverse_dependencies
from app.graph.triple_builder import sanitize_entity

_STOP_WORDS = {
    "incident",
    "symptom",
    "symptoms",
    "root",
    "cause",
    "causes",
    "down",
    "failed",
    "failure",
    "error",
    "errors",
    "latency",
    "slow",
    "outage",
    "service",
    "is",
    "the",
    "a",
    "an",
    "on",
    "in",
}


def _symptoms(state: dict[str, Any]) -> list[str]:
    value = state.get("symptoms") or state.get("incident_symptoms")
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value or state.get("question") or state.get("objective") or "")
    return [part.strip() for part in re.split(r"[.;\n]+", text) if part.strip()]


def _candidate_entities(symptoms: list[str], state: dict[str, Any]) -> list[str]:
    explicit = state.get("entity") or state.get("target_entity")
    candidates: list[str] = [sanitize_entity(str(explicit))] if explicit else []
    for symptom in symptoms:
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9_.-]*", symptom)
        for token in tokens:
            if token.lower() not in _STOP_WORDS:
                candidates.append(sanitize_entity(token))
    seen: set[str] = set()
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            unique.append(candidate)
    return unique[:8]


def _score_candidate(entity: str, dependencies: list[dict[str, Any]], reverse: list[dict[str, Any]]) -> float:
    dependency_weight = min(len(dependencies) * 0.15, 0.45)
    reverse_weight = min(len(reverse) * 0.2, 0.4)
    return min(0.95, round(0.2 + dependency_weight + reverse_weight, 3))


def run(state: dict) -> dict:
    """Analyze symptoms and propose probable graph-based root causes."""
    symptoms = _symptoms(state)
    candidates = _candidate_entities(symptoms, state)
    probable_causes: list[dict[str, Any]] = []
    warnings: list[str] = []

    for entity in candidates:
        try:
            dependencies = list(get_dependencies(entity).get("dependencies", []))
            reverse = list(get_reverse_dependencies(entity).get("reverse_dependencies", []))
            neighbors = get_neighbors(entity).get("neighbors", {})
        except Exception as exc:  # pragma: no cover - external GraphDB failures vary
            warnings.append(f"graph lookup failed for {entity}: {exc.__class__.__name__}")
            dependencies = []
            reverse = []
            neighbors = {}

        if dependencies or reverse or entity == candidates[0]:
            probable_causes.append(
                {
                    "entity": entity,
                    "confidence": _score_candidate(entity, dependencies, reverse),
                    "evidence": {
                        "dependencies": dependencies,
                        "reverse_dependencies": reverse,
                        "neighbors": neighbors,
                    },
                    "reason": "Entity appears in symptoms and has graph dependency evidence.",
                }
            )

    probable_causes.sort(key=lambda item: item["confidence"], reverse=True)
    confidence = float(probable_causes[0]["confidence"]) if probable_causes else 0.0
    rca_context = {
        "symptoms": symptoms,
        "candidate_entities": candidates,
        "probable_root_causes": probable_causes[:5],
        "confidence": confidence,
        "warnings": warnings,
    }
    return {**state, "rca_context": rca_context}
