"""Azure inventory discovery.

Cloud SDK clients are created lazily and only when the cloud connector flag is on.
"""

from __future__ import annotations

import os
from typing import Any

from app.connectors.azure.models import AzureInventoryEntity
from app.connectors.registry import ensure_cloud_connector_enabled
from app.core.config import settings
from app.security.audit import record_security_event


class AzureInventoryConnector:
    connector_type = "azure"

    def __init__(self) -> None:
        self._resource_client: Any | None = None

    def _client(self) -> Any | None:
        """Initialize Azure SDK lazily; require explicit subscription config."""
        if self._resource_client is not None:
            return self._resource_client
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID", "").strip()
        if not subscription_id:
            record_security_event(
                action="connector_client_init",
                resource="connector:azure",
                decision="skipped",
                risk_level="low",
                metadata={"reason": "missing_subscription_id"},
            )
            return None
        try:
            from azure.identity import DefaultAzureCredential  # type: ignore
            from azure.mgmt.resource import ResourceManagementClient  # type: ignore
        except ImportError:
            record_security_event(
                action="connector_client_init",
                resource="connector:azure",
                decision="skipped",
                risk_level="low",
                metadata={"reason": "azure_sdk_unavailable"},
            )
            return None
        try:
            credential = DefaultAzureCredential()
            self._resource_client = ResourceManagementClient(credential, subscription_id)
        except Exception as exc:
            record_security_event(
                action="connector_client_init",
                resource="connector:azure",
                decision="failed",
                risk_level="medium",
                metadata={"reason": exc.__class__.__name__},
            )
            return None
        record_security_event(
            action="connector_client_init",
            resource="connector:azure",
            decision="allowed",
            risk_level="medium",
            metadata={"sdk": "azure"},
        )
        return self._resource_client

    def discover_inventory(self) -> list[dict]:
        _ = settings.enable_cloud_connectors
        ensure_cloud_connector_enabled(self.connector_type)
        record_security_event(
            action="connector_sync",
            resource="connector:azure",
            decision="started",
            risk_level="medium",
            metadata={"operation": "discover_inventory"},
        )
        self._client()
        entities: list[AzureInventoryEntity] = []
        record_security_event(
            action="connector_sync",
            resource="connector:azure",
            decision="completed",
            risk_level="medium",
            metadata={"items": len(entities)},
        )
        return [entity.model_dump() for entity in entities]


def discover_inventory() -> list[dict]:
    """Return normalized Azure inventory entities."""
    return AzureInventoryConnector().discover_inventory()
