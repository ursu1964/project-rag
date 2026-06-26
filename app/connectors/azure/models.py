"""Azure connector normalized models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AzureInventoryEntity(BaseModel):
    name: str = ""
    entity_type: str = "AzureResource"
    provider: str = "azure"
    location: str = ""
    resource_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
