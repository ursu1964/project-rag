"""Shared API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)


class ValidationResult(BaseModel):
    grounded: bool = False
    confidence: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    requires_human_approval: bool = True
    model_config = ConfigDict(extra="allow")


class QueryEvidence(BaseModel):
    vector: list[Any] = Field(default_factory=list)
    graph: list[Any] | dict[str, Any] = Field(default_factory=list)
    memory: list[Any] = Field(default_factory=list)


class QueryMetrics(BaseModel):
    workflow_id: str | None = None
    duration_ms: int = 0
    model_config = ConfigDict(extra="allow")


class QueryResponse(BaseModel):
    question: str | None = None
    route: str | None = None
    answer: str | None = None
    validation: ValidationResult | dict[str, Any] | None = None
    evidence: QueryEvidence = Field(default_factory=QueryEvidence)
    citations: list[dict[str, Any]] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    policy_decision: dict[str, Any] = Field(default_factory=dict)
    metrics: QueryMetrics = Field(default_factory=QueryMetrics)
    model_config = ConfigDict(extra="allow")


class IngestResponse(BaseModel):
    status: str
    results: list[dict[str, Any]] = Field(default_factory=list)


class DocumentRecord(BaseModel):
    id: str
    source: str | None = None
    file_hash: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: Any = None
    updated_at: Any = None
    model_config = ConfigDict(extra="allow")


class GraphQueryRequest(BaseModel):
    query: str = Field(min_length=1)


class HealthResponse(BaseModel):
    status: str
    service: str | None = None
    postgres: str | None = None
    graphdb: str | None = None
    ollama: str | None = None
    errors: dict[str, str] | None = None
