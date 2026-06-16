"""DevOps inventory domain models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class InfrastructureEntity(BaseModel):
    name: str
    entity_type: str
    provider: str = "local"
    region: str = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class InfrastructureRelationship(BaseModel):
    source: str
    relationship: str
    target: str
    metadata: dict[str, Any] = Field(default_factory=dict)
