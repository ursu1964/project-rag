# Local Docker Deployment

This guide runs ProjectRAG locally with Docker Compose for PostgreSQL/pgvector, GraphDB, and the FastAPI app.

## Prerequisites

- Docker and Docker Compose installed.
- Ollama installed on the host.
- `.env` created from `.env.example`.
- No real secrets committed to the repository.

```bash
cp .env.example .env
```

Adjust ports in `.env` if your machine already uses `5432`, `7200`, or `8000`.

## Build the FastAPI Image

```bash
docker compose -f docker-compose.prod.yml build projectrag-api
```

Or build directly:

```bash
docker build -t projectrag-api:local .
```

## Start Compose

```bash
docker compose -f docker-compose.prod.yml up -d
```

Check containers:

```bash
docker compose -f docker-compose.prod.yml ps
```

View logs:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

## Initialize PostgreSQL

After PostgreSQL is healthy, initialize the schema:

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

The schema script is idempotent and can be rerun safely.

## Initialize GraphDB Repository

If the `projectrag` repository does not exist, create it:

```bash
python -m scripts.init_graphdb_repository
```

Then verify GraphDB:

```bash
curl http://localhost:7200/rest/repositories
```

## Pull Ollama Models

Run Ollama on the host:

```bash
ollama serve
```

In another terminal, pull the required models:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Verify Ollama:

```bash
curl http://localhost:11434/api/tags
```

## Run Health Checks

Basic app health:

```bash
curl http://127.0.0.1:8000/health
```

Dependency health:

```bash
curl http://127.0.0.1:8000/health/deep
```

Expected result is `status: ok`. If one dependency is down, `/health/deep` returns `degraded` with an error message.

## Optional Smoke Test

Create sample data in `data/raw/topology_example.txt`, then ingest:

```bash
make ingest
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What does VM1 depend on?"}'
```

## Troubleshoot Ports

### Port Already in Use

Find the process:

```bash
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :7200
```

Stop the conflicting process or change the port in `.env`.

Common alternatives:

```env
APP_PORT=8001
POSTGRES_PORT=5433
```

Then restart:

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### PostgreSQL Connection Refused

Check container state:

```bash
docker compose -f docker-compose.prod.yml ps projectrag-postgres
```

Check logs:

```bash
docker logs projectrag-postgres
```

Confirm your API uses the container hostname in Docker:

```env
POSTGRES_HOST=projectrag-postgres
```

For host-based local development, use:

```env
POSTGRES_HOST=localhost
```

### GraphDB Not Reachable

Check logs:

```bash
docker logs projectrag-graphdb
```

Verify endpoint:

```bash
curl http://localhost:7200/rest/repositories
```

### Ollama Not Reachable from API Container

If the API runs in Docker and Ollama runs on the host, `localhost` inside the container points to the container itself. Configure a host-accessible Ollama URL if needed, for example:

```env
OLLAMA_URL=http://host.docker.internal:11434
```

On Linux, you may need an additional Docker host-gateway mapping before this works.
