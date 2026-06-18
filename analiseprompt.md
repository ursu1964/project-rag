# ProjectRAG Implementation Prompt and Step-by-Step Execution Plan

## Goal

Build the existing repository into an infrastructure-intelligence RAG platform by reusing as much current code as possible. The platform should actively support local document ingestion, graph/vector retrieval, query answering, citations, audit, evaluation, middleware, UI, Redis/Qdrant/PostgreSQL services, and observability. Cloud-provider connectors must remain dormant for now.

## Current Foundation to Reuse

The repository already contains strong reusable foundations:

- FastAPI application factory in `app/main.py`.
- Health, query, document, graph, memory, evaluation, feedback, source, and audit-style routes.
- PostgreSQL helpers and schema in `app/memory/postgres.py` and `scripts/init_postgres.sql`.
- pgvector-backed chunk storage in `app/repositories/chunks_repository.py`.
- GraphDB integration in `app/graph/graphdb_client.py`.
- RAG ingestion and repair logic in `app/rag/ingestion.py`.
- RAG workflow in `app/workflows/rag_workflow.py`.
- Citation, parsing, source catalog, prompt policy, PII filter, RBAC/security modules.
- Initial connector skeletons for AWS/Azure.
- Docker Compose foundation.
- Streamlit UI plus newly added Next.js frontend scaffold.
- A broad existing automated test suite.

## Operating Rule

Prefer reuse over rewriting:

1. Extend existing modules where possible.
2. Keep existing API behavior stable.
3. Add feature flags for incomplete or risky areas.
4. Keep cloud connector execution dormant until explicitly enabled.
5. Keep destructive infrastructure actions disabled.
6. Add tests with each implementation step.

## Active Now

These parts can be active immediately:

- Local FastAPI API.
- PostgreSQL/pgvector.
- Redis cache.
- Qdrant optional vector index.
- GraphDB local graph store.
- Ollama/local LLM integration.
- Document ingestion.
- Vector retrieval.
- Graph retrieval.
- Hybrid RAG query.
- Citations.
- Prompt security checks.
- PII redaction.
- Audit logs.
- Evaluation routes and datasets.
- Local Docker Compose.
- Next.js frontend shell.
- Kubernetes/Terraform deployment manifests as templates only.

## Dormant For Now

Cloud and external infrastructure integrations must remain dormant until manually enabled:

- AWS live API calls.
- Azure live API calls.
- GCP live API calls.
- Any cloud write/mutation action.
- Linux/Windows live server collectors.
- Ticketing/CMDB live writes.
- Terraform apply/destroy.
- Ansible playbook execution.

Dormant means:

- Routes may list connector capability.
- Test/dry-run endpoints may return safe metadata.
- Sync endpoints must not call live cloud APIs by default.
- Configuration must require an explicit enable flag before any live cloud discovery.
- No credentials should be read from environment unless the connector is enabled.

## Step-by-Step Implementation Plan

### Step 1 — Stabilize the local active baseline

- Keep tests green.
- Keep Docker Compose valid.
- Ensure local services include PostgreSQL, Redis, Qdrant, GraphDB, API, frontend, and OpenTelemetry collector.
- Ensure cloud connectors are marked dormant by default.

Acceptance:

- `pytest -q` passes.
- `docker compose config` passes.
- `/health` route imports cleanly.
- `/connectors` shows cloud connectors as dormant unless enabled.

### Step 2 — Harden connector gating

- Add an explicit config flag such as `ENABLE_CLOUD_CONNECTORS=false`.
- Return `skipped` for AWS/Azure sync when disabled.
- Keep Terraform/Kubernetes/Prometheus connector entries as local/planned unless implemented safely.
- Store only secret references later, never secret values.

Acceptance:

- AWS/Azure sync performs no live calls by default.
- Connector response clearly says cloud connector is dormant.

### Step 3 — Complete local RAG APIs

- Reuse existing ingestion, vector store, graph retriever, workflow, citation, and validation modules.
- Keep `/query` as the main orchestration endpoint.
- Keep `/retrieval/vector`, `/retrieval/graph`, and `/retrieval/hybrid` as lower-level diagnostic endpoints.
- Add caching where safe.

