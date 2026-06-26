"""Infrastructure connector API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.connectors.registry import (
    CLOUD_CONNECTOR_TYPES,
    CloudConnectorsDisabledError,
    connector_definition,
    connector_enabled,
    connector_status,
    create_connector,
    disabled_feature_message,
)
from app.core.config import settings
from app.security.audit import record_security_event
from app.security.rbac import permission_dependency

router = APIRouter(prefix="/connectors", tags=["connectors"])


class ConnectorSyncRequest(BaseModel):
    dry_run: bool = True
    config: dict = Field(default_factory=dict)


def _cloud_connectors_enabled() -> bool:
    return bool(settings.enable_cloud_connectors)


def _connector(connector_type: str) -> dict:
    definition = connector_definition(connector_type)
    if definition is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    return {
        **definition,
        "status": connector_status(connector_type),
        "enabled": connector_enabled(connector_type),
    }


def _disabled_response(connector_type: str) -> dict:
    record_security_event(
        action="connector_access",
        resource=f"connector:{connector_type}",
        decision="denied",
        risk_level="medium",
        metadata={"reason": "cloud_connectors_disabled"},
    )
    return {
        "connector_type": connector_type,
        "status": "skipped",
        "reason": "cloud_connector_dormant",
        "error": "cloud_connectors_disabled",
        "message": disabled_feature_message(connector_type),
        "dry_run": True,
        "items": [],
    }


@router.get("", dependencies=[Depends(permission_dependency("read"))])
def list_connectors() -> dict:
    return {
        "cloud_connectors_enabled": _cloud_connectors_enabled(),
        "connectors": [
            _connector(connector_type)
            for connector_type in ["aws", "azure", "kubernetes", "terraform", "prometheus"]
        ],
    }


@router.get("/{connector_type}", dependencies=[Depends(permission_dependency("read"))])
def get_connector(connector_type: str) -> dict:
    return _connector(connector_type)


@router.post("/{connector_type}/test", dependencies=[Depends(permission_dependency("ingest"))])
def test_connector(connector_type: str, request: ConnectorSyncRequest | None = None) -> dict:
    connector = get_connector(connector_type)
    if connector_type in CLOUD_CONNECTOR_TYPES and not _cloud_connectors_enabled():
        return _disabled_response(connector_type)
    record_security_event(
        action="connector_test",
        resource=f"connector:{connector_type}",
        decision="allowed",
        risk_level="low",
        metadata={"dry_run": True},
    )
    return {"connector": connector, "status": "ok", "dry_run": True}


@router.post("/{connector_type}/sync", dependencies=[Depends(permission_dependency("ingest"))])
def sync_connector(connector_type: str, request: ConnectorSyncRequest) -> dict:
    get_connector(connector_type)
    if connector_type in CLOUD_CONNECTOR_TYPES and not _cloud_connectors_enabled():
        return _disabled_response(connector_type)

    try:
        inventory = create_connector(connector_type).discover_inventory()
    except CloudConnectorsDisabledError:
        return _disabled_response(connector_type)
    except KeyError:
        raise HTTPException(status_code=404, detail="Connector not found") from None
    except Exception as exc:
        record_security_event(
            action="connector_sync",
            resource=f"connector:{connector_type}",
            decision="failed",
            risk_level="medium",
            metadata={"reason": exc.__class__.__name__},
        )
        return {
            "connector_type": connector_type,
            "status": "failed",
            "error": "connector_sync_failed",
            "message": "Connector sync failed gracefully; check audit logs for details.",
            "dry_run": request.dry_run,
            "items": [],
        }
    return {"connector_type": connector_type, "status": "completed", "dry_run": request.dry_run, "items": inventory}
