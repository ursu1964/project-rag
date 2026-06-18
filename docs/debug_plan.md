# ProjectRAG Debug Plan

Generated: 2026-06-17

## Validation Snapshot

Commands run:

```bash
git status --short
/home/RAG/.venv/bin/python -m pytest -q
docker compose config
docker compose -f docker-compose.prod.yml config
/home/RAG/.venv/bin/python -m compileall -q app scripts tests ui
docker compose ps
curl-equivalent checks for /health, GraphDB, and Ollama
```

Current results:

- Unit/non-external tests: `286 passed, 1 skipped`.
- Python compile check: passed.
- Docker Compose config validation: passed for local and prod compose files.
- Running containers: PostgreSQL healthy on host port `5433`; GraphDB running on `7200`.
- Runtime health checks:
  - `/health`: ok
  - `/health/deep`: ok
  - GraphDB repository: reachable
  - Ollama API: reachable

## Confirmed Gaps

### 1. Data ingestion is partially inconsistent

Metrics show:

| Metric | Value |
|---|---:|
| Documents | 1 |
| Chunks | 0 |
| Graph facts | 0 |
| Workflow runs | 11 |
| Average validation confidence | 0.200 |

This means a document row exists, but no chunks or graph facts exist.

Likely cause: an earlier ingestion run registered the document, then failed during GraphDB insertion before chunk insertion. Subsequent ingestion skips the file as a duplicate because `documents.file_hash` already exists.

Impact:

- Vector retrieval has no chunks to retrieve.
- Graph export returns no nodes/edges.
- `/query` returns low-confidence answers despite route/workflow being functional.

### 2. `/query` workflow is functional but evidence is empty

Smoke query:

```text
What does VM1 depend on?
```

Observed:

- HTTP 200
- route: `hybrid`
- validation confidence: `0.2`
- warning: `missing_evidence`
- graph context entity: `VM1`
- graph outgoing/incoming/path facts: empty

Impact:

- API is alive, but RAG quality is not acceptable until data is re-ingested correctly.

### 3. Graph visualization endpoint works structurally, but no graph data exists

`GET /graph/export?limit=20` returns:

```json
{
  "nodes": [],
  "edges": []
}
```

Impact:

- UI/frontend graph rendering will show an empty graph until `graph_facts` is populated.

### 4. Docker/API port conflicts remain an operational risk

Previous logs showed repeated `Errno 98 address already in use` on port `8000`.

Impact:

- Starting Uvicorn manually can fail if a previous Uvicorn or Docker API container is already bound to the port.

### 5. Repository hygiene risk: many untracked files

`git status --short` shows many untracked files from recent implementation work, including `.vscode/`.

Impact:

- Before commit, review untracked files carefully.
- `.vscode/` should usually be ignored unless intentionally shared.

### 6. Local placeholder password is present in config/compose

`projectrag_password` exists as local placeholder configuration.

Impact:

- Acceptable for local MVP only.
- Must be overridden in real environments via `.env` or secret manager.

## Debug Plan

### Phase 1: Confirm runtime baseline

```bash
docker compose ps
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/deep
curl http://127.0.0.1:7200/rest/repositories
curl http://127.0.0.1:11434/api/tags
```

Pass criteria:

- PostgreSQL container is healthy.
- GraphDB responds and contains repository `projectrag`.
- Ollama lists `llama3.1:8b` and `nomic-embed-text`.
- `/health/deep` returns all dependencies as `ok`.

### Phase 2: Inspect database state

```bash
python -m scripts.generate_metrics_report
cat docs/metrics_report.md
```

Expected for a useful demo:

- documents >= 1
- chunks >= 1
- graph_facts >= 1
- workflow_runs can be any number
- average validation confidence should improve after evidence exists

### Phase 3: Repair partial ingestion state safely

For the current sample document, the safe choices are:

1. Preferred for development: use a new sample filename or slightly changed file content so it is not treated as duplicate.
2. If intentionally resetting local demo data, delete only local demo rows from PostgreSQL after backing up. Do not do this for user data.
3. Longer-term code fix: make ingestion transactional or allow a `force_reingest` path that fills missing chunks/graph facts for an already registered document.

Debug command after choosing a safe reset/retry strategy:

```bash
python -m scripts.ingest_documents
python -m scripts.generate_metrics_report
```

Pass criteria:

- chunks > 0
- graph_facts > 0

### Phase 4: Validate graph extraction and export

```bash
curl http://127.0.0.1:8000/graph/export?limit=20
python -m scripts.query_graph
```

Pass criteria:

- `/graph/export` returns nodes including `VM1`, `Database01`, `SubnetA`, etc.
- Edges include relationships such as `dependsOn`, `connectedTo`, `protectedBy`.

### Phase 5: Validate query quality

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What does VM1 depend on?"}'
```

Pass criteria:

- route is `graph` or `hybrid`.
- graph evidence is non-empty.
- answer mentions `Database01` for the sample topology.
- validation confidence improves above the current `0.2` baseline.

### Phase 6: Validate UI

```bash
make ui
```

Pass criteria:

- Sidebar health shows API available.
- Documents tab lists ingested documents.
- Graph tab shows graph facts via `/graph/query`.
- Query tab shows answer, route, confidence, and evidence.

### Phase 7: Prevent recurrence

Recommended engineering fixes after debugging:

1. Make ingestion atomic: document registration, graph ingestion, chunk embedding, and chunk insertion should either complete together or mark a partial/failed state.
2. Add an ingestion repair path: if document exists but chunks or graph facts are missing, allow controlled reprocessing.
3. Add an ingestion status field to `documents` or a separate ingestion runs table.
4. Update metrics report to flag `documents > 0 AND chunks = 0` as a warning.
5. Add `/graph/export` to API route tests and smoke docs.
6. Add `.vscode/` to `.gitignore` unless workspace settings are intentionally shared.

## Priority Order

1. Fix/retry ingestion data state.
2. Confirm chunks and graph facts are populated.
3. Re-test `/query` quality.
4. Re-test Streamlit UI.
5. Clean up untracked files and ignore local IDE settings.
6. Only then prepare commit/release.
