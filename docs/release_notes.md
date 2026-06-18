# Release Notes

## v0.1.0-local-graphrag-mvp

### Features

- Local-first ProjectRAG MVP foundation.
- FastAPI API layer with health, query, document, graph, memory, DevOps, and cognitive endpoints.
- LangGraph RAG workflow orchestration.
- PostgreSQL + pgvector schema for documents, chunks, memory, workflow logs, validation, graph facts, and audit-oriented tables.
- GraphDB integration for entity and relationship triples.
- Ollama integration for local embeddings and generation.
- Text document ingestion from `data/raw`.
- Deterministic entity and relationship extraction for infrastructure topology examples.
- Vector, graph, memory, hybrid retrieval, reranking, context merging, and validation pipeline.
- Read-only/tool-governance foundations with dangerous actions blocked by default.
- Streamlit UI for question answering, evidence display, uploads, ingestion, document listing, and graph fact queries.
- Local smoke-test, troubleshooting, operations, backup, architecture, and guardrail documentation.

### Known Limitations

- MVP quality only; not production-hardened.
- GraphDB repository must exist or be initialized before reliable graph ingestion/querying.
- Vector retrieval quality depends on local Ollama embedding model availability and ingested data.
- No autonomous infrastructure execution; execution is intentionally disabled.
- No real cloud inventory API calls; cloud connectors are skeletons or JSON/import based.
- Authentication/RBAC is local-development foundation only.
- Evaluation metrics are baseline and may report low vector usage until documents are ingested and indexed.
- SQL schema is idempotent but not yet managed by a migration framework.

### Setup Requirements

- Python 3.12 recommended.
- Docker and Docker Compose.
- PostgreSQL with pgvector via `docker-compose.yml`.
- GraphDB via `docker-compose.yml`.
- Ollama running locally.
- Required Ollama models:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Typical local startup:

```bash
make install
make up
make init-db
python -m scripts.init_graphdb_repository
make ingest
make api
make ui
```

### Test Status

Current expected baseline:

```bash
pytest -q
```

The repository includes unit tests plus clearly marked external-dependency/e2e tests. External tests require live PostgreSQL, GraphDB, Ollama, and the FastAPI service where applicable.

### Delayed Scope

The following are explicitly delayed until MVP stability is proven:

- Autonomous execution.
- Terraform apply/destroy.
- Kubernetes deployment and mutation.
- Cloud resource modification.
- Production AGII behavior.
- Recursive self-evolution or automatic code deployment.
- Artificial CEO/CTO/COO production decision logic.
- Distributed cluster execution.
- Full authentication provider integration.
