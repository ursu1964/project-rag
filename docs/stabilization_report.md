# ProjectRAG Stabilization Report

Date: 2026-06-16

## Scope

Reviewed the current ProjectRAG repository without adding new product features. Focus areas:

- Imports
- Tests
- Docker Compose
- PostgreSQL schema
- GraphDB connection
- Ollama connection
- FastAPI routes
- LangGraph workflow
- `.env` usage
- `.gitignore` security

## Summary

ProjectRAG is stable enough for local MVP testing after two blocking issues were addressed:

1. FastAPI route introspection failed under the Python 3.12 virtual environment because included router sentinel objects did not expose `.path`.
2. `/health/deep` test failed because the response included an extra `service` field not expected by the existing test contract.

After fixes, the test suite passes.

## Validation Results

### Imports

Command:

```bash
python -m compileall -q app scripts tests
```

Result: **PASS**

No import/syntax failures were found.

### Tests

Command:

```bash
/home/RAG/.venv/bin/python -m pytest -q
```

Result: **PASS**

```text
184 passed in 1.37s
```

A secondary run under the ambient Python environment also passed after the health route contract fix:

```text
184 passed, 2 warnings
```

Warnings observed in the ambient Python environment were external package warnings from pandas optional dependencies (`numexpr`, `bottleneck`) during chaos tests. They are not blocking ProjectRAG tests.

### Docker Compose

Command:

```bash
docker compose config
```

Result: **PASS**

Validated services:

- `postgres`: `pgvector/pgvector:pg16`
- `graphdb`: `ontotext/graphdb:10.8.6`

Current resolved PostgreSQL host mapping:

```text
5433 -> 5432/tcp
```

This avoids conflict with a host PostgreSQL service on port `5432`.

Runtime check:

```bash
docker compose ps
```

Result: **PASS**

Observed:

- `projectrag-postgres`: running and healthy
- `projectrag-graphdb`: running

### PostgreSQL Schema

Reviewed:

```text
scripts/init_postgres.sql
```

Result: **PASS**

Schema includes:

- `CREATE EXTENSION IF NOT EXISTS vector;`
- `documents`
- `chunks` with `embedding vector(768)`
- `memory_items`
- `workflow_runs`
- `agent_runs`
- `validation_results`
- `graph_facts`
- `evaluation_results`
- `experience_runs`
- `experience_steps`
- `experience_outcomes`

Required indexes are present for documents, chunks, memory, workflow, agent, graph fact, evaluation, and experience tables.

Live PostgreSQL check:

```python
SELECT 1 AS ok
```

Result: **PASS**

```text
[RealDictRow({'ok': 1})]
```

### GraphDB Connection

Command:

```bash
curl http://localhost:7200/rest/repositories
```

Result: **PASS**

Observed repository:

```text
projectrag RUNNING writable=true
```

GraphDB repository bootstrap support is present through:

```text
scripts/init_graphdb_repository.py
app/graph/graphdb_client.py:create_repository()
```

### Ollama Connection

Command:

```bash
curl http://localhost:11434/api/tags
```

Result: **PASS**

Observed local models include:

- `nomic-embed-text:latest`
- `llama3.1:8b`

### FastAPI Routes

Validated application creation and OpenAPI route registration.

Observed routes:

```text
/health
/health/deep
/metrics
/query
/documents
/documents/upload
/ingest
/devops/inventory/import
/graph/query
/memory
/memory/search
/cognitive/query
```

Runtime check with Uvicorn on port `8022`:

```bash
curl http://127.0.0.1:8022/health
```

Result: **PASS**

```json
{"status":"ok","service":"ProjectRAG"}
```

### LangGraph Workflow

Reviewed:

```text
app/workflows/rag_workflow.py
```

RAG workflow order:

```text
router -> memory -> vector -> graph -> merge -> compress -> reason -> validate -> END
```

Result: **PASS**

Workflow construction is covered by tests and passed.

### `.env` Usage

Reviewed:

```text
app/core/config.py
.env.example
```

Result: **PASS with note**

The config now resolves `.env` from the project root instead of depending on the process working directory. This prevents Uvicorn reloaders or external launchers from accidentally loading defaults.

Current effective settings observed:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=projectrag
POSTGRES_USER=projectrag
GRAPHDB_URL=http://localhost:7200
GRAPHDB_REPOSITORY=projectrag
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EMBEDDING_MODEL=nomic-embed-text
```

### `.gitignore` Security

Reviewed:

```text
.gitignore
```

Result: **PASS**

Protected paths/patterns include:

- `.venv/`
- `.env`
- `.env.*`
- `!.env.example`
- `__pycache__/`
- `.pytest_cache/`
- `data/raw/`
- `!data/raw/*.example`
- `data/processed/`
- `data/private/`
- `data/exports/`
- `*.log`
- `backups/`
- `*.dump`
- `*.backup`

Secret scan command:

```bash
grep -R "api_key\|secret\|token\|password" . --exclude-dir=.venv --exclude-dir=.git --exclude=.env --exclude='*.pyc'
```

Result: **PASS with expected placeholder findings**

Findings are placeholders, documentation, or code references such as `projectrag_password`, `change-me-local-only`, and variable names. No real credentials were identified.

## Fixes Applied

### 1. FastAPI included-router compatibility

File:

```text
app/main.py
```

Problem:

Under the Python 3.12 virtual environment, `create_app().routes` contained FastAPI `_IncludedRouter` sentinel objects. These objects do not expose `.path`, causing route introspection tests to fail.

Fix:

Extended route expansion to support FastAPI's `original_router` attribute in addition to older router shapes.

Status: **FIXED**

### 2. Deep health response contract

File:

```text
app/api/routes_health.py
```

Problem:

`/health/deep` included `service`, but the existing test contract expected only dependency statuses and overall status.

Fix:

Removed the extra `service` field from the direct `deep_health()` return while keeping `/health` unchanged.

Status: **FIXED**

## Current Blocking Issues

None found after fixes.

## Non-Blocking Notes

1. The local Docker PostgreSQL port is configured as `5433` to avoid host conflicts. Keep `.env` aligned with Docker Compose when using the local port mapping.
2. GraphDB repository initialization is now available, but operators may still need to run:

   ```bash
   /home/RAG/.venv/bin/python -m scripts.init_graphdb_repository
   ```

   before first graph ingestion if the repository is absent.
3. Start Uvicorn from the project virtual environment to avoid missing dependencies:

   ```bash
   /home/RAG/.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
   ```

4. One ambient Python run emitted pandas optional-dependency warnings. The project virtual environment test run passed cleanly without those warnings.

## Recommended Stable Local Startup

```bash
cd /home/RAG/project-rag

docker compose up -d

docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql

/home/RAG/.venv/bin/python -m scripts.init_graphdb_repository

/home/RAG/.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Then verify:

```bash
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/health/deep
```

Expected deep-health response when all dependencies are running:

```json
{"status":"ok","postgres":"ok","graphdb":"ok","ollama":"ok"}
```
