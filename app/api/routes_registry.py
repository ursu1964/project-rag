"""AIOS registry discovery routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.agents.registry import list_agents
from app.security.rbac import permission_dependency
from app.workflows.registry import list_workflows

router = APIRouter(prefix="/registry", tags=["registry"])


@router.get("/agents", dependencies=[Depends(permission_dependency("read"))])
def agents() -> list[dict[str, Any]]:
    return list_agents()


@router.get("/workflows", dependencies=[Depends(permission_dependency("read"))])
def workflows() -> list[dict[str, Any]]:
    return list_workflows()


@router.get("", dependencies=[Depends(permission_dependency("read"))])
def registry() -> dict[str, Any]:
    return {"agents": list_agents(), "workflows": list_workflows()}
