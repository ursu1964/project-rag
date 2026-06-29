"""Request/workflow/model correlation context helpers."""

from __future__ import annotations

import uuid
from contextvars import ContextVar, Token

_request_id: ContextVar[str] = ContextVar("request_id", default="")
_workflow_id: ContextVar[str] = ContextVar("workflow_id", default="")


def set_request_id(request_id: str) -> Token[str]:
    return _request_id.set(str(request_id or ""))


def reset_request_id(token: Token[str]) -> None:
    _request_id.reset(token)


def current_request_id() -> str:
    return _request_id.get()


def set_workflow_id(workflow_id: str) -> Token[str]:
    return _workflow_id.set(str(workflow_id or ""))


def reset_workflow_id(token: Token[str]) -> None:
    _workflow_id.reset(token)


def current_workflow_id() -> str:
    return _workflow_id.get()


def new_model_call_id() -> str:
    return str(uuid.uuid4())
