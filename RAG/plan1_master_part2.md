
# ProjectRAG Master Plan - Part 2

## Volume A - GraphDB Ontology Design

### Purpose

The ontology defines how knowledge is represented.

Without an ontology:

- relationships become inconsistent
- retrieval quality decreases
- GraphRAG becomes unreliable

### Core Entity Types

Infrastructure:

- VM
- Host
- Hypervisor
- Container
- KubernetesCluster
- Namespace
- Pod
- Service
- LoadBalancer
- Firewall
- Router
- Switch
- VNet
- Subnet
- Storage

Application:

- Application
- API
- Database
- Queue
- Cache
- User

Documents:

- Document
- Chunk
- Topic
- Tag

### Relationship Types

dependsOn
connectedTo
hostedOn
belongsTo
protectedBy
contains
uses
calls
readsFrom
writesTo
managedBy

### Example

VM1 -> connectedTo -> SubnetA
VM1 -> dependsOn -> Database01
Database01 -> protectedBy -> Firewall01

---

## Volume B - PostgreSQL Schema Strategy

### Document Layer

documents
chunks
document_registry

### Memory Layer

memory_items
memory_sessions
memory_summaries

### Observability Layer

workflow_runs
agent_runs
validation_results

### Security Layer

audit_log

---

## Volume C - Agent Contracts

Every agent should expose:

```python
def run(state: dict) -> dict:
    pass
```

### Router Agent

Input:

question

Output:

route

Possible routes:

- vector
- graph
- hybrid
- action

### Memory Agent

Input:

question

Output:

selected memory

### Validator Agent

Output:

confidence score
warnings
approval flag

---

## Volume D - DevOps Expansion

Future integrations:

AWS
Azure
VMware
Proxmox
VirtualBox
Kubernetes

### Read Only Mode

Phase 1:

Collect inventory only.

### Recommendation Mode

Phase 2:

Suggest actions.

### Approval Mode

Phase 3:

Request approval.

### Execution Mode

Phase 4:

Execute actions.

---

## Volume E - MCP Integration

Future MCP servers:

Filesystem MCP
GitHub MCP
PostgreSQL MCP
GraphDB MCP
AWS MCP
Azure MCP

Purpose:

Allow agents to access tools safely.

---

## Volume F - Performance Targets

Query latency:

< 5 seconds

Vector search:

< 500 ms

Graph query:

< 500 ms

Validation:

< 1 second

---

## Volume G - Production Readiness Checklist

Environment
Database
GraphDB
LLM
Agents
Tests
Security
Monitoring
Backups
Documentation

Every item must be validated before production.

---

## Volume H - Recommended Next Deliverables

1. Full PostgreSQL schema document
2. Full GraphDB ontology document
3. LangGraph implementation document
4. Agent implementation document
5. FastAPI API specification
6. Docker deployment guide
7. Ubuntu operations guide
8. GitHub workflow guide
9. Codex usage guide
10. GraphRAG implementation guide

This document continues the master plan and serves as the foundation for the next engineering volumes.
