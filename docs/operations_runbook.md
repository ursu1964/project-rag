# ProjectRAG Operations Runbook

## Daily Checks

### 1. Container status

```bash
docker ps
```

Expected containers:

- `projectrag-postgres`
- `projectrag-graphdb`

### 2. Docker Compose logs

```bash
docker compose logs --tail=100
```

Follow logs if investigating an issue:

```bash
docker compose logs -f
```

### 3. Basic health check

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok","service":"ProjectRAG"}
```

### 4. Deep health check

```bash
curl http://localhost:8000/health/deep
```

Expected all dependencies to report `ok`:

- `postgres`
- `graphdb`
- `ollama`

### 5. Database size check

```bash
docker exec -it projectrag-postgres psql -U projectrag -d projectrag -c "SELECT pg_size_pretty(pg_database_size('projectrag')) AS database_size;"
```

### 6. Document count check

```bash
docker exec -it projectrag-postgres psql -U projectrag -d projectrag -c "SELECT count(*) AS documents FROM documents;"
```

### 7. Chunk count check

```bash
docker exec -it projectrag-postgres psql -U projectrag -d projectrag -c "SELECT count(*) AS chunks FROM chunks;"
```

### 8. GraphDB query check

```bash
curl -X POST http://localhost:8000/graph/query \
  -H "Content-Type: application/json" \
  -d '{"query":"PREFIX project: <http://projectrag.local/> SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"}'
```

### 9. Backup commands

Create backup directory:

```bash
mkdir -p backups
```

PostgreSQL backup:

```bash
docker exec projectrag-postgres pg_dump -U projectrag -d projectrag > backups/projectrag_$(date +%Y%m%d_%H%M%S).sql
```

GraphDB data volume backup depends on deployment policy. For local Docker volume backup:

```bash
docker run --rm \
  -v project-rag_graphdb_data:/data:ro \
  -v "$PWD/backups:/backup" \
  alpine tar czf /backup/graphdb_$(date +%Y%m%d_%H%M%S).tgz -C /data .
```

## Weekly Checks

### Review logs

```bash
docker compose logs --since=168h > logs/weekly_docker.log
```

Review application/API logs if configured.

### Review failed workflows

```bash
docker exec -it projectrag-postgres psql -U projectrag -d projectrag -c "SELECT id, workflow_name, status, error, created_at FROM workflow_runs WHERE status <> 'completed' ORDER BY created_at DESC LIMIT 50;"
```

### Review validation warnings

```bash
docker exec -it projectrag-postgres psql -U projectrag -d projectrag -c "SELECT workflow_id, passed, details, created_at FROM validation_results WHERE passed = false OR details::text ILIKE '%warning%' ORDER BY created_at DESC LIMIT 50;"
```

### Review storage growth

```bash
docker exec -it projectrag-postgres psql -U projectrag -d projectrag -c "SELECT relname AS table, pg_size_pretty(pg_total_relation_size(relid)) AS size FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;"
```

## Monthly Checks

### Backup restore test

Test restoring the latest PostgreSQL backup into a disposable local database/container before relying on it for recovery.

Example outline:

```bash
# Create a temporary database/container or local restore target.
# Restore the selected backup.
# Verify documents, chunks, graph_facts, workflow_runs counts.
```

### Dependency review

```bash
pip list --outdated
```

Review updates carefully before changing pinned or production dependencies.

### Security review

Check for accidental secrets or sensitive data:

```bash
git status
grep -R "api_key\|secret\|token\|password" . --exclude-dir=.venv --exclude=.env --exclude-dir=.git
```

Confirm local data and secrets are not tracked:

```bash
git ls-files .env 'data/raw/*' 'data/private/*' '*.log'
```

Expected: no real `.env`, private data, raw data, or logs tracked.
