# Plan vs Current Application Comparison

Generated: 2026-06-17

Scope compared:

- `plan1_master_part9.md`
- `plan1_master_part11.md` through `plan1_master_part29.md`
- Current repository under `/home/RAG/project-rag`

## Executive Summary

The current application is strongest against **Part 29: Practical MVP Reset**. The repository has the main local GraphRAG foundation: FastAPI, LangGraph, PostgreSQL/pgvector schema, GraphDB integration, Ollama client, ingestion code, vector retrieval, graph retrieval, validation, logging, tests, Docker Compose, Streamlit UI, and safety guardrails.

However, the active runtime data state is not yet healthy:

- documents exist: yes
- chunks exist: no
- graph facts exist: no
- `/query` works technically but gives low-confidence answers because evidence is empty

The later master-plan layers, Parts 9 and 11-28, are mostly **foundations, skeletons, or deterministic MVP versions**, not full production systems. This is good: Part 29 explicitly says not to start with AGII, autonomous DevOps, cloud mutation, recursive evolution, or artificial executives.

## Current Test/Runtime Baseline

Latest local validation:

```text
pytest: 286 passed, 1 skipped
compileall: passed
local docker compose config: passed
prod docker compose config: passed
/health: ok
/health/deep: ok
GraphDB: reachable
Ollama: reachable
PostgreSQL container: healthy
```

Known runtime data gap:

```text
Documents: 1
Chunks: 0
Graph facts: 0
Average validation confidence: 0.200
```

Likely cause: a previous ingestion inserted the document record, then failed before chunks and graph facts were written. Duplicate detection now skips the same file.

## Maturity Scale

| Score | Meaning |
|---:|---|
| 0 | Not present |
| 20 | Skeleton/stub only |
| 40 | Deterministic MVP foundation |
| 60 | Working but incomplete |
| 80 | Stable MVP |
| 100 | Production-grade |

## Plan Coverage Matrix

