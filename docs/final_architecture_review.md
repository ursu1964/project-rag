# ProjectRAG Final Architecture Review

## Current Architecture

ProjectRAG is a local-first GraphRAG MVP built around a modular Python backend.

Core architecture:

- **FastAPI** API layer for health, query, ingestion, graph, memory, DevOps inventory, cognitive workflow, and metrics endpoints.
- **LangGraph** workflow orchestration for RAG and cognitive multi-agent flows.
- **PostgreSQL + pgvector** for documents, chunks, embeddings, memory, workflow logs, validation results, graph fact provenance, evaluation results, and experience tables.
- **GraphDB** for RDF triples and SPARQL graph queries.
- **Ollama** for local embeddings, generation, optional LLM routing, and optional LLM judging.
- **Python agents** for routing, retrieval, graph traversal, context merging, reasoning, validation, topology analysis, cost/resource estimation, recommendations, learning, and cognitive orchestration.
- **Repository layer** introduced for key persistence areas to prepare for future SQLAlchemy migration.

The system is intentionally local-first and does not use n8n or cloud APIs by default.

## Implemented Components

### API Layer

Implemented endpoints include:

- `GET /health`
- `GET /health/deep`
- `GET /metrics`
- `POST /query`
- `GET /documents`
- `POST /documents/upload`
- `POST /ingest`
- `POST /graph/query`
- `GET /memory`
- `POST /memory`
- `GET /memory/search`
- `POST /devops/inventory/import`
- `POST /cognitive/query`

### RAG Layer

Implemented:

- File hashing and duplicate detection.
- Text chunking.
- Ollama embedding creation.
- pgvector chunk storage and similarity search.
- Deterministic reranking.
- Context compression.
- Evidence scoring and merging.

### GraphRAG Layer

Implemented:

- Regex entity extraction.
- Regex relationship extraction.
- Turtle triple generation.
- GraphDB insertion.
- SPARQL query templates.
- Incoming/outgoing relationship retrieval.
- Impact and traversal helpers.
- PostgreSQL graph fact provenance.
- Ontology documentation and relation validation.

### Memory Layer

Implemented:

- Conversation/session/project/knowledge/ontology memory types.
- Memory search and recent memory listing.
- Knowledge memory store.
- Ontology memory store.
- Experience tables for future learning loops.

### Agents

Implemented agents include:

- Router agent with deterministic default and optional LLM routing.
- Query planner.
- Memory agent.
- Vector retriever.
- Graph retriever.
- Context merger.
- Context compressor.
- Reasoner.
- Validator.
- Topology agent.
- Chief/planning/security/cost/execution/learning agents.
- Recommendation agent.
- Resource allocator.

### DevOps and Connectors

Implemented:

- DevOps inventory models.
- JSON inventory importer.
- Topology importer for AWS/Azure/VMware-shaped inventories.
- AWS connector skeleton.
- Azure connector skeleton.
- No cloud credentials or API calls.

### Validation and Evaluation

Implemented:

- Deterministic safety checks.
- Hallucination detector.
- Optional LLM judge.
- Evaluation metrics: groundedness, answer completeness, graph usage, hallucination rate, citation coverage.
- Evaluation result storage.

### Operations

Implemented:

- Docker Compose for PostgreSQL + GraphDB.
- PostgreSQL schema initialization.
- Makefile commands.
- Backup scripts.
- Local smoke test guide.
- Troubleshooting guide.
- Operations runbook.
- Acceptance criteria.
- GitHub Actions CI.

## Missing Components

### Production Migrations

The schema is currently managed by one large idempotent SQL script. There is no migration framework such as Alembic. This will become painful as schema changes accumulate.

### Authentication and Authorization

The API currently has no authentication, no API keys, no RBAC, and no per-endpoint authorization. This is acceptable for local-only MVP use but not production-safe.

### Real Upload Integration Tests

