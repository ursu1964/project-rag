"""Application logging helpers."""

from __future__ import annotations

import logging

from app.core.config import settings

_LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s %(message)s"
_CONFIGURED = False


def _configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(level=level, format=_LOG_FORMAT)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger.

    Callers should log operational metadata only and must not include secrets,
    credentials, prompts, or raw document content in log messages.
    """
    _configure_logging()
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    return logger
