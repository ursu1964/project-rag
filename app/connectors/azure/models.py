"""Azure inventory connector models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AzureInventoryEntity(BaseModel):
    name: str
    entity_type: str
    provider: str = "azure"
    region: str = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)