Acceptance:

- Sample infrastructure document produces chunks and graph facts.
- Query returns answer, route, evidence, citations, confidence, and policy decision.

### Step 4 — Improve frontend progressively

- Keep current Next.js shell.
- Wire pages to existing FastAPI endpoints.
- Prefer simple views first, then graph visualization.
- Add streaming later after stable query workflow.

Acceptance:

- Dashboard shows API status.
- Ask page can call `/query`.
- Documents page lists documents.
- Topology page renders graph export JSON or graph canvas.
- Audit page lists audit events.

### Step 5 — Add production-shaped middleware

- Reuse existing gateway middleware, security modules, RBAC, prompt policy, and PII filters.
- Add Redis-backed rate limits and tenant-aware cache keys later.
- Keep local mode permissive unless configured otherwise.

Acceptance:

- Local dev remains easy.
- Production config can enforce auth/RBAC/rate limits.

### Step 6 — Add observability

- Keep Prometheus metrics endpoint.
- Use OpenTelemetry when enabled.
- Track query latency, retrieval latency, ingestion count, validation confidence, and cache hit ratio.

Acceptance:

- `/metrics` works.
- OpenTelemetry can be enabled by environment variable.

### Step 7 — Add QA gates

- Keep existing unit/integration tests.
- Add focused tests for connector dormancy, retrieval routes, embeddings route, and frontend smoke build when dependencies are available.
- Add RAG golden datasets as regression gates.

Acceptance:

- Connector dormancy cannot regress silently.
- RAG quality has measurable checks.

## Current Instruction to Future Implementers

Continue incrementally. Do not introduce a parallel architecture. Reuse the existing ProjectRAG modules and extend them safely. Keep cloud functionality dormant until the user explicitly asks to activate live cloud discovery.

---

# Measures Plan: Increase Enterprise Excellence Score from 7.4 to 9.0

## Target

Raise the platform from strong MVP / early enterprise foundation to enterprise-ready score **9.0/10** without overbuilding unsafe cloud automation.

Current audited score: **7.4/10**
Target score: **9.0/10**

## Scoring Focus

| Area | Current | Target | Main Measures |
|---|---:|---:|---|
| Architecture | 8 | 9 | formal service boundaries, data contracts, tenancy model |
| UI/UX | 7 | 8.5 | Next.js evidence-first UI, topology, audit/eval screens |
| Backend | 8 | 9 | migrations, background jobs, idempotent APIs |
| Frontend | 6 | 8.5 | production React implementation, responsive UX |
| Middleware | 7 | 9 | Redis rate limits/cache, auth/RBAC enforcement, tracing |
| RAG Quality | 8 | 9 | reranking, golden evals, confidence calibration |
| Security | 7 | 9 | OIDC-ready auth, tenant isolation, secret scanning, immutable audit plan |
| QA | 8 | 9 | RAG regression, prompt-injection, e2e smoke tests |
| Infrastructure Integration | 7 | 8.5 | safe connector SDK, local/Terraform/K8s/Prometheus first, cloud dormant |
| Observability | 6 | 8.5 | OpenTelemetry, metrics dashboards, cost/latency tracking |
| Business Value | 9 | 9.5 | package concrete workflows: Ask, topology, RCA, risk, audit |

## Guiding Principles

1. Reuse existing implementation first.
2. Keep cloud connectors dormant until explicitly enabled.
3. Keep infrastructure mutation disabled.
4. Improve production readiness before adding new futuristic features.
5. Make every RAG answer evidence-first, cited, auditable, and confidence-scored.
6. Add tests for every safety and quality improvement.

## Priority 1 — Platform Hardening

### Measures

- Add Alembic or migration-compatible schema management.
- Keep `scripts/init_postgres.sql` idempotent for local bootstrap.
- Add repository/service/API boundaries for new modules.
- Add API version prefix plan: `/api/v1` while preserving current routes.
- Add background job table usage for ingestion, connector sync, evaluation, and audit enrichment.
- Add idempotency keys for ingestion and connector runs.

