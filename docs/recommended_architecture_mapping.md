# Recommended Architecture Mapping for ProjectRAG

Generated: 2026-06-17

This maps the requested target architecture to the current ProjectRAG repository and identifies implementation priority for an excellence-grade presentation and delivery path.

## Executive Result

ProjectRAG already matches the recommended architecture at the **local MVP / prototype** level for Frontend, Backend RAG services, pgvector/PostgreSQL storage, GraphDB topology, evaluation foundations, and audit traces.

The largest gaps are in the **Middleware/API Gateway** layer and production storage/observability:

- no real endpoint authentication/RBAC enforcement yet
- no rate limiting middleware yet
- cache is in-process only, not Redis
- no object storage layer yet
- no OpenTelemetry/Grafana/Loki stack yet
- notification/automation is deliberately blocked/recommendation-only for safety

The correct next direction is **not** to jump to AGII/autonomous execution. The correct path is:

1. stabilize MVP and evidence quality
2. add gateway controls: auth, validation, rate limits, audit middleware
3. add evaluation and presentation dashboards
4. then expand read-only infrastructure connectors
5. only later consider controlled approval workflows

## 1. Frontend

| Recommended component | Current implementation | Status | Evidence | Gap / next action |
|---|---|---:|---|---|
| Chat UI | Streamlit Query tab | Implemented MVP | `ui/streamlit_app.py` | Add saved conversations and citation/source viewer |
| Admin Dashboard | Streamlit Cockpit tab | Implemented MVP | `render_dashboard_panel()` | Add runtime config, service controls, and quality gates |
| Infrastructure Topology View | Streamlit Topology tab + `/graph/export` | Implemented MVP | `app/api/routes_graph.py`, `ui/streamlit_app.py` | Improve layout, filtering, impact paths, node details |
| Document/Knowledge Manager | Streamlit Documents tab + upload/list/delete/reindex | Implemented MVP | `app/api/routes_documents.py` | Add file preview, ingestion status, per-document graph stats |
| Audit & Evaluation Console | Streamlit Audit tab + workflow audit routes | Partial | `app/api/routes_workflow_audit.py`, `app/evaluation/*` | Add evaluation report UI and security audit events UI |

### Frontend maturity

**Score: 65/100**

The UI now presents well for demos. It is still Streamlit, not a full production SPA. That is acceptable for MVP/excellence presentation but not enterprise frontend scale.

## 2. Middleware / API Gateway

| Recommended component | Current implementation | Status | Evidence | Gap / next action |
|---|---|---:|---|---|
| Authentication / RBAC | Local identity and RBAC modules exist | Skeleton | `app/security/identity.py`, `app/security/rbac.py`, `app/security/policy_engine.py` | Add FastAPI dependency/middleware to enforce auth on routes |
| Request validation | Pydantic schemas and FastAPI validation | Implemented MVP | `app/core/schemas.py`, route models | Add stricter schemas for all endpoints and payload size limits |
| Rate limiting | Not implemented | Missing | none | Add local in-memory limiter first, Redis later |
| Caching | In-process cognitive cache | Partial | `app/ragos/cognitive_cache.py` | Wire cache into query/graph endpoints; Redis later |
| Prompt policy layer | Safety classifier, validator, tool policies | Partial | `app/tools/safety.py`, `app/agents/validator.py`, `app/tools/tool_policy.py` | Add explicit prompt-injection checks before retrieval/generation |
| Audit logging | Workflow/agent/validation storage; security audit module | Partial | `workflow_runs`, `agent_runs`, `validation_results`, `app/security/audit.py` | Add request-level audit middleware and expose security events |

### Middleware maturity

**Score: 35/100**

This is the key gap for excellence and production readiness. The modules exist, but enforcement at the API boundary is incomplete.

## 3. Backend Services

| Recommended component | Current implementation | Status | Evidence | Gap / next action |
|---|---|---:|---|---|
| RAG Orchestrator | LangGraph workflow | Implemented MVP | `app/workflows/rag_workflow.py` | Add robust error paths and per-step telemetry |
| Document Ingestion Service | File ingestion, chunking, graph extraction | Implemented MVP | `app/rag/ingestion.py`, `app/rag/chunking.py` | Add ingestion runs/status table and background jobs |
| Embedding Service | Ollama embedding client | Implemented MVP | `app/tools/ollama_client.py` | Add batching/retry/backoff and model health checks |
| Retrieval Service | Vector, graph, memory retrieval agents | Implemented MVP | `app/agents/vector_retriever.py`, `graph_retriever.py`, `memory_agent.py` | Add metadata filters and hybrid retrieval tuning |
| LLM Generation Service | Ollama generate client + reasoner | Implemented MVP | `app/agents/reasoner.py` | Add prompt templates, timeout handling, response validation |
| Infrastructure Connectors | Docker discovery, AWS/Azure inventory skeletons, topology importer | Partial | `app/discovery`, `app/connectors`, `app/devops/topology_importer.py` | Expand read-only Kubernetes/Terraform/Prometheus connectors |
| Evaluation Service | deterministic metrics + eval runner | Partial | `app/evaluation/*`, `scripts/generate_metrics_report.py` | Add UI and acceptance thresholds/gates |
| Notification/Automation Service | Recommendation-only action planning; execution blocked | Safe skeleton | `app/devops/*`, `app/tools/tool_executor.py` | Keep blocked until auth/RBAC/audit/approval are mature |

