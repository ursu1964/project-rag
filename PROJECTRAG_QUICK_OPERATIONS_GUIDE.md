# ProjectRAG Quick Operations Guide

This document is an execution-oriented guide for operators, developers, and technical stakeholders.

Single standard process for teams:

- Follow docs/standard_dashboard_and_analysis_workflow.md for one command startup plus one analysis checklist.

## 1. Agent Monitoring Dashboard (Yes, it exists)

ProjectRAG already provides a dashboard for monitoring workflows and agent activity:

- Streamlit Cockpit UI: `ui/streamlit_app.py`
- Audit tab shows:
  - recent workflow runs
  - recent agent runs
  - validation results
  - evaluation summary and quality gates

Related API endpoints used by the dashboard:

- `GET /workflows`
- `GET /workflows/{workflow_id}`
- `GET /agents/runs`
- `GET /validation/results`
- `GET /evaluation/report`
- `GET /health` and `GET /health/deep`
- `GET /metrics` (Prometheus format)

## 1.1 Models Connected Today and Production Expansion

Current active runtime models configured by default:

- 1 generation model: `OLLAMA_MODEL=llama3.1:8b`
- 1 embedding model: `EMBEDDING_MODEL=nomic-embed-text`

Total currently connected by default: **2 models**.

Additional model slots you can add in production:

- keep current local generation + embedding models
- optional remote tiered models via environment variables used by the allocator:
  - `PROJECTRAG_REMOTE_SMALL_MODEL`
  - `PROJECTRAG_REMOTE_MEDIUM_MODEL`
  - `PROJECTRAG_REMOTE_LARGE_MODEL`
  - `PROJECTRAG_REMOTE_MODEL_URL`

Practical production guidance:

- start with 2 to 4 models total (1 embedding + 1 to 3 generation tiers)
- scale to more models only with clear routing rules and cost/latency targets
- validate each model with evaluation report and latency dashboards before rollout

## 2. Starting the Application

### Option A: One-command local launcher (recommended)

Run API + Cockpit UI with automatic free-port selection:

Use `8001` by default unless you intentionally free `8000` for ProjectRAG.

```bash
python scripts/launch_app.py --with-ui --auto-port --auto-ui-port
```

What this does:

- starts FastAPI (`uvicorn`) from `app.main:app`
- starts Streamlit UI from `ui/streamlit_app.py`
- injects `PROJECTRAG_API_URL` into UI so API and UI stay aligned

### Option A2: One command for all dashboards

Run Cockpit dashboard plus any configured Grafana/Prometheus services in one command:

Use `8001` by default unless you intentionally free `8000` for ProjectRAG.

```bash
python scripts/launch_dashboards.py --auto-port --auto-ui-port --with-observability
```

Shortcut via Makefile:

```bash
make dashboards-all
```

Notes:

- This always starts Streamlit Cockpit.
- It starts API locally unless Compose API is available in observability mode, then it reuses Compose API.
- If `alertmanager`, `grafana`, and `prometheus` services exist in your compose file, it will start them too.
- If observability services are not configured yet, the command still launches Cockpit successfully.

Observability URLs after startup:

- Cockpit UI: `http://127.0.0.1:8501`
- ProjectRAG API: `http://127.0.0.1:8001`
- Grafana: `http://127.0.0.1:3001`
- Prometheus: `http://127.0.0.1:9091`
- Alertmanager: `http://127.0.0.1:9094`

Grafana credentials (local default):

- user: `admin`
- password: `admin`

Command to verify full stack quickly:

```bash
docker compose -f docker-compose.yml ps
```

Pre-provisioned Grafana dashboards:

1. Health and Availability
2. Latency p50/p95/p99 and Error Rate by Endpoint
3. Ingestion Throughput and Failure
4. Workflow and Agent Performance
5. Dependency Health (PostgreSQL, GraphDB, Ollama)

Prometheus alert rules now included in stack:

- API down (2m)
- high 5xx error rate > 2% (10m)
- query latency p95 > 5000ms (10m)
- ingestion failure rate > 10% (15m)

Alert routing is now enabled via Alertmanager:

- Slack receiver
- Teams receiver (webhook)
- Email receiver

Routing policy:

- `critical` alerts -> all channels (Slack + Teams + Email)
- `warning` alerts -> Slack + Teams
- `service=ingestion` alerts -> Email

Configuration file to edit with real credentials/webhooks:

- `deploy/monitoring/alertmanager/alertmanager.yml`

Recommended secret setup (do not hardcode real secrets in tracked files):

- copy local secret file:
  - `cp deploy/monitoring/alertmanager/alertmanager.local.example.yml deploy/monitoring/alertmanager/alertmanager.local.yml`
- put real Slack/Teams/SMTP values in `alertmanager.local.yml`
- local file is ignored by git (`.gitignore`)
- set this in `.env`:
  - `ALERTMANAGER_CONFIG_PATH=./deploy/monitoring/alertmanager/alertmanager.local.yml`

After editing receiver endpoints/credentials, apply updates:

