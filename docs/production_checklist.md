# ProjectRAG Production Readiness Checklist

Use `PASS`, `FAIL`, or `N/A` for each item.

## Environment

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | `.env` is present on host and not committed. |
| PASS / FAIL / N/A | Required environment variables are configured. |
| PASS / FAIL / N/A | `PROJECTRAG_MODE` is set intentionally. |
| PASS / FAIL / N/A | Non-local auth is configured (`PROJECTRAG_AUTH_MODE` + OIDC or API key hash). |
| PASS / FAIL / N/A | Python version is supported. |
| PASS / FAIL / N/A | Dependencies are installed from reviewed requirements. |

## Database

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | PostgreSQL container/service is running. |
| PASS / FAIL / N/A | `scripts/init_postgres.sql` has been applied. |
| PASS / FAIL / N/A | pgvector extension is installed. |
| PASS / FAIL / N/A | Documents, chunks, memory, workflow, validation, graph facts tables exist. |
| PASS / FAIL / N/A | Database size and growth are monitored. |

## GraphDB

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | GraphDB service is running. |
| PASS / FAIL / N/A | ProjectRAG repository exists. |
| PASS / FAIL / N/A | SPARQL query check succeeds. |
| PASS / FAIL / N/A | RDF export/backup process is documented and tested. |

## LLM

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | Ollama is running. |
| PASS / FAIL / N/A | Generation model is pulled. |
| PASS / FAIL / N/A | Embedding model is pulled. |
| PASS / FAIL / N/A | Local hardware can support expected workload. |
| PASS / FAIL / N/A | Prompts do not leak secrets in logs. |

## Agents

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | Router works for vector, graph, hybrid, and action routes. |
| PASS / FAIL / N/A | Memory agent returns expected memory context. |
| PASS / FAIL / N/A | Vector retriever returns chunks. |
| PASS / FAIL / N/A | Graph retriever returns relationships. |
| PASS / FAIL / N/A | Reasoner answers only from context. |
| PASS / FAIL / N/A | Validator returns confidence and approval status. |
| PASS / FAIL / N/A | Execution agent remains disabled unless explicit approval mode exists. |

## Tests

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | `pytest -v` passes. |
| PASS / FAIL / N/A | Import validation passes. |
| PASS / FAIL / N/A | Docker Compose config validates. |
| PASS / FAIL / N/A | Local smoke test passes. |
| PASS / FAIL / N/A | CI workflow is enabled. |

## Security

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | No real secrets are committed. |
| PASS / FAIL / N/A | `.env` is ignored. |
| PASS / FAIL / N/A | `data/raw`, `data/private`, backups, and logs are ignored. |
| PASS / FAIL / N/A | High-risk questions require approval. |
| PASS / FAIL / N/A | Execution is disabled by default. |
| PASS / FAIL / N/A | Upload path traversal is blocked. |

## Monitoring

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | `/health` works. |
| PASS / FAIL / N/A | `/health/deep` works. |
| PASS / FAIL / N/A | `/metrics` works or safe fallback is available. |
| PASS / FAIL / N/A | Logs are reviewed regularly. |
| PASS / FAIL / N/A | Failed workflows are reviewed regularly. |

## Backups

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | PostgreSQL backup script works. |
| PASS / FAIL / N/A | GraphDB backup/export process works. |
| PASS / FAIL / N/A | Backup files are not committed. |
| PASS / FAIL / N/A | Restore test has been performed. |
| PASS / FAIL / N/A | Backup retention policy is defined. |

## Documentation

| Status | Item |
| --- | --- |
| PASS / FAIL / N/A | README is current. |
| PASS / FAIL / N/A | Local smoke test guide is current. |
| PASS / FAIL / N/A | Troubleshooting guide is current. |
| PASS / FAIL / N/A | Operations runbook is current. |
| PASS / FAIL / N/A | Architecture decisions are documented in ADRs. |
| PASS / FAIL / N/A | Graph ontology is documented. |
