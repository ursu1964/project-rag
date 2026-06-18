# RAG Intelligent Infrastructure Step-by-Step Implementation Plan

Generated: 2026-06-17

Scope: RAG Infrastructure Intelligence architecture only. n8n is intentionally ignored and is not part of this implementation plan.

## Target Architecture

- Frontend: chat, cockpit/admin, topology, document manager, audit/evaluation console.
- Middleware/API Gateway: auth/RBAC, request validation, rate limiting, caching, prompt policy, audit logging.
- Backend Services: RAG orchestration, ingestion, embeddings, retrieval, LLM generation, infrastructure connectors, evaluation, safe automation.
- Storage: PostgreSQL/pgvector, GraphDB, future object storage, future Redis, future OpenTelemetry/Grafana/Prometheus.

## Implemented Step 1 — Gateway Foundation

Implemented now:

1. `app/gateway/middleware.py`
   - optional API-key authentication
   - public health/docs/metrics paths
   - optional in-memory rate-limit scaffold
   - logger-based request audit

2. `app/core/config.py`
   - `PROJECTRAG_API_KEY`
   - `PROJECTRAG_RATE_LIMIT_PER_MINUTE`
   - `PROJECTRAG_REQUEST_AUDIT_ENABLED`

3. `app/main.py`
   - gateway middleware installed during app creation

4. `ui/streamlit_app.py`
   - optional API-key field
   - automatically sends `X-ProjectRAG-API-Key` when provided

5. `.env.example`
   - documents optional gateway settings

6. `tests/test_gateway_middleware.py`
   - validates local-dev auth disabled by default
   - validates health remains public
   - validates protected endpoint rejects missing key
   - validates protected endpoint accepts correct key


## Implemented Step 2 — Citation Foundation

Implemented now from Prompt 7 / QA audit requirements:

1. `app/rag/citations.py`
   - builds compact citations from vector, graph, and memory evidence

2. `app/api/routes_query.py`
   - returns `citations` with normal query responses
   - includes citations in debug state

3. `ui/streamlit_app.py`
   - displays a Citations table under each answer

4. `tests/test_citations.py` and API route tests
   - validate vector, graph, memory, and response citations

## Implemented Step 3 — Endpoint RBAC Permission Map

Implemented now from Prompt 6 / Middleware Optimization requirements:

1. `app/gateway/middleware.py`
   - maps route families to permissions:
     - document reads, graph export, workflow audit: `read`
     - query and graph query: `query`
     - ingestion, upload, reindex, delete, inventory import: `ingest`
   - optionally enforces RBAC when `PROJECTRAG_ENFORCE_RBAC=true`
   - returns `403 Forbidden` with a policy decision when denied

2. `app/core/config.py` and `.env.example`
   - added `PROJECTRAG_ENFORCE_RBAC=false` default

3. `tests/test_gateway_middleware.py`
   - validates permission mapping and local role decisions

Local development remains unchanged unless RBAC enforcement is enabled.

## Implemented Step 4 — Prompt Policy Pre-check

Implemented now from Prompt 10 / Security Audit requirements:

1. `app/security/prompt_policy.py`
   - blocks prompt-injection, system-prompt exfiltration, secret exfiltration, and destructive execution requests
   - flags likely PII/private-key content for human approval

2. `app/api/routes_query.py`
   - evaluates prompt policy before workflow execution
   - blocks unsafe prompts without starting retrieval/generation
   - returns `policy_decision` in query responses

3. `ui/streamlit_app.py`
   - displays prompt policy result under each answer

4. `tests/test_prompt_policy.py` and API route tests
   - validate allowed, flagged, and blocked prompt behavior

## Implemented Step 5 — Evaluation Console

Implemented now from Prompt 9 / QA and Testing requirements:

1. `app/api/routes_evaluation.py`
   - exposes read-only `GET /evaluation/report`
   - parses the generated Markdown report summary
   - does not run expensive live evaluations during UI page load

2. `ui/streamlit_app.py`
   - Audit tab now shows evaluation question count and report summary
   - expandable Markdown report for presentation/review

3. `tests/test_evaluation_routes.py` and API route tests
   - validate report parsing, missing report behavior, and API route registration

Additional improvement implemented: read-only evaluation reports now include MVP quality gates with pass/fail thresholds for route accuracy, keyword match, graph/vector evidence usage, validation confidence, and safety approval correctness.

