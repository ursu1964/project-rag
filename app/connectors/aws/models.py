"""AWS inventory connector models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AWSInventoryEntity(BaseModel):
    name: str
    entity_type: str
    provider: str = "aws"
    region: str = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)
