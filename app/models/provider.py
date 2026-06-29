"""Local model provider abstraction."""

from __future__ import annotations

import time
from typing import Any, Protocol

import requests

from app.core.config import settings
from app.core.correlation import (
    current_request_id,
    current_workflow_id,
    new_model_call_id,
)
from app.core.logging import get_logger
from app.core.metrics import observe_llm_call

_TIMEOUT_SECONDS = 120
logger = get_logger(__name__)


class ModelProvider(Protocol):
    def embed(self, text: str, model: str | None = None) -> list[float]: ...

    def generate(self, prompt: str, model: str | None = None) -> str: ...

    def list_models(self) -> list[dict[str, Any]]: ...


class OllamaProvider:
    """Ollama-backed local model provider."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.ollama_url).rstrip("/")

    def embed(self, text: str, model: str | None = None) -> list[float]:
        model_name = model or settings.embedding_model
        started = time.perf_counter()
        model_call_id = new_model_call_id()
        logger.info(
            "model_call_start request_id=%s workflow_id=%s model_call_id=%s operation=embedding model=%s",
            current_request_id(),
            current_workflow_id(),
            model_call_id,
            model_name,
        )
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model_name, "prompt": text},
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            duration_ms = (time.perf_counter() - started) * 1000
            observe_llm_call("embedding", model_name, duration_ms)
            logger.info(
                "model_call_complete request_id=%s workflow_id=%s model_call_id=%s operation=embedding model=%s duration_ms=%s",
                current_request_id(),
                current_workflow_id(),
                model_call_id,
                model_name,
                int(duration_ms),
            )
            return list(response.json()["embedding"])
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            observe_llm_call("embedding", model_name, duration_ms, error=True)
            logger.warning(
                "model_call_error request_id=%s workflow_id=%s model_call_id=%s operation=embedding model=%s duration_ms=%s",
                current_request_id(),
                current_workflow_id(),
                model_call_id,
                model_name,
                int(duration_ms),
            )
            raise

    def generate(self, prompt: str, model: str | None = None) -> str:
        model_name = model or settings.ollama_model
        started = time.perf_counter()
        model_call_id = new_model_call_id()
        logger.info(
            "model_call_start request_id=%s workflow_id=%s model_call_id=%s operation=generate model=%s",
            current_request_id(),
            current_workflow_id(),
            model_call_id,
            model_name,
        )
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model_name, "prompt": prompt, "stream": False},
                timeout=_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            duration_ms = (time.perf_counter() - started) * 1000
            observe_llm_call("generate", model_name, duration_ms)
            logger.info(
                "model_call_complete request_id=%s workflow_id=%s model_call_id=%s operation=generate model=%s duration_ms=%s",
                current_request_id(),
                current_workflow_id(),
                model_call_id,
                model_name,
                int(duration_ms),
            )
            return str(response.json()["response"])
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            observe_llm_call("generate", model_name, duration_ms, error=True)
            logger.warning(
                "model_call_error request_id=%s workflow_id=%s model_call_id=%s operation=generate model=%s duration_ms=%s",
                current_request_id(),
                current_workflow_id(),
                model_call_id,
                model_name,
                int(duration_ms),
            )
            raise

    def list_models(self) -> list[dict[str, Any]]:
        response = requests.get(f"{self.base_url}/api/tags", timeout=10)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model for model in models if isinstance(model, dict)]


def get_model_provider() -> ModelProvider:
    """Return the configured model provider."""
    return OllamaProvider()
