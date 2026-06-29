"""AWS connector normalized models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AWSInventoryEntity(BaseModel):
    name: str = ""
    entity_type: str = "AWSResource"
    provider: str = "aws"
    region: str = "unknown"
    resource_id: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
