"""Artificial Architect advisory stub.

Future purpose: recommend architecture patterns, dependency boundaries, topology
improvements, and migration paths. This module is recommendation-only and does
not approve or execute changes.
"""

from __future__ import annotations

from typing import Any


def recommend_architecture(context: dict[str, Any]) -> dict[str, Any]:
    """Return recommendation-only architecture guidance."""
    return {
        "role": "artificial_architect",
        "mode": "recommendation_only",
        "recommendation": "Assess architecture context and suggest improvements; no autonomous decision made.",
        "context_keys": sorted(context.keys()),
        "execution": "disabled",
    }