| Plan Part | Theme | Current Coverage | Maturity | Evidence in App | Main Gaps |
|---|---|---:|---:|---|---|
| Part 9 | Topology Intelligence Engine | Partial implementation | 45 | `impact_agent`, `blast_radius_agent`, `failure_prediction_agent`, `rca_agent`, `simulation_engine`, `impact_analysis`, chaos/prediction modules, DB tables | No full capacity agent, no full chaos agent workflow, no incident mining, current graph facts empty |
| Part 11 | MCP/tooling/external system integration | Controlled local foundation | 40 | `app/tools/tool_registry.py`, `tool_policy.py`, `tool_executor.py`, Docker/Postgres/GraphDB/GitHub read-only adapters, `app/mcp/*` | No real MCP server, no full schema contracts, no external cloud/Kubernetes/Terraform tools, limited audit integration |
| Part 12 | Discovery & digital twin | Partial deterministic foundation | 40 | `app/discovery/docker_discovery.py`, `app/digital_twin/*`, `app/devops/topology_importer.py`, inventory tables | Docker-only read path; no VirtualBox/AWS/Azure/Kubernetes live discovery; visualization export just added but no populated graph facts |
| Part 13 | Chaos/prediction/self-learning models | Deterministic baseline | 35 | `app/chaos/*`, `app/prediction/*`, `failure_prediction_agent.py`, capacity/failure tables | No Lyapunov agent, no incident pattern mining, no real telemetry pipeline, no ML/self-learning model loop |
| Part 14 | Swarm intelligence | Controlled skeleton | 25 | `app/swarm/agent_registry.py`, `reputation.py`, `consensus.py`, `consensus_engine.py` | No dynamic workflow generator, no swarm memory, no marketplace, no real multi-agent runtime |
| Part 15 | Autonomous Infrastructure Intelligence Platform | Skeleton only | 25 | `app/brain/*`, model/resource allocators | No MCP mesh, no enterprise deployment target, no complete infrastructure brain loop |
| Part 16 | RAG-OS layer | Lightweight local-only skeleton | 30 | `app/ragos/scheduler.py`, `resource_manager.py`, `model_runtime_manager.py`, `knowledge_router.py`, `context_manager.py`, `goal_manager.py`, `cognitive_cache.py` | No workflow compiler, no resource isolation, no production scheduling semantics |
| Part 17 | Distributed cluster/neural mesh | Single-node skeleton only | 20 | `app/cluster/*`, cluster tables | No distributed execution, no Redis/Rabbit/NATS, no Kubernetes, no node auth, worker only safe registered tasks |
| Part 18 | Production security/RBAC/governance | Local dev foundation | 30 | `app/security/*`, `security_audit_events`, policies, local identity | No real auth provider, no tokens/sessions, no production RBAC enforcement on endpoints |
| Part 19 | Autonomous decision systems | Intentionally delayed/blocked | 10 | `execution_agent` disabled, approval gates, safety policy | No autonomous action; this is intentional for MVP safety |
| Part 20 | Artificial CTO layer | Recommendation-only stub | 15 | `app/enterprise/artificial_cto.py` | No real CTO reasoning, no authority, no execution |
| Part 21 | Artificial Enterprise Architect | Recommendation-only stub | 15 | `app/enterprise/artificial_architect.py` | No capability maps, value streams, enterprise architecture graph |
| Part 22 | Artificial COO | Recommendation-only stub | 15 | `app/enterprise/artificial_coo.py` | No operational KPIs, team/project intelligence, process twin |
| Part 23 | Artificial CEO | Recommendation-only stub | 15 | `app/enterprise/artificial_ceo.py` | No strategy engine, scorecards, executive board |
| Part 24 | Artificial Enterprise Civilization | Mostly not implemented | 5 | High-level docs only | No ecosystem twin, supply chain, market intelligence, federated learning |
| Part 25 | Artificial Scientific Research Organization | Partial skeleton | 25 | `app/research/hypothesis_agent.py`, `experiment_agent.py`, `evidence_agent.py`, `theory_agent.py`, research tables | Missing pattern discovery, causal inference, research portfolio agent, no experiment execution |
| Part 26 | AGII | Documentation/guardrail only | 5 | `docs/agii_future_architecture.md` | No AGII core modules; intentionally not part of MVP |
| Part 27 | Cognitive governance/self-regulation | Partial governance foundation | 30 | `app/governance/constitutional_engine.py`, `governance_agent.py`, `trust_agent.py`, governance tables | Missing ethics/epistemic/cognitive immune/meta-governance modules, no endpoint enforcement |
| Part 28 | Recursive cognitive evolution | Sandbox only | 20 | `app/evolution/evolution_sandbox.py`, `fitness_engine.py`, evolution tables | No production self-modification, no genomes, no evolution engine; intentionally blocked |
| Part 29 | Practical MVP roadmap | Mostly implemented, but data gap blocks acceptance | 70 code / 45 runtime | FastAPI, LangGraph, PostgreSQL, GraphDB, Ollama, ingestion, agents, validation, tests, Docker, UI | Ingestion partial-state bug: chunks and graph facts are currently zero; vector/graph evidence quality not accepted yet |

## Detailed Comparison by Layer

### Part 29 - MVP Foundation

Implemented:

- FastAPI app and routes
- LangGraph RAG workflow
- PostgreSQL schema with pgvector
- GraphDB client and SPARQL templates
- Ollama embedding/generation client
- Document registry, chunking, vector store, ingestion
- Entity/relationship extraction
- Basic agents: router, memory, vector, graph, merger, reasoner, validator
- Workflow logging, validation storage, audit endpoints
- Tests and CI/lint/type config
- Docker Compose, production Compose, Dockerfile
- Streamlit UI
- Local smoke/deployment docs

Blocking gap:

- Current sample data is not actually indexed into chunks or graph facts.
- This prevents good answers and graph visualization.

Acceptance status:

```text
Code structure: PASS
Tests: PASS
Runtime services: PASS
Data/evidence state: FAIL until re-ingestion is repaired
```

### Part 9 - Topology Intelligence

Implemented at MVP level:

- direct/indirect impact code
- blast radius agent
- RCA agent
- simulation engine
- failure prediction baseline
- chaos metric functions
- digital twin generator
- topology importer
- related schema tables

Gaps:

- no full capacity agent module named `capacity_agent.py`
- no full chaos agent module named `chaos_agent.py`
- no production topology state refresh loop
- no populated graph facts in current runtime

### Part 11 - Tooling/MCP

Implemented safely:

- tool registry
- tool policy
- tool executor
- read-only Docker/Postgres/GraphDB/GitHub tool adapters
- internal MCP preparation modules
- dangerous commands blocked

