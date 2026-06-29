"""Ollama HTTP client helpers."""

from app.core.config import settings
from app.core.logging import get_logger
from app.models.provider import get_model_provider

logger = get_logger(__name__)


def create_embedding(text: str) -> list[float]:
    """Create an embedding for text using the configured Ollama embedding model."""
    logger.info("Requesting Ollama embedding with model=%s", settings.embedding_model)
    return get_model_provider().embed(text, model=settings.embedding_model)


def generate(prompt: str) -> str:
    """Generate text using the configured Ollama model."""
    return get_model_provider().generate(prompt, model=settings.ollama_model)
