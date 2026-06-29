# Worktree Changeset Plan

This repository currently contains a large mixed worktree. Do not squash it into one commit.
Use the following commit order so each change can be reviewed, tested, and reverted independently.

## Commit 0 — changeset plan

Purpose: document how to split the current mixed worktree before landing code.

Files:

- `docs/architecture/CHANGESET_PLAN.md`

Validation:

```bash
git diff -- docs/architecture/CHANGESET_PLAN.md
```

## Commit 1 — local run, security, and production hardening

Purpose: make the local stack safer by default and close the critical/high security findings.

Files:

- `.env.example`
- `docker-compose.yml`
- `run.sh`
- `app/gateway/middleware.py`
- `app/core/settings_validator.py`
- `app/core/config.py`
- `frontend/lib/api.ts`
- `frontend/app/dashboards/page.tsx`
- `frontend/components/AuthProvider.tsx`
- `tests/test_gateway_middleware.py`
- `tests/test_oidc_jwt_verification.py`
- `tests/test_security_phase_1.py`
- `tests/e2e/test_e2e_production_hardening.py`

Validation:

```bash
.venv/bin/python -m pytest tests/test_gateway_middleware.py tests/test_security_phase_1.py tests/e2e/test_e2e_production_hardening.py -q
docker compose config >/tmp/projectrag-compose-config.txt
```

## Commit 2 — AIOS model, memory, vector, workflow, and registry backend

Purpose: introduce AIOS backend primitives while preserving existing ProjectRAG behavior.

Files:

- `docs/architecture/AIOS_PRODUCT_MAP.md`
- `app/models/__init__.py`
- `app/models/provider.py`
- `app/tools/ollama_client.py`
- `app/api/routes_openai_compat.py`
- `app/api/routes_registry.py`
- `app/agents/registry.py`
- `app/workflows/registry.py`
- `app/workflows/rag_workflow.py`
- `app/memory/memory_store.py`
- `app/rag/vector_store.py`
- `app/services/qdrant_vector_store.py`
- `app/core/correlation.py`
- `app/api/routes_query.py`
- `app/main.py`

Validation:

```bash
.venv/bin/python -m pytest tests/e2e/test_smoke_rag_flow.py tests/test_openapi_contract.py -q
.venv/bin/ruff check app
```

## Commit 3 — ingestion, Ask AI, dashboard, and topology UX

Purpose: expose the new local-AI control-plane flows in the web UI.

Files:

- `frontend/app/ask/page.tsx`
- `frontend/app/documents/page.tsx`
- `frontend/app/dashboards/page.tsx`
- `frontend/app/memory/page.tsx`
- `frontend/app/models/page.tsx`
- `frontend/app/workflows/page.tsx`
- `frontend/components/AppShell.tsx`
- `frontend/components/TopologyExplorer.tsx`
- `frontend/lib/api.ts`

Validation:

```bash
cd frontend && npx tsc --noEmit --ignoreDeprecations 6.0
```

## Commit 4 — observability and database bootstrap assets

Purpose: add local operational dashboards/provisioning and fresh-database bootstrap assets.

Files:

- `scripts/init_postgres.sql`
- `scripts/reset_grafana_admin.sh`
- `deploy/monitoring/grafana/dashboards/01_health_availability.json`
- `deploy/monitoring/grafana/dashboards/02_latency_error_by_endpoint.json`
- `deploy/monitoring/grafana/dashboards/03_postgres_data_ingestion.json`
- `deploy/monitoring/grafana/dashboards/04_workflow_agent_performance.json`
- `deploy/monitoring/grafana/provisioning/dashboards/dashboards.yml`
- `deploy/monitoring/grafana/provisioning/datasources/datasources.yml`

Validation:

```bash
docker compose config >/tmp/projectrag-compose-config.txt
.venv/bin/python scripts/validate_observability.py
```

## Commit 5 — docs, connector defaults, and generated API contract

Purpose: capture documentation updates, connector default fixes, and OpenAPI snapshot drift from API changes.

Files:

- `README.md`
- `.github/copilot-instructions.md`
- `app/connectors/aws/models.py`
- `app/connectors/azure/models.py`
- `docs/openapi.snapshot.json`
- `app/agents/memory_agent.py`
- `app/agents/router.py`

Validation:

```bash
.venv/bin/python -m pytest tests/test_aws_connector.py tests/test_azure_connector.py tests/test_openapi_contract.py -q
```

## Final release-gate validation

Two files intentionally require patch-level staging because they contain changes from
more than one workstream:

- `frontend/lib/api.ts`
  - Commit 1: secret handling and auth header hardening.
  - Commit 3: multipart upload helper for ingestion.
- `frontend/app/dashboards/page.tsx`
  - Commit 1: restrict sensitive infrastructure links to admin/operator roles.
  - Commit 3: add AIOS dashboard links.

Use `git add -p` for these files if exact commit isolation is required.

Run after all commits are applied in order:

```bash
.venv/bin/ruff check app tests scripts
.venv/bin/python -m pytest -q
cd frontend && npx tsc --noEmit --ignoreDeprecations 6.0
docker compose config >/tmp/projectrag-compose-config.txt
```

Current known validation result before commit splitting: backend tests pass and frontend typecheck passes.
