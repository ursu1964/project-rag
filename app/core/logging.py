"""Application logging helpers."""

from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import settings


@lru_cache(maxsize=128)
def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, str(settings.log_level).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return logging.getLogger(name)
