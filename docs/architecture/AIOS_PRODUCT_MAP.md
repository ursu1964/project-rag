# AIOS Product Map

AIOS is the target product direction for this repository: a modular, local-first AI operating system that keeps model execution, memory, agent workflows, observability, and administration under local operator control.

This document maps the current ProjectRAG codebase into the AIOS product architecture and defines the first implementation boundary. It is intentionally additive: existing ProjectRAG names, routes, tests, and environment variables should remain compatible while AIOS modules are introduced.

## Product goal

Build a local AI OS with these core capabilities:

- FastAPI backend as the local system API.
- LangGraph workflows for agent orchestration.
- Ollama as the default local model backend.
- Shimmy OpenAI-compatible local endpoint for existing SDK/tool compatibility.
- PostgreSQL for durable relational memory, workflow state, audits, and operations data.
- Qdrant for vector memory and semantic recall.
- Web dashboard for operators and users.
- Logs, metrics, traces, health checks, and monitoring dashboards.

## Current-to-target map

| AIOS module | Current location | Current status | Target responsibility |
|---|---|---:|---|
| API gateway | `app/main.py`, `app/api/*`, `app/gateway/*` | Present | Versioned local system API, auth/RBAC, rate limits, audit hooks, OpenAPI docs. |
| Model gateway | `app/tools/ollama_client.py`, `app/api/routes_embeddings.py` | Partial | Unified provider interface for chat, completion, embedding, model listing, streaming, and telemetry. |
| Shimmy OpenAI API | Missing | Missing | `/v1/models`, `/v1/chat/completions`, `/v1/embeddings` backed by the model gateway and protected by existing auth. |
| Agent runtime | `app/agents/*` | Present modules | Agent capability registry, standard agent input/output contracts, run metadata, safety gates. |
| Workflow runtime | `app/workflows/*` | Partial | Real LangGraph `StateGraph` workflows with typed state, conditional routing, checkpoints, and durable run records. |
| PostgreSQL memory | `app/memory/*`, `scripts/init_postgres.sql` | Partial | Durable memory items, workflow runs, agent runs, audits, validations, jobs, and relational system state. |
| Vector memory | `app/rag/vector_store.py`, `app/services/qdrant_vector_store.py` | Partial | Qdrant-backed semantic memory with collection lifecycle, upsert/search/delete, filters, and health checks. |
| Graph/topology memory | `app/graph/*`, `app/api/routes_graph.py` | Present | Relationship extraction, topology exploration, graph retrieval, dependency reasoning. |
| Local dashboard | `frontend/*` | Present | AIOS control panel: ask, agents, workflows, models, memory, vector DB, logs, health, settings. |
| Observability | `app/core/metrics.py`, `app/core/telemetry.py`, `deploy/monitoring/*` | Present | Correlated logs/metrics/traces across requests, workflows, agents, memory, and model calls. |
| Operations | `app/services/background_jobs.py`, `app/api/routes_operations.py` | Present | Durable jobs, retries, maintenance tasks, backups, health, and local admin workflows. |
| Security | `app/security/*`, `app/gateway/middleware.py` | Present | Local auth, API key/JWT/OIDC, RBAC, prompt policy, audit, tenant context, safe defaults. |

## Target module boundaries

```text
app/
  api/                 FastAPI route surface, including AIOS and compatibility routes
  gateway/             auth, RBAC, rate limiting, request IDs, audit middleware
  models/              target: provider abstraction and OpenAI-compatible schemas
  tools/               current: Ollama/file helpers; target: low-level adapters only
  agents/              agent nodes and capability implementations
  workflows/           LangGraph graph definitions and workflow registry
  memory/              PostgreSQL-backed durable state and memory stores
  services/            background jobs, cache, Qdrant/vector service facades
  graph/               graph memory and topology reasoning
  rag/                 ingestion, retrieval, citations, scoring, source parsing
  core/                config, logging, metrics, telemetry, shared schemas
frontend/
  app/                 AIOS dashboard pages
  components/          shared dashboard components
  lib/                 API client and auth context
deploy/
  monitoring/          Prometheus, Grafana, Alertmanager, OTEL
  k8s/                 optional deployment manifests
```

The near-term approach should avoid large renames. Add AIOS-facing modules and docs while keeping ProjectRAG compatibility until the product boundary is stable.

## First implementation boundary

The first AIOS milestone should deliver a locally usable control plane without breaking the existing RAG flow:

1. Keep existing `/query`, `/documents`, `/graph`, `/memory`, `/health`, and `/metrics` routes working.
2. Add AIOS-compatible names/config aliases only where needed.
3. Make memory durable in PostgreSQL before expanding agent behavior.
4. Make Qdrant real but configurable so pgvector users are not broken.
5. Add the OpenAI-compatible Shimmy surface as a thin adapter over the same model gateway used internally.
6. Convert workflows to LangGraph incrementally while preserving current node order and response shape.
7. Extend dashboard pages after backend contracts are stable.

## Design principles

- Local-first: no cloud dependency required for core operation.
- Compatibility-first: preserve existing ProjectRAG routes, tests, and env vars during transition.
- Modular: model providers, memory backends, vector stores, agents, and workflows should be swappable.
- Observable: every request, workflow, agent run, memory operation, and model call should be traceable.
- Safe by default: keep RBAC, audit, prompt policy, and production startup validation on the critical path.
- Small changes: each implementation step should be independently testable and reversible.

## Open decisions

- Should Qdrant become the default vector backend, or should AIOS support `pgvector`, `qdrant`, and `hybrid` modes from the start?
- Should AIOS expose new `/aios/*` routes, or keep route names product-neutral and rely on dashboard branding?
- Should GraphDB remain required for local startup, or become an optional graph-memory module?
- What is the minimum OpenAI compatibility surface for Shimmy: non-streaming only first, or streaming from the beginning?
- Should long-term memory search be text-only PostgreSQL first, vectorized Qdrant first, or both?

## Next implementation steps

1. Add `AIOS_*` configuration aliases while preserving `PROJECTRAG_*` variables.
2. Replace process-local memory with PostgreSQL-backed memory operations.
3. Add Qdrant collection lifecycle and search/upsert implementation.
4. Define a vector backend selector: `pgvector`, `qdrant`, or `hybrid`.
5. Introduce a model provider abstraction over Ollama.
6. Add minimal Shimmy OpenAI-compatible routes.
7. Convert the current deterministic RAG workflow into a LangGraph `StateGraph` with the same behavior.
8. Add workflow/agent registry metadata for dashboard discovery.
9. Add dashboard pages for models, memory, vector collections, and workflow runs.
10. Add correlation IDs across logs, metrics, traces, audits, workflow records, and model calls.
