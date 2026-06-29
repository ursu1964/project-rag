"""OpenAI-compatible local API routes backed by AIOS providers."""

from __future__ import annotations

import time
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.provider import get_model_provider
from app.security.rbac import permission_dependency

router = APIRouter(prefix="/v1", tags=["openai-compatible"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(min_length=1)
    temperature: float | None = None
    stream: bool = False


class EmbeddingRequest(BaseModel):
    input: str | list[str]
    model: str | None = None
    encoding_format: Literal["float"] = "float"


def _messages_to_prompt(messages: list[ChatMessage]) -> str:
    return "\n".join(f"{message.role}: {message.content}" for message in messages)


def _model_card(model_id: str) -> dict[str, Any]:
    return {"id": model_id, "object": "model", "created": 0, "owned_by": "local"}


@router.get("/models", dependencies=[Depends(permission_dependency("read"))])
def list_models() -> dict[str, Any]:
    provider = get_model_provider()
    seen: set[str] = set()
    data: list[dict[str, Any]] = []
    for model in provider.list_models():
        model_id = str(model.get("name") or model.get("model") or "").strip()
        if model_id and model_id not in seen:
            seen.add(model_id)
            data.append(_model_card(model_id))
    for model_id in (settings.ollama_model, settings.embedding_model):
        if model_id not in seen:
            data.append(_model_card(model_id))
            seen.add(model_id)
    return {"object": "list", "data": data}


@router.post(
    "/chat/completions", dependencies=[Depends(permission_dependency("query"))]
)
def chat_completions(request: ChatCompletionRequest) -> dict[str, Any]:
    if request.stream:
        # Minimal compatibility surface: non-streaming first.
        raise HTTPException(
            status_code=400,
            detail="stream=true is not supported by the local compatibility endpoint yet",
        )
    model = request.model or settings.ollama_model
    content = get_model_provider().generate(
        _messages_to_prompt(request.messages), model=model
    )
    now = int(time.time())
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": now,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


@router.post("/embeddings", dependencies=[Depends(permission_dependency("query"))])
def embeddings(request: EmbeddingRequest) -> dict[str, Any]:
    model = request.model or settings.embedding_model
    inputs = request.input if isinstance(request.input, list) else [request.input]
    data = [
        {
            "object": "embedding",
            "index": index,
            "embedding": get_model_provider().embed(text, model=model),
        }
        for index, text in enumerate(inputs)
    ]
    return {
        "object": "list",
        "model": model,
        "data": data,
        "usage": {"prompt_tokens": 0, "total_tokens": 0},
    }
