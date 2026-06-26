"""Optional telemetry setup."""

from __future__ import annotations

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_telemetry(app: FastAPI) -> None:
    if not settings.otel_enabled:
        return
    try:  # pragma: no cover - optional dependency path
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
    except Exception as exc:  # pragma: no cover
        logger.warning("otel_setup_failed reason=%s", exc.__class__.__name__)
