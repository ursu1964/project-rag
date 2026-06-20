# ProjectRAG Master Plan - Part 17
# Distributed ProjectRAG Cluster and Neural Infrastructure Mesh

**Version:** 1.0  
**Target OS:** Ubuntu Linux 24.x  
**Generated:** 2026-06-16  

---

## 1. Purpose

Part 16 introduced RAG-OS, the internal operating system layer for ProjectRAG.

Part 17 extends ProjectRAG from a single Ubuntu laptop into a distributed architecture.

The objective is to move from:

```text
Single-node ProjectRAG
```

to:

```text
Distributed ProjectRAG Cluster
```

and later:

```text
ProjectRAG Neural Infrastructure Mesh
```

This allows the system to scale across:

- local laptop;
- dedicated server;
- GPU workstation;
- cloud VM;
- Kubernetes cluster;
- edge nodes;
- monitoring nodes;
- DevOps automation nodes.

---

# 2. Why a Distributed Architecture Is Needed

Your current laptop is good for MVP work:

```text
Ubuntu 24.x
32 GB RAM
1 TB HDD
4 GB GPU
```

But future ProjectRAG will include:

```text
GraphRAG
Digital Twin
Chaos Intelligence
Swarm Agents
Predictive Models
MCP Tooling
DevOps Execution
Topology Discovery
Monitoring Integration
```

One machine can start the system, but later several workloads should be separated.

Reasons:

```text
LLMs consume RAM and GPU.
GraphDB can grow large.
PostgreSQL can become heavily used.
Agents may run in parallel.
Discovery jobs may be expensive.
Predictive models may require more compute.
```

Therefore, the system should be designed to scale early, even if the MVP runs locally.

---

# 3. Cluster Evolution Roadmap

## Phase 1 — Single Node

```text
Ubuntu Laptop
├── FastAPI
├── LangGraph
├── PostgreSQL + pgvector
├── GraphDB
├── Ollama
└── Agents
```

Purpose:

```text
Build and validate MVP.
```

---

## Phase 2 — Split Database Node

```text
Node 1: API + Agents + Ollama
Node 2: PostgreSQL + GraphDB
```

Purpose:

```text
Separate compute from storage.
```

Effect:

```text
Better performance and easier backups.
```

---

## Phase 3 — Dedicated Model Node

```text
Node 1: FastAPI + LangGraph
Node 2: PostgreSQL + GraphDB
Node 3: Ollama / LLM Runtime
```

Purpose:

```text
Move model inference to stronger hardware.
```

Effect:

```text
Your laptop can remain the control node.
```

---

## Phase 4 — Agent Worker Nodes

```text
Control Node
├── API
├── Scheduler
├── RAG-OS

Worker Node 1
├── Retrieval Agents

Worker Node 2
├── Graph Agents

Worker Node 3
├── Prediction / Chaos Agents
```

Purpose:

```text
Scale agent execution.
```

---

## Phase 5 — Kubernetes Cluster

```text
Ingress
 ↓
FastAPI Pods
 ↓
Agent Worker Pods
 ↓
PostgreSQL
 ↓
GraphDB
 ↓
Model Runtime
 ↓
Monitoring Stack
```

Purpose:

```text
Enterprise-scale operation.
```

---

# 4. Node Roles

## Control Node

Runs:

```text
FastAPI
RAG-OS
LangGraph
Workflow Scheduler
Security Manager
Audit Manager
```

Responsibilities:

- receive requests;
- coordinate agents;
- route tools;
- enforce policy;
- manage workflows;
- store audit decisions.

---

## Knowledge Node

Runs:

```text
PostgreSQL
pgvector
GraphDB
Backup jobs
```

Responsibilities:

- store documents;
- store embeddings;
- store memory;
- store graph;
- store workflow history;
- store telemetry.

---

## Model Node

Runs:

```text
Ollama
LLM models
Embedding models
Model Runtime Manager
```

Responsibilities:

- local inference;
- embeddings;
- summarization;
- reasoning;
- model switching.

---

## Agent Worker Node

Runs:

```text
Agent runtime
Specialized agents
Task queue workers
```

Responsibilities:

- execute retrieval;
- run graph reasoning;
- run topology analysis;
- run chaos metrics;
- run forecasting;
- run validation.

---

## Discovery Node

Runs:

```text
Inventory collectors
Docker discovery
VirtualBox discovery
Cloud discovery
Kubernetes discovery
Network discovery
```

Responsibilities:

- collect infrastructure data;
- normalize inventory;
- send topology updates;
- update Digital Twin.

---

## Monitoring Node

Runs:

```text
Prometheus
Grafana
OpenTelemetry Collector
Log collectors
Metrics exporters
```

Responsibilities:

- gather metrics;
- expose dashboards;
- feed chaos analysis;
- feed capacity prediction.