## Implemented Step 6 — Storage/Observability Hardening: GraphDB Cleanup

Implemented now:

1. `app/graph/graphdb_client.py`
   - added `sparql_update()`
   - added `delete_graph_facts()` to remove triples reconstructed from PostgreSQL graph provenance

2. `app/repositories/documents_repository.py`
   - document deletion now performs best-effort GraphDB cleanup before deleting PostgreSQL graph facts/chunks/document rows
   - PostgreSQL deletion still completes if GraphDB is temporarily unavailable

3. tests
   - validates SPARQL update generation
   - validates document delete calls GraphDB cleanup first

Remaining later storage/observability work:

- Redis only when multi-process deployment is needed.
- OpenTelemetry tracing and Grafana dashboards.
- MinIO/object storage only when local file storage becomes insufficient.

## Current Principle

Build in this order:

**analyse → program → plan → implement → audit → audit**

The system stays local-first, evidence-first, audit-first, and execution-safe.


## Implemented Step 7 — Data Source Inspection / Source Catalog

Implemented now from Step 2 / Data Source Inspection requirements:

1. `app/rag/source_catalog.py`
   - scans local source files under `data/raw`
   - classifies documents, runbooks, logs, inventory-like JSON, Terraform, and Kubernetes-like manifests
   - marks currently ingestable text files

2. `app/api/routes_sources.py`
   - exposes read-only `GET /sources/catalog`

3. `ui/streamlit_app.py`
   - Document manager now shows source catalog status, counts, and source file table

4. tests
   - validate missing-path behavior, classification, and route registration



## Implemented Step 8 — Text Parser and Metadata Extraction

Implemented now from Step 3 / RAG Pipeline Prototype requirements:

1. `app/rag/parsing.py`
   - supports `.txt`, `.md`, and `.log` files
   - extracts filename, suffix, source type, line count, and character count

2. `app/rag/ingestion.py`
   - uses the parser instead of raw `.txt`-only reads
   - stores extracted metadata on documents and chunks
   - directory ingestion now includes `.txt`, `.md`, and `.log`

3. `app/rag/source_catalog.py`
   - ingestable flag now matches parser support

4. tests
   - validate parser metadata
   - validate Markdown ingestion
   - validate directory ingestion includes text-like infrastructure files



## Implemented Step 9 — Infrastructure File Ingestion Support

Implemented now from Step 2 / Data Source Inspection and Step 5 / Infrastructure Connectors requirements:

1. `app/rag/parsing.py`
   - text parser now supports `.json`, `.yaml`, `.yml`, and `.tf` in addition to `.txt`, `.md`, and `.log`
   - classifies Terraform, Kubernetes manifests, Ansible playbooks, inventory/CMDB JSON, generic JSON/YAML, logs, runbooks, and documents

2. `app/rag/ingestion.py`
   - directory ingestion automatically includes supported infrastructure text files

3. `app/rag/source_catalog.py`
   - ingestable status now aligns with the expanded parser support

4. tests
   - validate parser classification and ingestion/catalog handling for infrastructure source types



## Implemented Step 10 — Structured Infrastructure Metadata Extraction

Implemented now from Prompt 7 / RAG Pipeline and Prompt 8 / Infrastructure Integration requirements:

1. `app/rag/parsing.py`
   - JSON: parse status, JSON type, top-level keys, array item count
   - YAML/Kubernetes-like manifests: apiVersion, kind, name, namespace, document separator count
   - Terraform: resource count/list, module count/list, provider list
   - Logs: severity counts for error/warn/info/debug/critical

2. ingestion automatically stores this metadata on documents and chunks because it uses `parse_text_document()`

3. tests validate metadata extraction for JSON, YAML, Terraform, and logs



## Implemented Step 11 — Workflow Output Provenance Persistence

Implemented now from QA/Audit Framework requirements:

1. `app/repositories/workflow_repository.py`
   - added `store_workflow_output()` to persist generated response payloads in `workflow_runs.output`

2. `app/api/routes_query.py`
   - stores answer, evidence, citations, policy decision, validation, and metrics after a successful query

3. `app/api/routes_workflow_audit.py` already exposes workflow output through `/workflows` and `/workflows/{workflow_id}`

4. tests
   - validate query route stores output
   - validate repository update payload



## Implemented Step 12 — Graph Evidence Alignment

Implemented now from the Part 29 acceptance follow-up:

