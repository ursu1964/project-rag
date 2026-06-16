# ProjectRAG MVP Acceptance Criteria

## Infrastructure

- Docker Compose starts PostgreSQL and GraphDB successfully.
- PostgreSQL schema initializes with `scripts/init_postgres.sql`.
- Ollama is reachable from the local environment.

## RAG

- A text document ingests from `data/raw`.
- Document chunks are stored in PostgreSQL.
- Embeddings are stored with chunks using pgvector.
- Vector search returns relevant chunks.

## GraphRAG

- Entities are extracted from ingested text.
- Relationships are extracted from ingested text.
- RDF triples are inserted into GraphDB.
- Graph queries return relationships.
- Graph facts are also stored in PostgreSQL for provenance/auditability.

## API

- `GET /health` works.
- `POST /query` works.
- `GET /documents` works.
- `POST /ingest` works.
- `POST /graph/query` works.

## Agents

- Router selects an appropriate route.
- Memory agent runs.
- Vector retriever runs.
- Graph retriever runs.
- Reasoner returns an answer.
- Validator returns confidence and approval status.

## Safety

- Execution is disabled by default.
- High-risk questions require human approval.

## Testing

- `pytest` passes.
