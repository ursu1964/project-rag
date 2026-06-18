# ProjectRAG System Audit After Prompts 0–111

Date: 2026-06-16

## Executive Summary

ProjectRAG has a broad local-first GraphRAG MVP foundation plus many controlled skeleton layers added through prompts 0–111.

Audit result: **no blocking issues found**.

Validation completed:

```text
/home/RAG/.venv/bin/python -m compileall -q app scripts tests
PASS

/home/RAG/.venv/bin/python -m pytest -q
273 passed

docker compose config
PASS

scripts/init_postgres.sql applied to local PostgreSQL
PASS
```

Live local dependency checks:

```text
PostgreSQL SELECT 1: PASS
GraphDB /rest/repositories: PASS
Ollama /api/tags: PASS
Docker Compose services: PASS
```

## Implemented Modules

### Core MVP / Active Engineering Scope

Implemented and tested:

- FastAPI application factory and API routers
- LangGraph RAG workflow
- PostgreSQL + pgvector schema and helpers
- GraphDB client and repository bootstrap
- Ollama client
- document ingestion
- chunking
- document registry
- vector store
- graph ingestion and provenance
- entity and relationship extraction
- memory stores
- query workflow logging
- validation and safety checks
- context merging, scoring, compression, reranking
- health/deep health/metrics endpoints

### Topology, Impact, Simulation, and Prediction

Implemented and tested:

- topology traversal
- impact analysis
- impact agent
- blast radius agent
- RCA agent
- failure simulation engine
- deterministic chaos metrics
- capacity forecasting
- failure prediction

### Read-Only Tooling and Governance

Implemented and tested:

- tool registry
- tool policy
- tool executor
- read-only Docker tool
- read-only PostgreSQL SELECT tool
- read-only GraphDB SELECT tool
- read-only Git status/diff tool
- DevOps action planning
- approval gate
- rollback planner
- verifier
- RBAC foundation
- identity stub
- policy engine
- security audit
- constitutional governance
- trust agent
- governance agent

### Discovery and Digital Twin

Implemented and tested:

- discovery package
- Docker discovery
- discovery agent
- supported entity types
- inventory schema
- digital twin topology builder
- digital twin generator

### Controlled Skeletons

Implemented as non-executing controlled skeletons:

- swarm registry, reputation, consensus, consensus engine
- infrastructure brain
- knowledge pyramid
- model matrix
- brain resource allocator
- RAG-OS local scheduler/resource/context/goal/runtime managers
- cognitive cache
- local cluster node registry/heartbeat/health
- local PostgreSQL-backed task queue and worker
- enterprise advisory role stubs
- research agents
- evolution sandbox and fitness engine

### Documentation and Guardrails

Implemented:

- AGII future architecture documentation only
- practical scope guardrails
- enterprise layers documentation
- stabilization report
- final architecture review

## Missing Imports

Checked all Python modules under `app/` by importing them with the project virtual environment.

Result: **PASS**

```text
modules_checked: 179
errors: []
```

No missing imports were found.

## Dead Code / Skeleton Code

No blocking dead code was detected.

Expected controlled skeletons remain in:

- `app/enterprise/`
- `app/brain/`
- `app/research/`
- `app/evolution/`
- portions of `app/swarm/`
- portions of `app/ragos/`

These are intentional after prompts 95–111 and are explicitly recommendation-only or execution-disabled.

Non-blocking note: several skeleton modules are not wired into FastAPI or LangGraph workflows yet. This is acceptable because they are future-facing controlled skeletons, not active MVP execution paths.

## Duplicated Logic

Non-blocking duplication observed:

1. **Entity extraction from questions** appears in multiple agents:
   - topology agent
   - graph retriever
   - impact agent
   - blast radius agent
   - RCA agent

   Recommendation: later centralize into a shared `question_entity_extractor` utility.

2. **Graph traversal neighborhood expansion** appears in:
   - `app/graph/traversal.py`
   - `app/simulation/simulation_engine.py`
   - `app/agents/blast_radius_agent.py`

   Recommendation: later reuse one traversal core with policy-aware callers.

3. **Execution-disabled / recommendation-only metadata** is repeated across governance, enterprise, research, evolution, and tool modules.

   Recommendation: later centralize common constants.