1. `app/agents/graph_retriever.py`
   - normalizes GraphDB URI bindings into local entity/predicate names
   - adds plain-text `fact_text` for incoming, outgoing, impact, and two-hop graph evidence
   - preserves query-type routing for dependency and impact questions

2. tests
   - validate `VM1 dependsOn Database01` graph evidence is returned as explicit subject/predicate/object fields plus `fact_text`

This completes the documented code-side Part 29 evidence repair path. Live acceptance still requires running services and re-ingesting sample data so documents, chunks, and graph facts are populated at runtime.

Runtime acceptance check completed locally:

- Docker services: PostgreSQL and GraphDB healthy
- Data state: 1 document, 1 chunk, 7 graph facts
- Graph export: returns topology nodes/edges including `VM1 -> Database01`
- Sample query: `What does VM1 depend on?` returns `Database01`
- Validation: grounded=true, confidence=0.8, requires_human_approval=false


## Implemented Step 13 — Query Provenance Envelope

Implemented now from the attached plan's QA and Audit Framework:

1. `app/api/routes_query.py`
   - query responses now include a `provenance` envelope with:
     - user question and rewritten query
     - retrieved chunks and source documents
     - prompt version, model name, embedding model
     - generated answer, citations, confidence score, latency, policy decision, and feedback placeholder
   - the same response payload is persisted to workflow output for audit/replay

2. tests
   - validate provenance fields are returned and persisted with workflow output

Remaining later audit improvements:

- token accounting when model backend exposes usage
- explicit prompt-template registry/versioning
- user feedback endpoint and evaluation trend aggregation


## Implemented Step 14 — User Feedback and Evaluation Trend Capture

Implemented now from the attached plan's Audit Console and Evaluation Dashboard requirements:

1. `app/api/routes_feedback.py`
   - adds `POST /feedback/{workflow_id}` for answer feedback
   - accepts rating, helpful flag, and bounded comment text

2. `app/repositories/workflow_repository.py`
   - attaches feedback to stored workflow output and provenance `user_feedback`
   - writes feedback metrics into `evaluation_results` under dataset `user_feedback` for trend analysis

3. `app/main.py` and gateway middleware
   - registers the feedback route
   - maps feedback submission to the `query` permission family

4. tests
   - validate feedback route success and 404 behavior
   - validate workflow output/provenance update and evaluation trend insert


## Implemented Step 15 — PII and Secret Redaction for Query Audit

Implemented now from the attached plan's Middleware/Security requirements:

1. `app/security/pii_filter.py`
   - redacts common SSNs, credit-card-like numbers, private keys, and simple secret assignments
   - supports recursive redaction for JSON-like response/evidence structures

2. `app/api/routes_query.py`
   - redacts sensitive text in query response question, answer, evidence, citations, and provenance
   - stores redacted audit question in workflow input
   - keeps prompt policy warning behavior for PII while reducing leakage in audit/response payloads

3. tests
   - validate text and recursive data redaction
   - validate query responses and persisted provenance do not expose SSN-style input

Remaining later security improvements:

- OAuth2/JWT identity provider integration
- tenant/workspace isolation
- full secrets manager integration
- configurable redaction policy and allowlisted admin review mode


## Implemented Step 16 — Request Tracing Header

Implemented now from the attached plan's Middleware and Observability requirements:

1. `app/gateway/middleware.py`
   - accepts safe caller-provided `X-Request-ID` values
   - generates a UUID trace id when missing or unsafe
   - adds `X-Request-ID` to normal and gateway-denied responses
   - includes request id in gateway audit logs for request traceability
   - stores request id on `request.state.request_id` for future route-level use

2. tests
   - validate safe request id reuse and unsafe value replacement

Remaining later observability improvements:

- OpenTelemetry trace/span propagation
- structured log export to Loki/ELK
- Grafana dashboards for request latency and RAG quality trends


## Implemented Step 17 — Graph Query Cache

Implemented now from the attached plan's Middleware/Performance Optimization requirements:

1. `app/graph/graphdb_client.py`
   - caches SPARQL query responses using the existing local cognitive cache
   - returns defensive copies so callers cannot mutate cached values
   - invalidates graph cache entries after Turtle inserts and SPARQL updates

2. tests
   - validate repeated SPARQL queries hit GraphDB only once
   - validate cache invalidation after graph mutation

This remains a local single-process cache. Redis-backed distributed caching is still future scope for multi-process or Kubernetes deployment.
