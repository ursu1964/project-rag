
# ProjectRAG Master Plan - Part 3
# Database, Graph Ontology, LangGraph and Agent Engineering Volume

## Volume I - Complete PostgreSQL Logical Schema

### documents

Purpose:
Store original source documents.

Fields:

- id UUID PK
- filename TEXT
- source_path TEXT
- file_hash TEXT UNIQUE
- mime_type TEXT
- source_type TEXT
- metadata JSONB
- created_at TIMESTAMP

Indexes:

- file_hash
- filename
- created_at

---

### chunks

Purpose:
Store chunked document content.

Fields:

- id UUID PK
- document_id UUID FK
- chunk_index INTEGER
- chunk_text TEXT
- embedding VECTOR(768)
- token_count INTEGER
- metadata JSONB
- created_at TIMESTAMP

Indexes:

- document_id
- chunk_index

---

### document_registry

Purpose:
Prevent duplicate ingestion.

Fields:

- id UUID PK
- filename
- file_hash
- created_at

---

### workflow_runs

Purpose:
Track every workflow execution.

Fields:

- id UUID
- workflow_name
- start_time
- end_time
- duration_ms
- status
- metadata

---

### agent_runs

Purpose:
Track agent execution.

Fields:

- id UUID
- workflow_id UUID
- agent_name
- input_tokens
- output_tokens
- latency_ms
- status

---

### validation_results

Purpose:
Store validation outcomes.

Fields:

- id UUID
- workflow_id UUID
- confidence_score
- grounded
- warnings JSONB
- created_at

---

## Volume J - GraphDB Ontology

### Classes

Infrastructure:

- VM
- Host
- Cluster
- Network
- VNet
- Subnet
- Firewall
- Router
- Switch
- Storage
- Database

Application:

- Application
- Service
- API
- Queue
- Cache

Knowledge:

- Document
- Chunk
- Topic
- Tag

---

### Relationships

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

---

### Example RDF

VM1 connectedTo SubnetA
SubnetA belongsTo VNetDev
VNetDev protectedBy Firewall01

---

## Volume K - LangGraph State Model

```python
class RAGState(TypedDict):
    question: str
    route: str
    vector_context: list
    graph_context: list
    memory_context: list
    answer: str
    validation: dict
    metrics: dict
```
---

### Workflow Path

Router
 -> Memory
 -> Vector Retriever
 -> Graph Retriever
 -> Context Merger
 -> Reasoner
 -> Validator
 -> Response

---

### Error Path

Failure
 -> Retry
 -> Fallback
 -> Log
 -> Return Error

---

## Volume L - Agent Engineering

### Router Agent

Responsibilities:

- classify request
- determine workflow
- estimate complexity

Output:

vector
graph
hybrid
action

---

### Memory Agent

Responsibilities:

- select memories
- summarize context
- prune irrelevant items

---

### Vector Agent

Responsibilities:

- query embeddings
- rank chunks
- return evidence

---

### Graph Agent

Responsibilities:

- SPARQL execution
- relationship expansion
- dependency discovery

---

### Reasoning Agent

Responsibilities:

- build final answer
- synthesize context

---

### Validator Agent

Responsibilities:

- confidence scoring
- grounding checks
- contradiction detection

---

## Volume M - Resource Allocation Strategy

Small Models:

- routing
- classification
- summarization

Medium Models:

- validation
- context compression

Large Models:

- final reasoning
- action planning

Goal:

Reduce cost and latency.

---

## Volume N - Production Metrics

Track:

- workflow duration
- retrieval latency
- graph query latency
- LLM latency
- token usage
- validation score
- memory hit ratio

---

## Volume O - Backup Strategy

PostgreSQL:

daily backup

GraphDB:

daily export

Repository:

GitHub

Documents:

external backup location

---

## Volume P - Next Deliverables

01_postgresql_schema.md
02_graphdb_ontology.md
03_langgraph_workflows.md
04_agent_engineering.md
05_security_architecture.md
06_observability.md
07_graphrag_design.md
08_devops_extension.md