### Acceptance Criteria

- Schema changes are repeatable.
- Ingestion can be retried without duplicate chunks/facts.
- Connector sync has durable run status.
- Existing tests stay green.

### Score Impact

- Architecture: +0.5
- Backend: +0.5
- QA: +0.2

## Priority 2 — Security and Governance

### Measures

- Implement OIDC-ready auth abstraction without forcing auth in local dev.
- Enforce RBAC when `ENFORCE_RBAC=true`.
- Add tenant-aware fields and filters for new tables.
- Scope Redis keys by tenant/user/model/version.
- Add secret/PII scanning before parsing, embedding, prompting, response, logs, and audit.
- Keep cloud connector credentials as future `secret_ref` only.
- Add audit events for query, ingestion, connector sync, policy block, prompt injection, and admin changes.

### Acceptance Criteria

- Local mode remains easy.
- Production mode can deny unauthorized routes.
- Secret test strings are redacted before embedding.
- Prompt-injection test sources are detected or downranked.
- Cloud sync remains dormant by default.

### Score Impact

- Security: +1.2
- Middleware: +0.6
- Architecture: +0.2

## Priority 3 — RAG Quality Upgrade

### Measures

- Formalize route classifier: `graph`, `vector`, `hybrid`, `blocked`, `deterministic`.
- Add deterministic graph answers for simple dependency questions.
- Add reranking for hybrid retrieval.
- Add context assembly format with graph facts, chunks, limitations, and source IDs.
- Compute confidence from evidence signals, not only LLM output.
- Validate citation coverage for factual claims.
- Add golden datasets:
  - `graph_questions.json`
  - `vector_questions.json`
  - `hybrid_questions.json`
  - `safety_questions.json`

### Acceptance Criteria

- “What does VM1 depend on?” answers from graph facts with citations.
- Unknown entities return insufficient-evidence warning.
- Every factual answer includes evidence and confidence.
- Golden RAG smoke suite passes in CI/local.

### Score Impact

- RAG Quality: +1.0
- QA: +0.5
- Business Value: +0.2

## Priority 4 — Production Frontend

### Measures

- Continue Next.js implementation under `frontend/`.
- Build evidence-first Ask page:
  - answer
  - route
  - confidence
  - citations
  - graph facts
  - warnings
- Build Documents page:
  - upload
  - list
  - reindex
  - ingestion status
- Build Topology page:
  - graph export visualization
  - node detail drawer
  - dependency/impact mode
- Build Audit page:
  - audit table
  - filters
  - event detail drawer
- Build Evaluation page:
  - dataset status
  - run results
  - failed cases

### Acceptance Criteria

- Frontend can run with Docker Compose.
- Ask page calls `/query` successfully.
- Documents page lists current documents.
- Topology page displays graph facts.
- Audit page displays audit events.

### Score Impact

- Frontend: +1.5
- UI/UX: +1.0
- Business Value: +0.2

## Priority 5 — Middleware and Performance

### Measures

- Add Redis-backed cache for:
  - embeddings
  - permissions
  - retrieval results
  - graph queries
- Add route-level rate limiting when configured.
- Add request correlation IDs.
- Add optional SSE streaming for `/query` later.
- Add query/retrieval timeouts and max graph depth enforcement.
- Move long-running ingestion/evaluation/connector tasks to background workers.

### Acceptance Criteria

- Repeated embedding requests can hit cache.
- Rate limit can block excessive requests when enabled.
- Logs include correlation ID.
- Long-running work does not block normal API requests.

### Score Impact

- Middleware: +1.0
- Backend: +0.4
- UI/UX: +0.2

## Priority 6 — Observability

### Measures

- Enable OpenTelemetry instrumentation by environment flag.
- Add Prometheus metrics for:
  - API request count/latency
  - query duration
  - retrieval duration
  - ingestion count/failures
  - validation confidence
  - cache hit/miss
  - connector sync status
