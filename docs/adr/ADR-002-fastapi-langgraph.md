# ADR-002: Use FastAPI and LangGraph

## Status

Accepted

## Context

ProjectRAG needs an API layer and explicit multi-step agent orchestration for query, ingestion, validation, and cognitive workflows.

## Decision

Use FastAPI for HTTP APIs and LangGraph for workflow orchestration.

## Consequences

- FastAPI provides a lightweight, typed, Python-native API layer.
- LangGraph provides explicit graph-based control flow for agents.
- Workflows remain local and testable.
- Runtime behavior depends on Python package compatibility.

## Alternatives Considered

- Flask for the API layer.
- Celery or Airflow for orchestration.
- Handwritten procedural pipelines only.
