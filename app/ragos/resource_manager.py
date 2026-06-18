"""Local resource manager for capacity hints."""

from __future__ import annotations

from typing import Any

_LOCAL_LIMITS = {"ram_gb": 32, "storage_gb": 1024, "gpu_gb": 4}


def local_capacity() -> dict[str, int]:
    """Return local deployment capacity assumptions."""
    return dict(_LOCAL_LIMITS)


def estimate_request_resources(task_type: str, context_size: int = 0) -> dict[str, Any]:
    """Estimate local resources for a task without reserving anything."""
    normalized = str(task_type or "general").lower()
    size = max(0, int(context_size))
    ram_estimate = 1.0 + min(8.0, size / 10000)
    gpu_estimate = 0.5 if normalized in {"routing", "summarization"} else 2.0 if normalized == "validation" else 4.0
    return {
        "task_type": normalized,
        "estimated_ram_gb": round(ram_estimate, 3),
        "estimated_gpu_gb": gpu_estimate,
        "fits_local": ram_estimate <= _LOCAL_LIMITS["ram_gb"] and gpu_estimate <= _LOCAL_LIMITS["gpu_gb"],
        "execution": "advisory_only",
    }
