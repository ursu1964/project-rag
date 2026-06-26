"""AWS inventory discovery.

Cloud SDK clients are created lazily and only when the cloud connector flag is on.
"""

from __future__ import annotations

import os
from typing import Any

from app.connectors.aws.models import AWSInventoryEntity
from app.connectors.registry import ensure_cloud_connector_enabled
from app.core.config import settings
from app.security.audit import record_security_event


class AWSInventoryConnector:
    connector_type = "aws"

    def __init__(self) -> None:
        self._sts_client: Any | None = None

    def _client(self) -> Any | None:
        """Initialize boto3 lazily without allowing EC2 metadata fallback."""
        if self._sts_client is not None:
            return self._sts_client
        os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
        try:
            import boto3  # type: ignore
        except ImportError:
            record_security_event(
                action="connector_client_init",
                resource="connector:aws",
                decision="skipped",
                risk_level="low",
                metadata={"reason": "boto3_unavailable"},
            )
            return None
        try:
            self._sts_client = boto3.client("sts")
        except Exception as exc:
            record_security_event(
                action="connector_client_init",
                resource="connector:aws",
                decision="failed",
                risk_level="medium",
                metadata={"reason": exc.__class__.__name__},
            )
            return None
        record_security_event(
            action="connector_client_init",
            resource="connector:aws",
            decision="allowed",
            risk_level="medium",
            metadata={"sdk": "boto3"},
        )
        return self._sts_client

    def discover_inventory(self) -> list[dict]:
        _ = settings.enable_cloud_connectors
        ensure_cloud_connector_enabled(self.connector_type)
        record_security_event(
            action="connector_sync",
            resource="connector:aws",
            decision="started",
            risk_level="medium",
            metadata={"operation": "discover_inventory"},
        )
        self._client()
        entities: list[AWSInventoryEntity] = []
        record_security_event(
            action="connector_sync",
            resource="connector:aws",
            decision="completed",
            risk_level="medium",
            metadata={"items": len(entities)},
        )
        return [entity.model_dump() for entity in entities]


def discover_inventory() -> list[dict]:
    """Return normalized AWS inventory entities."""
    return AWSInventoryConnector().discover_inventory()
