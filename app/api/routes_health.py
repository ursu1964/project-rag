"""Health check routes."""

from __future__ import annotations

import requests
from fastapi import APIRouter, Response

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import CONTENT_TYPE_LATEST, REQUEST_COUNTER, render_metrics
from app.core.schemas import HealthResponse
from app.memory.postgres import get_connection

router = APIRouter()
logger = get_logger(__name__)
_TIMEOUT_SECONDS = 5


@router.get("/health", response_model=HealthResponse, response_model_exclude_none=True)
@router.get("/health/live", response_model=HealthResponse, response_model_exclude_none=True)
def health() -> dict[str, str]:
    """Basic application status."""
    return {"status": "ok", "service": "ProjectRAG"}


def _check_postgres() -> tuple[str, str | None]:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        return "ok", None
    except Exception as exc:  # pragma: no cover - exact driver errors vary
        logger.warning("PostgreSQL health check failed: %s", exc.__class__.__name__)
        return "failed", str(exc)


def _check_graphdb() -> tuple[str, str | None]:
    try:
        response = requests.get(f"{settings.graphdb_url.rstrip('/')}/rest/repositories", timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        return "ok", None
    except Exception as exc:  # pragma: no cover - network failures vary
        logger.warning("GraphDB health check failed: %s", exc.__class__.__name__)
        return "failed", str(exc)


def _check_ollama() -> tuple[str, str | None]:
    try:
        response = requests.get(f"{settings.ollama_url.rstrip('/')}/api/tags", timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        return "ok", None
    except Exception as exc:  # pragma: no cover - network failures vary
        logger.warning("Ollama health check failed: %s", exc.__class__.__name__)
        return "failed", str(exc)


@router.get("/health/deep", response_model=HealthResponse, response_model_exclude_none=True)
def deep_health() -> dict[str, object]:
    """Check application dependencies without raising on failures."""
    checks = {
        "postgres": _check_postgres(),
        "graphdb": _check_graphdb(),
        "ollama": _check_ollama(),
    }
    statuses = {name: result[0] for name, result in checks.items()}
    errors = {name: result[1] for name, result in checks.items() if result[1]}

    failed_count = sum(1 for status in statuses.values() if status == "failed")
    if failed_count == 0:
        status = "ok"
    elif failed_count == len(statuses):
        status = "failed"
    else:
        status = "degraded"

    response: dict[str, object] = {"status": status, **statuses}
    if errors:
        response["errors"] = errors
    return response


@router.get("/metrics")
def metrics() -> Response:
    REQUEST_COUNTER.labels("/metrics").inc()
    return Response(content=render_metrics(), media_type=CONTENT_TYPE_LATEST)