Upload logic is covered at function level, but full multipart API integration is not deeply tested in the runtime environment because `python-multipart` may not be installed in the current interpreter.

### Durable Workflow State

LangGraph workflows are compiled and invoked per request. There is no durable checkpointer or replayable graph state yet.

### GraphDB Repository Provisioning

Docker starts GraphDB, but repository creation/configuration is not automated. Operators may need manual setup depending on GraphDB defaults.

### True Vector Search Validation

pgvector SQL is implemented, but most tests mock database calls. There is no integration test that validates actual vector inserts/searches against a live PostgreSQL container.

### Robust Entity Extraction

Entity and relationship extraction is deterministic regex-based. It is transparent and testable but brittle for natural language, multiline diagrams, tables, YAML, Terraform, Kubernetes manifests, and ambiguous entity names.

### Advanced Graph Traversal

Traversal helpers exist, but impact queries are still shallow and SPARQL templates are basic. Depth handling is currently bounded but not fully expressed in recursive graph traversal logic.

### Multi-Tenant or Multi-Project Isolation

No tenant, workspace, project, or namespace model exists yet. All data lands in shared tables and graph namespace.

### Secrets Management

The repository avoids real secrets, but runtime secret management is not implemented. `.env` is the only supported configuration mechanism.

## Technical Debt

1. **Python version mismatch risk**: CI targets Python 3.12, but local validation was performed under Python 3.9 in this environment. Code includes compatibility fixes, but the production target should be validated with Python 3.12.
2. **Repository pattern is partial**: Documents, chunks, memory, and workflows have repositories, but graph facts, evaluation, and some health SQL still use direct persistence helpers.
3. **Large SQL script**: `scripts/init_postgres.sql` is growing and should be replaced or complemented by migrations.
4. **Inconsistent response typing**: Some API responses are schema-based, while others return raw dictionaries for flexibility.
5. **Pydantic models are not centralized everywhere**: Some route-local request schemas remain.
6. **Graph ontology is not enforced everywhere**: Graph ingestion validates relation types, but topology import can still insert predicates not checked against ontology.
7. **Testing is broad but mostly unit-level**: Integration coverage with real PostgreSQL, GraphDB, and Ollama is still missing.
8. **Mock-heavy confidence**: Passing tests prove interfaces and deterministic logic, not full runtime interoperability.
9. **Potential duplicate concepts**: Memory, graph facts, knowledge store, ontology store, and experience store overlap conceptually and need clearer boundaries.
10. **No structured error model**: API errors rely mostly on FastAPI defaults and generic exceptions.

## Security Concerns

1. **No API authentication**: Any local caller can query, ingest, upload, or import inventory.
2. **No rate limiting**: Query and ingestion endpoints can be abused locally and exhaust Ollama/CPU/GPU resources.
3. **SPARQL endpoint proxy risk**: `/graph/query` accepts raw SPARQL and forwards it to GraphDB. This is useful for local development but risky if exposed.
4. **Upload size limits missing**: File upload path safety exists, but there is no maximum file size enforcement.
5. **Graph/import data trust**: Imported JSON is validated only structurally, not semantically or by size/depth.
6. **Prompt injection risk**: Ingested documents can influence generated answers. Reasoner prompts instruct grounding, but there is no prompt-injection detector.
7. **Local placeholder password**: `projectrag_password` is present as local Docker placeholder. It is not a real secret, but production must override it.
8. **Execution safety is conservative**: Execution is disabled by default, which is good. Future approval mode must be designed carefully before enabling actions.

## Performance Risks

1. **Ollama latency**: Local generation and embeddings may be slow on 4 GB GPU or CPU-only hosts.
2. **Synchronous ingestion**: Ingestion creates embeddings and graph facts synchronously; large directories will block execution.
3. **No batching**: Embedding calls and database writes are per chunk/fact. This will be inefficient for large imports.
4. **No connection pooling**: psycopg2 helper opens connections directly; pool management is absent.
5. **GraphDB query cost**: Raw SPARQL queries and broad relationship searches may become expensive.
6. **Context size growth**: Evidence merging and prompt assembly may become large without stricter token budgeting.
7. **Regex extraction cost**: Current extraction is fine for small text but not optimized for large corpora.

