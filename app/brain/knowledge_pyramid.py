"""Knowledge pyramid orchestration stub."""

from __future__ import annotations

from typing import Any

_LEVELS = ("data", "information", "knowledge", "insight", "recommendation")


def build_knowledge_pyramid(context: dict[str, Any]) -> dict[str, Any]:
    """Arrange available context into DIKIR-style orchestration levels."""
    return {
        "levels": {
            "data": context.get("raw") or context.get("digital_twin") or {},
            "information": context.get("vector") or context.get("graph") or {},
            "knowledge": context.get("memory") or {},
            "insight": context.get("prediction") or {},
            "recommendation": context.get("recommendation") or None,
        },
        "level_order": list(_LEVELS),
        "execution": "disabled",
    }
