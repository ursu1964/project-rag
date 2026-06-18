# ProjectRAG

[![CI](https://github.com/ursu1964/project-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/ursu1964/project-rag/actions/workflows/ci.yml)

> **PR Smoke Check**: Pull requests run `retry-backoff-smoke` (Python 3.12 blocking, 3.13 informational). See [operations guide](PROJECTRAG_QUICK_OPERATIONS_GUIDE.md#92-pr-smoke-ci-lane-retry-backoff) for details.

ProjectRAG is a local-first GraphRAG platform for ingesting project documents, extracting infrastructure/application relationships, and answering grounded questions using local retrieval, graph context, and local LLM inference.

The MVP is designed for private engineering knowledge bases, architecture notes, topology files, runbooks, and internal documentation where data should stay on the developer machine or controlled local infrastructure.

## Architecture Summary

ProjectRAG combines vector retrieval, graph retrieval, memory, validation, and agent orchestration:

- **FastAPI** exposes health, query, ingestion, document, and graph endpoints.
- **LangGraph** orchestrates RAG and cognitive multi-agent workflows.
- **PostgreSQL + pgvector** stores documents, chunks, embeddings, memory items, workflow runs, agent runs, and validation results.
- **GraphDB** stores extracted entities and relationships as RDF triples.
- **Ollama** provides local LLM generation and embeddings.
- **Python agents** replace external workflow tools and keep orchestration inside the codebase.

## Local-First Design

ProjectRAG is intended to run locally by default:

- Local PostgreSQL/pgvector via Docker Compose
- Local GraphDB via Docker Compose
- Local Ollama models for LLM and embedding calls
- No required cloud APIs
- No real credentials committed to the repository

## No-n8n Decision

ProjectRAG does **not** use n8n. Workflow automation is implemented with Python agents and LangGraph so that behavior is testable, version-controlled, and fully local-first.

## Main Stack

- FastAPI
- LangGraph
- PostgreSQL + pgvector
- GraphDB
- Ollama
- pytest

## Folder Structure

```text
app/
  api/          FastAPI route modules
  agents/       RAG, validation, cognitive, and orchestration agents
  core/         Configuration
  graph/        GraphDB client, SPARQL templates, entity/relationship extraction
  memory/       PostgreSQL client and workflow/audit stores
  rag/          Chunking, ingestion, document registry, vector store, scoring
  tools/        Ollama client
  workflows/    LangGraph workflow definitions
data/
  raw/          Local input documents, ignored by git
  processed/    Local processed files, ignored by git
  private/      Private local data, ignored by git
  exports/      Local exports, ignored by git
docs/           Project documentation
scripts/        CLI helper scripts
tests/          pytest test suite
```

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create local environment configuration:

```bash
cp .env.example .env
```

Edit `.env` if your local ports or model names differ.

## Start Local Infrastructure

```bash
docker compose up -d
```

This starts:

- PostgreSQL with pgvector on port `5432`
- GraphDB on port `7200`

## Initialize PostgreSQL

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

## Alembic Migrations

ProjectRAG now includes Alembic baseline migration scaffolding.

- Use `PROJECTRAG_DATABASE_URL` to override database URL when needed.
- Otherwise Alembic reads database settings from `app/core/config.py`.

Run migrations:

```bash
alembic upgrade head
```

Check current revision:

```bash
alembic current
```

## Start Ollama and Pull Models

In a separate terminal:

```bash
ollama serve
```

Pull the default local models:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

## Ingest Documents

Place `.txt` files in `data/raw/`, then run:

```bash
python -m scripts.ingest_documents
```

Ingestion will:

- Read `.txt` files
- Hash files and skip duplicates
- Chunk text
- Create embeddings with Ollama
- Store chunks in PostgreSQL/pgvector
- Extract entities and relationships
- Insert graph triples into GraphDB

## Start the API

Use port `8001` by default unless you intentionally free `8000` for ProjectRAG.

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Health Check

```bash
curl http://localhost:8001/health
```

Expected response:

```json
{"status":"ok","service":"ProjectRAG"}
```

## Example Query

```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What does VM1 depend on?"}'
```

The response returns the full workflow state, including route, retrieved context, compressed context, answer, validation, and workflow id.

## Graph Query Script

```bash
python -m scripts.query_graph
```

## Run Tests

```bash
pytest -q
```

## Security Notes

- Do not commit `.env`.
- Do not place real credentials in the repository.
- `.env.example` contains only local placeholder values.
- Local data directories are ignored by git:
  - `data/raw/`
  - `data/processed/`
  - `data/private/`
  - `data/exports/`
- Generated logs are ignored.
- Execution agents are disabled by default until an explicit approval mode exists.
- The security agent blocks execution by default in the cognitive workflow.