## Scaling Risks

1. **Single-node local assumption**: The design assumes one local machine with Docker services.
2. **No background workers**: Long-running ingestion/evaluation tasks are not queued.
3. **No horizontal API scaling plan**: Shared workflow state is not externalized beyond logs/results.
4. **No sharding or partitioning**: PostgreSQL tables may grow without retention/partition policy.
5. **Graph namespace collisions**: Sanitized entity names can collide across projects/providers.
6. **No model routing implementation beyond policy**: Resource allocator decides tiers, but Ollama client still uses one configured model.
7. **No cache layer**: Embeddings, graph queries, and LLM responses are not cached.

## Recommended Next Sprint

### 1. Integration Test Harness

Create Docker-backed integration tests for:

- PostgreSQL schema initialization.
- pgvector insert/search.
- GraphDB repository/query lifecycle.
- FastAPI `/query` with mocked Ollama but real DB services.

### 2. Alembic Migration Foundation

Introduce Alembic or a lightweight migration runner. Freeze current schema as migration `0001`.

### 3. API Security Baseline

Add local API token support:

- `PROJECTRAG_API_TOKEN`
- optional auth dependency
- disabled by default for dev, enabled for production mode

### 4. GraphDB Repository Bootstrap

Add script to create/configure the `projectrag` repository if missing.

### 5. Upload and Ingestion Hardening

Add:

- max upload size
- file count limit
- ingestion batch size
- better error reporting per file

### 6. Model Routing Implementation

Use resource allocator output to select small/medium/large Ollama model names from settings.

### 7. Background Jobs

Move ingestion and evaluation to a simple local job queue or worker model.

### 8. Entity Namespace Strategy

Add project/provider prefixes to graph entity identifiers to avoid collisions.

### 9. Production Config Profiles

Add explicit config modes:

- local
- test
- production

Make unsafe endpoints such as raw SPARQL configurable by mode.

### 10. Documentation Tightening

Update README and smoke tests to reflect all new endpoints and known limitations.

## Maturity Scores

| Area | Score | Rationale |
| --- | ---: | --- |
| Infrastructure | 72 | Docker Compose, schema, Makefile, CI, backups, and docs exist. Missing migrations and integration tests. |
| GraphRAG | 68 | Entity/relationship extraction, triples, traversal, impact helpers, and provenance exist. Extraction and traversal remain basic. |
| Memory | 70 | Conversation/project/knowledge/ontology memory stores exist. Boundaries and retrieval semantics need refinement. |
| Agents | 74 | Broad agent skeleton exists with workflows, planning, validation, learning, and recommendations. Many agents are deterministic placeholders. |
| Validation | 66 | Safety, deterministic hallucination checks, optional LLM judge, and evaluation metrics exist. Needs stronger grounding/citation enforcement. |
| DevOps | 58 | Inventory importers and connector skeletons exist. No real cloud discovery, no credential-safe implementation yet. |
| Security | 52 | Secrets are avoided, uploads are path-safe, execution disabled by default. No auth, rate limiting, or production hardening yet. |
| Observability | 61 | Health, deep health, Prometheus metrics, workflow logs, and runbooks exist. No tracing, dashboards, or alerting yet. |

## Overall Assessment

ProjectRAG is a strong local-first MVP foundation with unusually broad coverage for architecture, agents, graph extraction, memory, validation, DevOps import skeletons, operations docs, and tests.

However, it is not production-ready yet. The main blockers are authentication, migration management, real integration testing, background execution for long-running jobs, GraphDB bootstrap automation, and stronger security controls around raw SPARQL, uploads, and prompt-injection risk.

Recommended overall maturity: **65 / 100**.