```bash
docker compose -f docker-compose.yml up -d alertmanager prometheus
```

### Option B: Makefile commands

```bash
make up         # start Docker dependencies
make init-db    # initialize PostgreSQL schema (idempotent)
make db-upgrade # apply Alembic migrations
make api        # start FastAPI
make ui         # start Streamlit UI
```

### Option C: Docker Compose production-like run

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Then verify:

```bash
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/health/deep
```

## 3. How to Use ProjectRAG

### Basic operator flow

1. Start infrastructure and app.
2. Upload or ingest documents.
3. Ask questions via API or UI.
4. Review evidence, confidence, and validation.
5. Monitor workflow and agent runs in Audit panel.

### Core actions

- Upload document: `POST /documents/upload`
- Trigger ingestion: `POST /ingest`
- Ask a question: `POST /query`
- Explore graph facts: `POST /graph/query` or `GET /graph/export`
- Reindex a document: `POST /documents/{id}/reindex`
- Delete a document: `DELETE /documents/{id}`

### API version compatibility

Both paths are available:

- unversioned routes (for existing clients)
- `/api/v1/...` routes (for versioned clients)

## 4. Where We Can Use It

ProjectRAG is best for local-first or controlled infrastructure environments where data privacy matters.

### Typical environments

- engineering teams managing architecture/runbooks/internal docs
- operations and SRE teams for topology and dependency reasoning
- security/governance teams requiring auditability and traceability
- private on-prem or restricted cloud workloads that cannot expose docs externally

### Good use cases

- impact analysis ("if service X fails, what depends on it?")
- architecture Q&A from internal documentation
- dependency mapping from text and topology documents
- evidence-backed answers with confidence and validation signals
- workflow-level audit for operational and governance review

## 5. Production Implementation Guide

### Recommended production baseline

1. Containerize and run with `docker-compose.prod.yml` (or Kubernetes manifests in `deploy/k8s/`).
2. Keep data services persistent (PostgreSQL volume, GraphDB volume).
3. Apply Alembic migrations on deploy (`alembic upgrade head`).
4. Configure environment variables from secure runtime secrets (not git).
5. Enable health and metrics scraping (`/health`, `/health/deep`, `/metrics`).
6. Wire OpenTelemetry endpoint when tracing is enabled.
7. Use reverse proxy/TLS and network policies for external exposure.
8. Back up PostgreSQL and GraphDB regularly; test restore.

### Production checklist (minimum)

- `.env` not committed and no real secrets in repo
- dependencies pinned and reviewed
- `pytest -v` green before release
- health checks green after deploy
- ingestion limits configured (`MAX_UPLOAD_BYTES`, `MAX_FILES_PER_INGEST_RUN`)
- observability active (logs + metrics + traces)
- incident/rollback procedure documented

## 6. Practical Value After Implementation

Once implemented and operating, teams can practically do the following:

- answer operational questions faster with grounded evidence
- reduce mean time to understand service dependencies
- run safer changes by checking graph and workflow audit history
- centralize knowledge from runbooks, architecture docs, and topology files
- provide explainable outputs for technical and governance stakeholders
- monitor whether system quality gates are passing over time

## 7. Day-2 Monitoring Model

Use three layers together:

- Service health:
  - `/health` for liveness
  - `/health/deep` for dependency state
- Metrics:
  - `/metrics` for Prometheus scraping
  - OTEL pipeline when enabled
- Operational audit:
  - Streamlit Audit tab for workflow/agent/validation visibility
  - API routes for automation and external dashboards

## 8. Recommended Daily Routine

1. Check `/health/deep`.
2. Open Cockpit and Audit tabs.
3. Review failed workflows and validation warnings.
4. Review ingestion activity and document index state.
5. Verify backups are being generated.

## 9. Fast Troubleshooting

- UI says API offline:
  - run `python scripts/launch_app.py --with-ui --auto-port --auto-ui-port`
  - set sidebar FastAPI URL to printed API address
- Port in use:
  - use `--auto-port` and `--auto-ui-port`
- Dependency degraded:
  - inspect `docker compose logs -f`
  - check PostgreSQL, GraphDB, and Ollama availability

### 9.1 Verify Durable Retry Scheduling (`next_retry_at`)

Use this sequence to verify retry persistence and exponential backoff in a live environment.

1. Confirm migrations are applied:

```bash
source .venv/bin/activate
alembic upgrade head
alembic current
```

Expected output pattern:

- current revision is `0003_workflow_ckpt_retry (head)`

2. Confirm Alembic version row length is safe:

```bash
python - <<'PY'
from app.memory.postgres import fetch_all
rows = fetch_all("SELECT version_num, length(version_num) FROM alembic_version")
print(rows)
PY
```

Expected output pattern:

- `version_num` is `0003_workflow_ckpt_retry`
- `length` is `24` (must be <= 32)

3. Run a live failure-to-retry demo (forces two failures and prints state):

```bash
python -m scripts.verify_retry_backoff
# or via Makefile
make verify-retry-backoff
```