---

# 5. Cluster Communication Model

Recommended communication pattern:

```text
FastAPI
 ↓
RAG-OS Scheduler
 ↓
Task Queue
 ↓
Worker Agents
 ↓
Result Store
 ↓
Reasoning Layer
```

Initial simple implementation:

```text
HTTP calls + PostgreSQL workflow tables
```

Future implementation:

```text
Redis Queue / RabbitMQ / NATS
```

Enterprise implementation:

```text
Kubernetes Jobs + Message Bus + Service Mesh
```

---

# 6. Suggested Message Bus Options

## Redis Queue

Best for:

```text
simple local distributed prototype
```

Pros:

- easy;
- fast;
- lightweight.

Cons:

- less robust for complex enterprise workflows.

---

## RabbitMQ

Best for:

```text
reliable message delivery
```

Pros:

- mature;
- durable queues;
- routing keys.

Cons:

- more operational overhead.

---

## NATS

Best for:

```text
high-performance distributed agent mesh
```

Pros:

- fast;
- lightweight;
- cloud-native.

Cons:

- requires more architecture discipline.

---

## Recommendation

For ProjectRAG:

```text
Phase 1: no queue
Phase 2: Redis Queue
Phase 3: NATS or RabbitMQ
```

---

# 7. Distributed Agent Protocol

Every agent task should use a standard envelope.

```json
{
  "task_id": "uuid",
  "workflow_id": "uuid",
  "agent_name": "graph_agent",
  "objective": "Analyze VM1 dependencies",
  "input": {},
  "priority": 80,
  "risk_level": "low",
  "created_at": "timestamp"
}
```

Every result should use:

```json
{
  "task_id": "uuid",
  "agent_name": "graph_agent",
  "status": "completed",
  "confidence": 0.91,
  "result": {},
  "warnings": [],
  "duration_ms": 842
}
```

Effect:

```text
Agents can run locally or remotely without changing workflow logic.
```

---

# 8. Distributed State Management

State must not live only in memory.

State should be stored in:

```text
PostgreSQL
```

Core tables:

```text
workflow_runs
agent_runs
agent_tasks
agent_results
tool_calls
validation_results
```

Why:

```text
If an agent crashes, the workflow can resume.
If a node restarts, state is not lost.
If an incident happens, history is auditable.
```

---

# 9. New Tables for Distributed Execution