No duplicated logic is currently blocking tests or local operation.

## Schema Drift

The schema is still managed through one append-only idempotent file:

```text
scripts/init_postgres.sql
```

Result: **PASS with technical debt**

The script applies successfully to local PostgreSQL and remains idempotent.

Known schema technical debt:

- no migration framework yet
- no schema version table
- many future-scope tables exist before product workflows use them
- `cluster_nodes.node_name` has an index but no uniqueness constraint, so repeated local registration can create duplicates depending on caller behavior
- some tables use `TIMESTAMP`, while earlier core tables use `TIMESTAMPTZ`

These are not blockers for the local MVP but should be addressed before production hardening.

## Broken Tests

Test result:

```text
273 passed
```

No broken tests found.

## Docker Issues

Docker Compose validation:

```text
docker compose config: PASS
```

Runtime status:

```text
projectrag-postgres: Up, healthy, 5433->5432
projectrag-graphdb: Up, 7200->7200
```

Resolved previous issues:

- GraphDB image is pinned to `ontotext/graphdb:10.8.6` instead of non-existent `latest`.
- PostgreSQL host port is configurable with `${POSTGRES_PORT:-5432}` and currently resolves to `5433` to avoid local conflicts.

Non-blocking Docker note:

- Compose still contains a local placeholder password. This is acceptable for local MVP only and is excluded from real secret use by policy.

## Unsafe Execution Paths

Audit found subprocess usage only in constrained read-only paths:

- `app/tools/docker_tool.py`
  - allowed: `docker ps`, `docker logs`
  - blocks destructive command terms
- `app/tools/github_tool.py`
  - allowed: `git status --short`, `git diff`
- `app/discovery/docker_discovery.py`
  - uses `docker ps --all --format` only

No arbitrary shell execution path was found.

Policy protections present:

- tool registry rejects shell-like tool names
- tool executor only invokes registered Python callables
- high/critical risk handling exists
- critical tools are blocked by default
- DevOps plans are recommendation-only
- execution agents remain disabled
- evolution sandbox never applies patches

Remaining non-blocking risk:

- `app/discovery/docker_discovery.py` invokes Docker directly for read-only discovery and relies on fixed argument lists. It is safe for the current local scope, but production should wrap it through the central tool policy/audit layer.

## Undocumented Endpoints

Current OpenAPI paths:

```text
/cognitive/query
/devops/inventory/import
/documents
/documents/upload
/graph/query
/health
/health/deep
/ingest
/memory
/memory/search
/metrics
/query
```

Endpoints are represented in generated OpenAPI. Documentation coverage is split across README, local smoke test, operations runbook, stabilization report, and final architecture review.

Non-blocking documentation gap:

- README focuses on the core smoke path and does not fully document every newer endpoint such as `/memory`, `/metrics`, `/documents/upload`, `/devops/inventory/import`, and `/cognitive/query`.

Recommendation: update README API section in a later documentation-only pass.

## Security and Secret Review

`.gitignore` protects:

- `.env`
- `.env.*`
- `.venv/`
- caches
- logs
- data directories
- backups and dumps

Secret scan showed only placeholders, docs, code variable names, and local-only sample values.

No real credentials were identified.

## Blocker Fixes Applied During This Audit

None.

No blocking issues were found, so no code changes were made as part of this audit beyond creating this report.

## Recommendations Before Next Feature Work

1. Freeze MVP scope using `docs/practical_scope_guardrails.md`.
2. Add Alembic or a minimal migration table before adding more schema.
3. Centralize duplicate entity extraction and graph traversal helpers.
4. Keep all future modules behind read-only/recommendation-only defaults.
5. Update README endpoint documentation.
6. Add integration tests for live PostgreSQL + GraphDB + mocked Ollama flows.
7. Consider unique constraint or upsert key for `cluster_nodes.node_name`.
8. Route Docker discovery through tool audit/policy before expanding it.

## Final Assessment

ProjectRAG after prompts 0–111 is stable for local MVP experimentation.

The project is not production-ready, but it is structurally coherent, tests pass, imports are valid, local infrastructure validates, and unsafe execution paths are blocked or constrained to read-only behavior.
