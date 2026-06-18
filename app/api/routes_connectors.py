"""Infrastructure connector API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.connectors.aws.inventory import discover_inventory as discover_aws_inventory
from app.connectors.azure.inventory import discover_inventory as discover_azure_inventory
from app.core.config import settings

router = APIRouter(prefix="/connectors", tags=["connectors"])

_CONNECTOR_DEFINITIONS = {
    "aws": {"type": "aws", "category": "cloud", "mode": "read_only"},
    "azure": {"type": "azure", "category": "cloud", "mode": "read_only"},
    "kubernetes": {"type": "kubernetes", "category": "local_or_cluster", "mode": "read_only"},
    "terraform": {"type": "terraform", "category": "iac", "mode": "read_only"},
    "prometheus": {"type": "prometheus", "category": "observability", "mode": "read_only"},
}


def _connector_status(connector_type: str) -> str:
    if connector_type in {"aws", "azure"} and not settings.enable_cloud_connectors:
        return "dormant"
    return "planned"


def _connector(connector_type: str) -> dict:
    definition = _CONNECTOR_DEFINITIONS.get(connector_type)
    if definition is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    return {
        **definition,
        "status": _connector_status(connector_type),
        "enabled": connector_type not in {"aws", "azure"} or settings.enable_cloud_connectors,
    }


_CONNECTORS = {
    "aws": {"type": "aws", "status": "dormant", "mode": "read_only"},
    "azure": {"type": "azure", "status": "dormant", "mode": "read_only"},
    "kubernetes": {"type": "kubernetes", "status": "planned", "mode": "read_only"},
    "terraform": {"type": "terraform", "status": "planned", "mode": "read_only"},
    "prometheus": {"type": "prometheus", "status": "planned", "mode": "read_only"},
}


class ConnectorSyncRequest(BaseModel):
    dry_run: bool = True
    config: dict = Field(default_factory=dict)


@router.get("")
def list_connectors() -> dict:
    return {
        "cloud_connectors_enabled": settings.enable_cloud_connectors,
        "connectors": [_connector(connector_type) for connector_type in _CONNECTOR_DEFINITIONS],
    }


@router.get("/{connector_type}")
def get_connector(connector_type: str) -> dict:
    return _connector(connector_type)


@router.post("/{connector_type}/test")
def test_connector(connector_type: str, request: ConnectorSyncRequest | None = None) -> dict:
    connector = get_connector(connector_type)
    return {"connector": connector, "status": "ok", "dry_run": True}


@router.post("/{connector_type}/sync")
def sync_connector(connector_type: str, request: ConnectorSyncRequest) -> dict:
    connector = get_connector(connector_type)
    if connector["status"] == "dormant":
        return {
            "connector_type": connector_type,
            "status": "skipped",
            "reason": "cloud_connector_dormant",
            "message": "Set ENABLE_CLOUD_CONNECTORS=true only after credential, tenant, and audit controls are ready.",
            "dry_run": True,
            "items": [],
        }

    if connector_type == "aws":
        inventory = discover_aws_inventory()
    elif connector_type == "azure":
        inventory = discover_azure_inventory()
    elif connector_type in _CONNECTORS:
        inventory = []
    else:
        raise HTTPException(status_code=404, detail="Connector not found")
    return {"connector_type": connector_type, "status": "completed", "dry_run": request.dry_run, "items": inventory}