Gaps:

- no external MCP server yet
- no Terraform/Kubernetes/cloud execution tools
- no real external credential flow
- no strong typed tool input/output schemas beyond simple functions

This is appropriate for MVP safety.

### Parts 12-17 - Discovery, Digital Twin, Chaos, Swarm, Brain, RAG-OS, Cluster

Current level:

- deterministic local foundations exist
- most are single-node only
- many are skeletons or local-only simple implementations

Major gaps:

- no live cloud or Kubernetes discovery
- no telemetry ingestion
- no distributed agent execution
- no message bus
- no production model runtime manager

### Parts 18-28 - Security, Enterprise, Research, AGII, Governance, Evolution

Current level:

- security/RBAC/governance foundations exist
- enterprise and research modules are recommendation-only stubs
- AGII is documented as future scope
- evolution sandbox blocks production self-modification

This matches the practical guardrail: do not enable autonomous execution or AGII before MVP stability.

## Highest-Risk Gaps

1. **Ingestion partial-state bug**
   - Document registered but chunks/graph facts missing.
   - Duplicate detection blocks retry.

2. **Runtime quality gap**
   - `/query` returns HTTP 200, but answer is not grounded due empty evidence.

3. **Graph facts empty**
   - `/graph/export` works but returns empty graph.

4. **Lots of untracked files**
   - Commit hygiene risk.
   - `.vscode/` probably should be ignored unless intentionally shared.

5. **Production security not real yet**
   - Local identity/RBAC exists, but endpoints are not protected by real auth.

6. **Many future modules are stubs**
   - Fine as long as they are clearly documented as delayed/recommendation-only.

## Recommended Next Engineering Plan Status

### Step 1 - Fix MVP data/evidence state first

Code status: implemented.

Goal:

```text
Documents > 0
Chunks > 0
Graph facts > 0
/query answer grounded for sample topology
```

Actions:

1. Add safe ingestion repair logic:
   - if document exists but chunks are missing, process chunks
   - if document exists but graph facts are missing, process graph facts
   - avoid duplicating facts/chunks

2. Add status metadata:
   - `ingestion_status`: `registered`, `chunked`, `graphed`, `completed`, `failed`
   - or a small `ingestion_runs` table later

3. Add tests for partial ingestion recovery.

Implemented in `app/rag/ingestion.py` and tests. If an existing document has missing
chunks or graph facts, ingestion now repairs the missing derived state instead of
blindly skipping the file as a duplicate.

### Step 2 - Validate MVP acceptance gate

Code validation status: passing. Runtime service/data validation passed locally after
starting Docker services and re-ingesting sample data.

Run:

```bash
pytest -q
docker compose ps
curl http://127.0.0.1:8000/health/deep
python -m scripts.generate_metrics_report
curl http://127.0.0.1:8000/graph/export?limit=20
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What does VM1 depend on?"}'
```

Expected:

- graph export shows nodes/edges
- query answer mentions `Database01`
- validation confidence improves

### Step 3 - Improve graph retriever/reasoner alignment

Code status: implemented.

Current graph context may exist structurally but reasoner still treats it as insufficient.

Actions:

- Ensure graph retriever returns outgoing facts in plain text form.
- Ensure context merger places graph facts into the prompt clearly.
- Add a test: `VM1 dependsOn Database01` graph evidence is normalized into
  subject/predicate/object fields and `fact_text`.

Implemented in `app/agents/graph_retriever.py`. GraphDB URI bindings are normalized
into local names such as `VM1`, `dependsOn`, and `Database01`, with explicit
plain-text `fact_text` for prompt/citation use.

### Step 4 - Keep Parts 19-28 delayed

Do not implement autonomous execution, AGII, recursive evolution, artificial executives, or cloud mutation until Part 29 acceptance passes.

### Step 5 - Clean repository before commit

Actions:

- Review untracked files.
- Add `.vscode/` to `.gitignore` unless desired.
- Confirm `.env` is not tracked.
- Generate final safety review.

## Final Assessment

Current ProjectRAG is:

```text
MVP codebase: strong foundation
MVP runtime data state: not accepted yet
Advanced plan layers: mostly skeleton/guardrail level
Safety posture: conservative and good
Next best move: fix ingestion recovery and evidence quality
```

Do not expand new future-scope features until the Part 29 MVP acceptance gate is green.
