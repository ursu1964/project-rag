# ADR-001: Do Not Use n8n

## Status

Accepted

## Context

ProjectRAG needs local-first, testable, version-controlled workflow orchestration for RAG, GraphRAG, safety checks, validation, and future cognitive agents.

## Decision

ProjectRAG will not use n8n. Workflow logic will be implemented in Python agents and LangGraph workflows inside the repository.

## Consequences

- Workflows are version-controlled with the application code.
- Agent behavior can be unit tested.
- Local-first deployment is simpler and has fewer moving parts.
- Visual workflow editing is not available by default.

## Alternatives Considered

- n8n for visual workflow automation.
- External task orchestrators.
- Ad-hoc scripts without a workflow framework.
