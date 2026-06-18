# ProjectRAG Excellence Interface and Presentation Guide

Generated: 2026-06-17

## Goal

Present ProjectRAG as an infrastructure intelligence cockpit, not a simple chatbot. The interface should show readiness, evidence, topology, document operations, auditability, and a clear executive story.

## Interface Added

The Streamlit app now has six presentation-oriented tabs:

1. **Cockpit**
   - API/dependency health
   - document count
   - graph node/edge count
   - recent workflow runs
   - readiness narrative and visible data gaps

2. **Query**
   - question input
   - answer output
   - route, confidence, groundedness, duration
   - vector/graph/memory evidence
   - optional debug state

3. **Documents**
   - upload document
   - ingest after upload
   - trigger bulk ingestion
   - list documents
   - delete selected document
   - reindex selected document

4. **Topology**
   - graph export metrics
   - graph edge table
   - Graphviz topology rendering
   - SPARQL read-only explorer

5. **Audit**
   - workflow run count
   - agent run count
   - validation result count
   - recent workflow/agent/validation tables

6. **Presentation**
   - executive demo narrative
   - recommended demo flow
   - talking points aligned with Plan Part 29 and the infrastructure-intelligence architecture document

## How to Run

Start the backend:

```bash
make api
```

Start the interface:

```bash
make ui
```

Open the Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Recommended Demo Flow

1. Open **Cockpit** and show the system is online.
2. Open **Documents** and upload or ingest a topology/runbook document.
3. Open **Query** and ask an infrastructure question, for example:

   ```text
   What does VM1 depend on?
   ```

4. Open **Topology** and show graph facts and dependency visualization.
5. Open **Audit** and show workflow, agent, and validation traces.
6. Open **Presentation** and summarize the system as:
   - local-first
   - evidence-first
   - topology-aware
   - safely operated
   - ready for incremental Part 29 execution

## Current Caveats

- The topology visualization depends on graph facts being populated.
- GraphDB triple cleanup on document delete is still a future improvement; PostgreSQL graph facts are cleaned now.
- Production auth/RBAC is still not implemented; use locally or behind trusted controls.
