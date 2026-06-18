# ProjectRAG Prioritized Implementation Checklist

This checklist turns the current documentation gaps into an execution order.

## P0. Keep the MVP stable

- [ ] Keep `pytest` passing on the current target Python version.
- [ ] Keep the local smoke test working end to end.
- [ ] Keep the Streamlit cockpit aligned with the current API routes.
- [ ] Keep the sample topology dataset ingesting cleanly.

Success criteria:

- Local startup remains reproducible.
- No regression in health, query, ingestion, or graph export paths.

## P1. Add API security and gateway controls

- [x] Add request audit middleware for API calls.
- [ ] Add local API token support for non-health endpoints.
- [ ] Enforce endpoint-level authorization with the existing RBAC/policy modules.
- [ ] Add in-memory rate limiting for query and ingestion routes.
- [ ] Add prompt-injection checks before retrieval and generation.
- [ ] Add upload size and file-count limits.

Success criteria:

- Unauthenticated access is blocked where intended.
- High-volume or high-risk requests are safely throttled or rejected.
- Audit events are persisted or exposed for review.

## P2. Make persistence and workflow state durable

- [ ] Introduce Alembic or a lightweight migration framework.
- [ ] Automate GraphDB repository creation/configuration.
- [ ] Add durable workflow state or checkpointing for LangGraph runs.
- [ ] Add background jobs for ingestion and evaluation.
- [ ] Add a clear retention or cleanup strategy for workflow/evaluation records.

Success criteria:

- Schema changes no longer depend on one large SQL script.
- GraphDB bootstraps without manual operator steps.
- Long-running jobs can run outside request/response cycles.

## P3. Improve integration coverage

- [ ] Add Docker-backed PostgreSQL vector-search integration tests.
- [ ] Add live GraphDB integration tests.
- [ ] Add multipart upload integration tests.
- [ ] Add `/query` integration tests with real DB services and mocked Ollama.
- [ ] Add regression tests for prompt-injection and hallucination controls.

Success criteria:

- Tests cover real service behavior, not only mocks.
- The main runtime dependencies are exercised before release.

## P4. Close the observability gap

- [ ] Add OpenTelemetry tracing.
- [ ] Add structured log shipping or a clear log strategy.
- [ ] Add Grafana dashboards for runtime and evaluation visibility.
- [ ] Verify Prometheus alerts and Alertmanager routing.
- [ ] Document backup and restore verification clearly.

Success criteria:

- Health, metrics, and alerting are visible from the documented operations stack.
- Operators can trace failures from request to storage and workflow state.

## P5. Add scale and product boundaries later

- [ ] Add Redis only when multi-process or multi-node usage needs it.
- [ ] Add model tier routing based on the resource allocator.
- [ ] Add multi-tenant or per-project isolation if the product requires it.
- [ ] Expand read-only infrastructure connectors only after the core gateway and persistence work are complete.

Success criteria:

- The MVP stays focused and safe.
- New scope does not outrun security, durability, or test coverage.

## Suggested Release Sequence

1. Finish P1 security and gateway controls.
2. Finish P2 durable persistence and workflow state.
3. Finish P3 integration coverage.
4. Finish P4 observability.
5. Consider P5 scale features only after the earlier gates pass.