Expected output pattern:

- attempt 1: job transitions to `retrying`, `attempts=1`, `next_retry_at` is set
- attempt 2: job remains `retrying`, `attempts=2`, `next_retry_at` moves further into the future
- printed checks include `backoff_increased: True`
- printed `result` is `PASS`

4. Optional: run worker continuously for short monitoring window:

```bash
python -m scripts.run_background_worker --worker-id projectrag-worker-1 --poll-interval 1 --max-iterations 6
```

Expected output pattern:

- worker starts and stops cleanly
- summary counters include `iterations`, `processed`, `skipped`, `failed`, `idle_cycles`

### 9.2 PR Smoke CI Lane (Retry Backoff)

Pull requests now run a dedicated smoke workflow that validates retry durability against live PostgreSQL:

- Workflow: `.github/workflows/ci.yml`
- Job: `retry-backoff-smoke`
- Steps: PostgreSQL service -> `alembic upgrade head` -> `python -m scripts.verify_retry_backoff`

Python lanes:

- `3.12` is blocking (required to pass)
- `3.13` is non-blocking (informational/early warning lane)

Interpretation:

- If `3.12` fails, treat as merge-blocking and fix before merge.
- If only `3.13` fails, merge can proceed, but create a follow-up issue for compatibility.

## 10. Key Project References

- `scripts/launch_app.py`
- `scripts/verify_retry_backoff.py`
- `ui/streamlit_app.py`
- `app/main.py`
- `app/api/routes_workflow_audit.py`
- `docs/deployment_local_docker.md`
- `docs/production_checklist.md`
- `docs/operations_runbook.md`
- `docker-compose.yml`
- `docker-compose.prod.yml`

## 11. Remaining Work Plan: UX + Automated Ops

This is the practical backlog to move from a strong MVP to production-grade operator experience.

### A) UX Polishing Backlog (High Priority)

1. Dashboard clarity and readability
  - Add a top-level status strip in Cockpit: API, DB, GraphDB, Ollama, ingestion queue, last successful workflow.
  - Add color-consistent severity levels: info/warn/error/critical.
  - Show timestamps in local timezone and relative format (for example "5 minutes ago").

2. Query and evidence usability
  - Add "copy answer" and "copy citations" actions.
  - Add response quality badges: grounded, confidence band, validation pass/fail.
  - Add empty-state guidance for missing evidence and no-ingestion scenarios.

3. Document operations UX
  - Add ingestion progress indicator and final summary card.
  - Add clear user-facing errors for size/file limits and supported file types.
  - Add bulk actions: reindex selected, delete selected, and safe confirmation dialogs.

4. Audit workflow UX
  - Add filters by date range, workflow status, and agent name.
  - Add details drawer per workflow with full run timeline.
  - Add CSV export button for workflow, agent, and validation tables.

### B) Automated Ops Dashboards (Prometheus/Grafana)

1. Add a Grafana service for local and production-like monitoring.
2. Create starter dashboards:
  - API health and request rate
  - query latency percentiles (p50, p95, p99)
  - error rate by endpoint
  - ingestion throughput and failure rate
  - workflow volume and failure ratio
  - agent run latency and failure ratio
3. Add service dependency dashboard:
  - PostgreSQL availability and connection errors
  - GraphDB availability and query latency
  - Ollama availability and generation latency
4. Add dashboard links into Streamlit Audit tab for fast operator handoff.

### C) Alerting Rules (Actionable)

Define alerts with thresholds and clear runbooks:

- API down: `/health` failing for 2 minutes.
- Dependency degraded: `/health/deep` status is degraded for 5 minutes.
- High error rate: 5xx > 2% over 10 minutes.
- High query latency: p95 `query` duration > 5s for 10 minutes.
- Ingestion failures: failure rate > 10% over 15 minutes.
- Workflow failure spike: failed workflows > 5 in 15 minutes.
- Agent failure spike: failed agent runs > 10 in 15 minutes.
- No backups generated in expected window.

Each alert should include:

- severity (warning/critical)
- service ownership
- immediate triage steps
- rollback or mitigation action
- link to runbook section

### D) 30-Day Implementation Sequence

Week 1

- UX quick wins in Streamlit (status strip, error messages, filters, exports).
- Add missing API fields needed by UI cards if required.

Week 2

- Stand up Grafana and import base dashboards.
- Validate metrics naming and cardinality.

Week 3

- Implement alert rules and notification routing.
- Write incident response playbooks for top 5 alerts.

Week 4

- Run game-day simulations (dependency down, high latency, ingestion failures).
- Tune thresholds to reduce noise and improve signal.
- Final operator acceptance review.

### E) Definition of Done for This Remaining Work

- Operators can identify failures in under 2 minutes.
- Root cause triage starts in under 10 minutes using dashboards/runbooks.
- Dashboard covers API, dependencies, ingestion, workflows, and agents.
- Alerts are actionable and linked to documented runbooks.
- UX flows are clear enough for non-developer operators.
