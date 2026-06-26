"""Connector registry and safe-by-default factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.core.config import settings
from app.security.audit import record_security_event

CLOUD_CONNECTOR_TYPES = {"aws", "azure"}

CONNECTOR_DEFINITIONS = {
    "aws": {"type": "aws", "category": "cloud", "mode": "read_only"},
    "azure": {"type": "azure", "category": "cloud", "mode": "read_only"},
    "kubernetes": {"type": "kubernetes", "category": "local_or_cluster", "mode": "read_only"},
    "terraform": {"type": "terraform", "category": "iac", "mode": "read_only"},
    "prometheus": {"type": "prometheus", "category": "observability", "mode": "read_only"},
}


class InventoryConnector(Protocol):
    connector_type: str

    def discover_inventory(self) -> list[dict]: ...


@dataclass(frozen=True)
class EmptyConnector:
    connector_type: str

    def discover_inventory(self) -> list[dict]:
        record_security_event(
            action="connector_sync",
            resource=f"connector:{self.connector_type}",
            decision="skipped",
            risk_level="low",
            metadata={"reason": "not_implemented"},
        )
        return []


class CloudConnectorsDisabledError(RuntimeError):
    """Raised when a cloud connector is used while the safety flag is off."""


def cloud_connectors_enabled() -> bool:
    return bool(getattr(settings, "enable_cloud_connectors", False))


def disabled_feature_message(connector_type: str) -> str:
    display = "AWS" if connector_type == "aws" else connector_type.title()
    return (
        f"{display} connector is disabled. Set "
        "PROJECTRAG_CLOUD_CONNECTORS_ENABLED=true only after credential, tenant, "
        "and audit controls are ready."
    )


def ensure_cloud_connector_enabled(connector_type: str) -> None:
    if connector_type in CLOUD_CONNECTOR_TYPES and not cloud_connectors_enabled():
        record_security_event(
            action="connector_access",
            resource=f"connector:{connector_type}",
            decision="denied",
            risk_level="medium",
            metadata={"reason": "cloud_connectors_disabled"},
        )
        raise CloudConnectorsDisabledError(disabled_feature_message(connector_type))


def connector_definition(connector_type: str) -> dict | None:
    return CONNECTOR_DEFINITIONS.get(connector_type)


def connector_enabled(connector_type: str) -> bool:
    return connector_type not in CLOUD_CONNECTOR_TYPES or cloud_connectors_enabled()


def connector_status(connector_type: str) -> str:
    if connector_type in CLOUD_CONNECTOR_TYPES and not cloud_connectors_enabled():
        return "dormant"
    return "planned"


def create_connector(connector_type: str) -> InventoryConnector:
    ensure_cloud_connector_enabled(connector_type)
    if connector_type == "aws":
        from app.connectors.aws.inventory import AWSInventoryConnector

        return AWSInventoryConnector()
    if connector_type == "azure":
        from app.connectors.azure.inventory import AzureInventoryConnector

        return AzureInventoryConnector()
    if connector_type in CONNECTOR_DEFINITIONS:
        return EmptyConnector(connector_type)
    raise KeyError(connector_type)
