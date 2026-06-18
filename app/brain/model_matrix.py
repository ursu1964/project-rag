"""Model allocation matrix orchestration stub."""

from __future__ import annotations

from typing import Any

_DEFAULT_MATRIX = {
    "routing": "small",
    "summarization": "small",
    "validation": "medium",
    "reasoning": "large",
    "prediction": "medium",
}


def get_model_matrix(overrides: dict[str, str] | None = None) -> dict[str, Any]:
    """Return the current model role matrix without loading or executing models."""
    matrix = {**_DEFAULT_MATRIX, **(overrides or {})}
    return {
        "matrix": matrix,
        "execution": "disabled",
        "note": "Orchestration stub only; model dispatch is not performed here.",
    }
