"""Ollama HTTP client helpers."""

import time

import requests

from app.core.config import settings
from app.core.logging import get_logger
from app.core.metrics import observe_llm_call

_TIMEOUT_SECONDS = 120
logger = get_logger(__name__)


def create_embedding(text: str) -> list[float]:
    """Create an embedding for text using the configured Ollama embedding model."""
    logger.info("Requesting Ollama embedding with model=%s", settings.embedding_model)
    started = time.perf_counter()
    try:
        response = requests.post(
            f"{settings.ollama_url.rstrip('/')}/api/embeddings",
            json={"model": settings.embedding_model, "prompt": text},
            timeout=_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        observe_llm_call("embedding", settings.embedding_model, (time.perf_counter() - started) * 1000)
        return list(response.json()["embedding"])
    except Exception:
        observe_llm_call(
            "embedding",
            settings.embedding_model,
            (time.perf_counter() - started) * 1000,
            error=True,
        )
        raise


def generate(prompt: str) -> str:
    """Generate text using the configured Ollama model."""
    started = time.perf_counter()
    try:
        response = requests.post(
            f"{settings.ollama_url.rstrip('/')}/api/generate",
            json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            timeout=_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        observe_llm_call("generate", settings.ollama_model, (time.perf_counter() - started) * 1000)
        return str(response.json()["response"])
    except Exception:
        observe_llm_call(
            "generate",
            settings.ollama_model,
            (time.perf_counter() - started) * 1000,
            error=True,
        )
        raise