- Add starter Grafana dashboard JSON or docs.
- Add structured logs with request/workflow/correlation IDs.

### Acceptance Criteria

- `/metrics` exposes platform metrics.
- OTEL collector runs in Docker Compose.
- Query path emits duration metric.
- Ingestion and connector status are observable.

### Score Impact

- Observability: +1.5
- QA: +0.2
- Backend: +0.2

## Priority 7 — Infrastructure Integration, Safely

### Measures

Active now:

- File connector.
- Terraform local parser/importer.
- Kubernetes manifest parser/importer.
- Prometheus metadata/alerts connector if read-only and local-configured.

Dormant until enabled:

- AWS live discovery.
- Azure live discovery.
- Any cloud write action.

### Acceptance Criteria

- `/connectors` clearly shows dormant vs active/planned connectors.
- AWS/Azure sync returns skipped while cloud connector flag is false.
- Local Terraform/K8s files can create entities/facts.
- Connector runs are audited.

### Score Impact

- Infrastructure Integration: +1.0
- Security: +0.2
- Business Value: +0.2

## Priority 8 — QA Expansion

### Measures

- Add unit tests for new services.
- Add API tests for new routes.
- Add connector dormancy tests.
- Add RAG golden eval tests.
- Add prompt-injection regression tests.
- Add PII/secret redaction tests.
- Add frontend smoke tests when Node dependencies are available.
- Add Docker Compose config validation to CI.

### Acceptance Criteria

- Safety regressions fail tests.
- RAG golden suite catches hallucination/missing citation regressions.
- All tests pass before release.

### Score Impact

- QA: +1.0
- Security: +0.3
- RAG Quality: +0.3

## Implementation Order

### Phase A — Immediate

1. Keep `analiseprompt.md` as implementation guidance.
2. Cloud connector dormancy flag and tests.
3. Fix/verify Docker Compose stack.
4. Add tests for new active routes.
5. Keep all tests green.

### Phase B — Local RAG Excellence

1. Improve retrieval/reranking.
2. Add confidence calibration.
3. Add deterministic citations.
4. Add golden RAG evals.
5. Improve source catalog and evidence display.

### Phase C — Enterprise Controls

1. RBAC enforcement mode.
2. Tenant-aware filters.
3. Redis rate limit/cache.
4. Audit enrichment.
5. Prompt/PII/secret scanning tests.

### Phase D — UX and Observability

1. Finish Next.js core pages.
2. Add topology visualization.
3. Add OpenTelemetry dashboards.
4. Add frontend smoke checks.

## Definition of 9.0 Readiness

The platform reaches approximately **9.0/10** when:

- Local Docker stack runs API, frontend, PostgreSQL, Redis, Qdrant, GraphDB, and telemetry.
- Documents ingest into chunks, vectors, graph facts, and citations.
- `/query` reliably answers from evidence with confidence and warnings.
- Unknown or unsupported questions do not hallucinate.
- Prompt injection and secrets are detected/redacted.
- Cloud connectors are safely dormant by default.
- UI supports Ask, Documents, Topology, Audit, and Evaluation workflows.
- Audit and metrics exist for all important actions.
- Regression tests cover RAG quality, security, connector dormancy, and APIs.

## What Is Not Required for 9.0

- Autonomous remediation.
- Live cloud mutation.
- Full HA/DR production deployment.
- Full CMDB/ticketing integration.
- Advanced predictive AIOps.
- Multi-region enterprise deployment.

Those belong to the path from **9.0 to 10.0**.

## Implementation Progress Update

### Completed after connector dormancy

- Added Redis-backed gateway rate limiting with safe in-memory fallback when Redis is unavailable.
- Extended RBAC route coverage for embeddings, retrieval, connectors, and audit routes.
- Added retrieval caching for vector and graph diagnostic endpoints.
- Added regression tests for Redis rate-limit behavior and retrieval cache behavior.

Validation:

```text
347 passed, 1 skipped
docker compose config OK
```

Next best step:

- Add durable background job orchestration for ingestion/evaluation/connector sync, then add RAG golden evaluation gates.
