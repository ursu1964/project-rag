# ProjectRAG Implementation Roadmap

This document converts the prioritized implementation checklist into three planning views:

- a short roadmap table
- a sprint-by-sprint plan
- a PR-ready issue list

## Short Roadmap

| Phase | Focus | Outcome |
|---|---|---|
| P0 | Keep the MVP stable | Preserve current local startup, query, ingestion, and graph behavior |
| P1 | Security and gateway controls | Add auth, audit, rate limiting, and request hardening |
| P2 | Durable persistence and workflow state | Add migrations, GraphDB bootstrap, checkpointing, and background jobs |
| P3 | Integration coverage | Prove behavior against real PostgreSQL, GraphDB, and API paths |
| P4 | Observability | Close tracing, logging, dashboards, and alerting gaps |
| P5 | Scale and boundary features | Add Redis, model routing, and future isolation only when needed |

## Sprint-by-Sprint Plan

### Sprint 1: Stability and security baseline

Goals:

- keep the MVP stable
- add API security and gateway controls

Work items:

- request audit middleware
- local API token support for non-health endpoints
- endpoint-level authorization using RBAC/policy modules
- in-memory rate limiting
- prompt-injection checks before retrieval/generation
- upload size and file-count limits

Exit criteria:

- unauthenticated access is blocked where intended
- abusive request patterns are throttled or rejected
- audit events are visible for review

### Sprint 2: Durability and workflow state

Goals:

- remove schema-management fragility
- make GraphDB and workflow execution more durable

Work items:

- introduce Alembic or a lightweight migration framework
- automate GraphDB repository creation/configuration
- add durable workflow checkpointing or replay support
- add background jobs for ingestion and evaluation
- define retention/cleanup for workflow and evaluation records

Exit criteria:

- schema changes no longer depend on a single large SQL script
- GraphDB can bootstrap with minimal manual steps
- long-running tasks can run outside request/response cycles

### Sprint 3: Real integration coverage

Goals:

- prove the system against real runtime services

Work items:

- Docker-backed PostgreSQL vector-search integration tests
- live GraphDB integration tests
- multipart upload integration tests
- `/query` integration test with real DB services and mocked Ollama
- regression tests for hallucination and prompt-injection controls

Exit criteria:

- core runtime dependencies are exercised in tests
- the most important flows are validated outside mocks

### Sprint 4: Observability and operations

Goals:

- make runtime behavior easier to inspect and support

Work items:

- OpenTelemetry tracing
- structured log strategy or log shipping
- Grafana dashboards for runtime and evaluation
- Prometheus alerts and Alertmanager routing verification
- backup and restore verification documentation

Exit criteria:

- health, metrics, and alerts are visible and usable
- failures can be traced from request to persistence and workflow state

### Sprint 5: Scale and product boundaries

Goals:

- add only the scale features that the MVP now needs

Work items:

- Redis only if multi-process or multi-node usage requires it
- model tier routing from the resource allocator
- multi-tenant or per-project isolation if the product needs it
- expand read-only infrastructure connectors only after earlier phases

Exit criteria:

- the MVP stays focused and safe
- new scope does not outrun security, durability, or test coverage

## PR-Ready Issue List

### P0. Stability

- [ ] Keep `pytest` passing on the target Python version.
- [ ] Keep the local smoke test working end to end.
- [ ] Keep the Streamlit cockpit aligned with backend routes.
- [ ] Keep the sample topology dataset ingesting cleanly.

### P1. Security and gateway

- [ ] Add request audit middleware for API calls.
- [x] Add request audit middleware for API calls.
- [ ] Add local API token support for non-health endpoints.
- [ ] Enforce endpoint-level authorization with RBAC/policy modules.
- [ ] Add in-memory rate limiting for query and ingestion routes.
- [ ] Add prompt-injection checks before retrieval and generation.
- [ ] Add upload size and file-count limits.

### P2. Durability

- [ ] Introduce Alembic or a lightweight migration framework.
- [ ] Automate GraphDB repository creation/configuration.
- [ ] Add durable workflow checkpointing or replay support.
- [ ] Add background jobs for ingestion and evaluation.
- [ ] Add retention/cleanup rules for workflow and evaluation data.

### P3. Integration tests

- [ ] Add Docker-backed PostgreSQL vector-search integration tests.
- [ ] Add live GraphDB integration tests.
- [ ] Add multipart upload integration tests.
- [ ] Add `/query` integration tests with real DB services.
- [ ] Add regression tests for prompt-injection and hallucination controls.

### P4. Observability

- [ ] Add OpenTelemetry tracing.
- [ ] Add structured log shipping or a defined log strategy.
- [ ] Add Grafana dashboards for runtime and evaluation visibility.
- [ ] Verify Prometheus alerts and Alertmanager routing.
- [ ] Document and test backup/restore.

### P5. Scale and boundaries

- [ ] Add Redis only when multi-process or multi-node usage requires it.
- [ ] Add model tier routing from the resource allocator.
- [ ] Add multi-tenant or per-project isolation if needed.
- [ ] Expand read-only infrastructure connectors only after core gaps are closed.