### Backend maturity

**Score: 70/100 for MVP, 45/100 for production**

RAG/GraphRAG foundations are strong. Production service boundaries, background workers, and telemetry need more maturity.

## 4. Storage

| Recommended component | Current implementation | Status | Evidence | Gap / next action |
|---|---|---:|---|---|
| Vector DB: Qdrant / Weaviate / pgvector | PostgreSQL + pgvector | Implemented MVP | `scripts/init_postgres.sql`, `chunks.embedding vector(768)` | pgvector is sufficient now; add vector indexes/tuning as data grows |
| Relational DB: PostgreSQL | Implemented | `app/memory/postgres.py`, repositories | Add migration framework such as Alembic later |
| Object Storage: S3 / MinIO / Azure Blob | Not implemented | Missing | local file upload only | Add MinIO for local object storage if files grow beyond local dev |
| Cache: Redis | Not implemented | Missing | in-memory cache only | Add Redis when multi-process/multi-node begins |
| Logs/Telemetry: OpenTelemetry + Grafana/Prometheus | Prometheus metrics only | Partial | `/metrics`, `app/core/metrics.py`, `prometheus-client` | Add OpenTelemetry tracing, Grafana dashboard, structured log shipping |
| Graph Store | GraphDB plus PostgreSQL graph facts | Implemented MVP | `app/graph/graphdb_client.py`, `app/memory/graph_fact_store.py` | Add provenance-aware GraphDB cleanup on delete/reindex |

### Storage maturity

**Score: 60/100**

Core local storage is good. Object storage, distributed cache, and full telemetry are future production layers.

## 5. Recommended Folder Structure Evolution

Current repository is already modular. For clearer enterprise architecture, future structure could evolve to:

```text
app/
  api/                 FastAPI route modules
  gateway/             auth, rate limit, request audit middleware
  services/            orchestration service layer wrapping agents/repositories
  rag/                 chunking, ingestion, vector store
  graph/               GraphDB and ontology logic
  retrieval/           optional future explicit retrieval services
  agents/              agent-level deterministic/LLM logic
  connectors/          external read-only infrastructure connectors
  repositories/        database access boundary
  security/            RBAC, identity, policy, audit
  evaluation/          eval runners and metrics
  observability/       tracing, logging, metrics helpers
ui/
  streamlit_app.py     current excellence cockpit
```

Do **not** rush this refactor. Current structure is acceptable. Add `gateway/` only when implementing middleware controls.

## 6. Highest Priority Gaps

### P0 — Keep MVP demonstrable

- Keep tests/lint/type passing.
- Keep Streamlit cockpit aligned with backend routes.
- Ensure sample topology data can populate chunks and graph facts.

### P1 — Middleware/API Gateway excellence

Implement in this order:

1. request audit middleware
2. local API key auth for non-health endpoints
3. endpoint permission map using existing RBAC/policy engine
4. in-memory rate limiter
5. prompt policy pre-check on `/query`

### P2 — Evidence and evaluation excellence

1. evaluation dashboard in UI
2. dataset pass/fail thresholds
3. retrieval precision metrics
4. hallucination/prompt-injection regression tests

### P3 — Storage/observability excellence

1. GraphDB provenance-aware cleanup
2. Redis cache only when multi-process is needed
3. OpenTelemetry tracing
4. Grafana/Prometheus dashboard
5. MinIO/object storage only when document volume requires it

## 7. Final Architecture Scorecard

| Layer | Score | Summary |
|---|---:|---|
| Frontend | 65 | Strong Streamlit excellence cockpit for demo/MVP |
| Middleware/API Gateway | 35 | Main production gap; modules exist but enforcement is incomplete |
| Backend Services | 70 MVP / 45 production | RAG/GraphRAG strong; background jobs/service boundaries still basic |
| Storage | 60 | pgvector/Postgres/GraphDB good; object/cache/telemetry missing |
| Security/Governance | 40 | safe defaults and blocked execution; no production auth yet |
| Audit/Evaluation | 55 | workflow and validation audit exist; evaluation UI/gates need more work |

## Recommendation

ProjectRAG is structurally on the right path. For excellence, prioritize the **API Gateway layer** next. That layer will make the current backend and frontend look professional, safe, and enterprise-ready without prematurely implementing dangerous autonomous execution.