```sql
CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY,
    workflow_id UUID,
    agent_name TEXT NOT NULL,
    objective TEXT,
    priority INT DEFAULT 50,
    status TEXT DEFAULT 'pending',
    input JSONB DEFAULT '{}'::jsonb,
    assigned_node TEXT,
    created_at TIMESTAMP DEFAULT now(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_results (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES agent_tasks(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence NUMERIC,
    result JSONB DEFAULT '{}'::jsonb,
    warnings JSONB DEFAULT '[]'::jsonb,
    duration_ms INT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cluster_nodes (
    id UUID PRIMARY KEY,
    node_name TEXT UNIQUE NOT NULL,
    node_role TEXT NOT NULL,
    host TEXT,
    status TEXT DEFAULT 'unknown',
    cpu_cores INT,
    memory_gb NUMERIC,
    gpu_available BOOLEAN DEFAULT false,
    last_heartbeat TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

Effect:

```text
ProjectRAG can track distributed work and node health.
```

---

# 10. Node Heartbeat

Each node should periodically report:

```text
node name
node role
CPU usage
memory usage
GPU availability
disk usage
running agents
health status
```

Create future module:

```text
app/cluster/heartbeat.py
```

Purpose:

```text
RAG-OS knows which nodes are alive and available.
```

---

# 11. Cluster Scheduler

Create:

```text
app/cluster/scheduler.py
```

Responsibilities:

```text
select node
assign task
track status
retry failed tasks
avoid overloaded nodes
prefer GPU node for model tasks
prefer Graph node for graph-heavy tasks
```

Scheduling rules:

```text
LLM task -> Model Node
SPARQL task -> Knowledge Node
Discovery task -> Discovery Node
Chaos task -> Prediction Node
API task -> Control Node
```

---

# 12. Model Runtime Distribution

Current:

```text
Ollama runs on laptop
```

Future:

```text
Ollama runs on dedicated model node
```

Configuration:

```env
OLLAMA_URL=http://model-node:11434
```

Effect:

```text
The API node can call remote model inference.
```

---

# 13. Storage Distribution

PostgreSQL and GraphDB should eventually move to a dedicated node.

Reason:

```text
Databases need stable disk and memory.
LLMs cause memory pressure.
Separating them improves reliability.
```

Recommended storage node:

```text
64 GB RAM
SSD/NVMe
daily backups
UPS if possible
```

---

# 14. Backup in Distributed Mode

Backups should run on the knowledge node.

Backup targets:

```text
PostgreSQL dump
GraphDB export
data/raw archive
configuration archive
GitHub repository
```

Backup destination:

```text
external disk
NAS
cloud object storage
```

---

# 15. Security Between Nodes

Use:

```text
private network
firewall rules
SSH keys
TLS later
service accounts
least privilege
```

Do not expose:

```text
PostgreSQL
GraphDB
Ollama
Agent workers
```

directly to the public internet.

Only expose:

```text
FastAPI gateway
```

and later protect it with authentication.

---

# 16. Cluster Deployment Modes

## Local Lab

```text
one Ubuntu laptop
Docker Compose
```

## Home Lab

```text
laptop + mini PC + NAS
```

## Small Server

```text
single 64 GB server
Docker Compose
```

## Multi-Node

```text
API node
DB node
Model node
Worker node
```

## Enterprise

```text
Kubernetes
GPU node pool
managed database
object storage
observability stack
```

---

# 17. Docker Compose Multi-Node Strategy

In small deployments, each node can run its own compose stack.

Example:

Control node:

```text
projectrag-api
projectrag-scheduler
```

Knowledge node:

```text
projectrag-postgres
projectrag-graphdb
```

Model node:

```text
ollama
```

Worker node:

```text
projectrag-worker
```

---

# 18. Kubernetes Future Strategy

Future components:

```text
Deployment: projectrag-api
Deployment: projectrag-worker
Deployment: projectrag-scheduler
StatefulSet: postgres
StatefulSet: graphdb
Deployment: ollama
Deployment: prometheus
Deployment: grafana
```

Use Kubernetes only after:

```text
local MVP works
Docker Compose deployment is stable
agents are modular
state is persisted
```

---

# 19. Distributed Observability

Track:

```text
node health
agent latency
queue depth
LLM latency
GraphDB query latency
PostgreSQL latency
task failures
retry count
memory pressure
GPU usage
```

Dashboards:

```text
Cluster Dashboard
Agent Dashboard
Model Dashboard
Graph Dashboard
Workflow Dashboard
```

---

# 20. Failure Handling

If worker node fails:

```text
mark node unavailable
requeue task
assign to another worker
log failure
```

If model node fails:

```text
fallback to smaller local model
or return degraded response
```

If GraphDB fails:

```text
continue with vector-only response
mark graph context unavailable
```

If PostgreSQL fails:

```text
stop workflow
return system degraded
```

---

# 21. Degraded Mode

ProjectRAG should support degraded modes:

```text
Full mode:
vector + graph + memory + model

Graph degraded:
vector + memory + model

Model degraded:
retrieval-only response

Database degraded:
health error only
```

Effect:

```text
The system fails gracefully.
```

---

# 22. Cluster Security Policy

Rules:

```text
No public database ports.
No public Ollama port.
No unauthenticated execution endpoints.
No direct shell access through API.
No destructive actions without approval.
All tool calls audited.
All node identities tracked.
```

---

# 23. Recommended Implementation Sequence

1. Keep MVP single-node.
2. Add agent task tables.
3. Add node heartbeat table.
4. Add simple local task scheduler.
5. Add worker process.
6. Move model URL into config.
7. Test remote Ollama.
8. Move GraphDB/PostgreSQL to another node.
9. Add Redis queue.
10. Add distributed observability.
11. Add Kubernetes only after stability.

---

# 24. New Modules

```text
app/cluster/__init__.py
app/cluster/node_registry.py
app/cluster/heartbeat.py
app/cluster/scheduler.py
app/cluster/task_queue.py
app/cluster/worker.py
app/cluster/degraded_mode.py
app/cluster/node_health.py
```

---

# 25. New API Endpoints

```text
GET  /cluster/nodes
POST /cluster/register
POST /cluster/heartbeat
GET  /cluster/tasks
POST /cluster/tasks
GET  /cluster/health
```

---

# 26. Final Outcome of Part 17

After implementing Part 17, ProjectRAG can evolve from:

```text
single laptop application
```

to:

```text
distributed cognitive infrastructure platform
```

It becomes possible to separate:

```text
API
agents
models
databases
discovery
monitoring
```

across multiple machines.

This prepares the platform for:

```text
enterprise scaling
GPU expansion
multi-agent parallelism
cloud integration
Kubernetes deployment
infrastructure neural mesh
```

---

# Part 18 Preview

The next logical volume is:

```text
Part 18 — Production Security, Identity, RBAC, and Governance
```

because once the system becomes distributed and capable of DevOps execution, access control becomes critical.

Part 18 should define:

```text
authentication
authorization
RBAC
service accounts
audit logging
secrets management
policy engine
approval workflows
secure MCP access
data classification
compliance model
```
