"""Ollama HTTP client helpers."""

import requests

from app.core.config import settings
from app.core.logging import get_logger

_TIMEOUT_SECONDS = 120
logger = get_logger(__name__)


def create_embedding(text: str) -> list[float]:
    """Create an embedding for text using the configured Ollama embedding model."""
    logger.info("Requesting Ollama embedding with model=%s", settings.embedding_model)
    logger.info("Requesting Ollama generation with model=%s", settings.ollama_model)
    response = requests.post(
        f"{settings.ollama_url.rstrip('/')}/api/embeddings",
        json={"model": settings.embedding_model, "prompt": text},
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return list(response.json()["embedding"])


def generate(prompt: str) -> str:
    """Generate text using the configured Ollama model."""
    response = requests.post(
        f"{settings.ollama_url.rstrip('/')}/api/generate",
        json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return str(response.json()["response"])
