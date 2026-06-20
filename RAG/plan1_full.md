# ProjectRAG Professional Master Plan — Ubuntu Linux Edition

**Version:** 2.0  
**Target OS:** Ubuntu Linux 24.x  
**Architecture:** Multi-Agent GraphRAG without n8n  
**Generated:** 2026-06-16  

---

## Document Purpose

This document rewrites and professionalizes the previous ProjectRAG plan into a complete Ubuntu-based engineering blueprint.

The previous plan contained the correct core idea:

- an LLM matrix;
- RAG optimization;
- memory management;
- resource-aware model allocation;
- ingestion;
- validation;
- duplicate protection;
- document management;
- DevOps automation;
- later Graph-RAG expansion.

This new version removes **all n8n dependency**.

All process orchestration is redesigned with:

```text
Python + FastAPI + LangGraph
```

The resulting project is a local-first, professional, extensible Multi-Agent GraphRAG platform.

---

# Table of Contents

1. Executive Summary  
2. Design Principles  
3. What Is Removed from the Old Plan  
4. What Replaces n8n  
5. Target Architecture  
6. Ubuntu 24.x Workstation Setup  
7. Project Repository Strategy  
8. VS Code + Codex Integration  
9. GitHub Safe Workflow  
10. Python Environment  
11. Docker Architecture  
12. PostgreSQL + pgvector Layer  
13. GraphDB Layer  
14. Ollama Local LLM Layer  
15. FastAPI Control Plane  
16. LangGraph Orchestration Plane  
17. LLM Matrix Architecture  
18. Agent Specifications  
19. Memory Architecture  
20. RAG Pipeline  
21. GraphRAG Pipeline  
22. Hybrid Retrieval Pipeline  
23. Duplicate Document Protection  
24. Document Registry  
25. Document Management Endpoints  
26. Validation Layer  
27. Observability Layer  
28. Security Model  
29. Testing Strategy  
30. DevOps Extension Roadmap  
31. Implementation Steps  
32. File-by-File Blueprint  
33. Operational Commands  
34. Troubleshooting  
35. Final Roadmap  

---

# 1. Executive Summary

ProjectRAG is a local-first AI system designed to manage Retrieval-Augmented Generation, memory, reasoning, and future infrastructure automation through an LLM matrix.

The original project idea was correct: instead of using one large model for everything, the system should use a matrix of specialized agents and services.

The new design uses:

```text
FastAPI        -> API/control interface
LangGraph      -> workflow orchestration
PostgreSQL     -> metadata, logs, memory, registry
pgvector       -> vector similarity search
GraphDB        -> semantic graph, topology, relationships, reasoning
Ollama         -> local LLM and embeddings
VS Code        -> development environment
Codex          -> coding assistant
GitHub         -> safe source control
Docker Compose -> local infrastructure
```

The major architectural change is:

```text
OLD:
User -> n8n -> FastAPI / Qdrant / Redis / Postgres / LLM

NEW:
User -> FastAPI -> LangGraph -> Agents -> PostgreSQL + pgvector + GraphDB + Ollama
```

The new system is more professional because:

- code is version-controlled;
- workflows are testable;
- execution state is explicit;
- agents are modular;
- databases have clear responsibilities;
- the system can later scale to Kubernetes, cloud, or enterprise deployment.

---

# 2. Design Principles

## 2.1 Remove Visual Workflow Dependency

n8n is useful for simple automation, but this project needs:

- advanced state management;
- agent coordination;
- reliable testing;
- version-controlled workflow logic;
- Python-native AI orchestration;
- GraphRAG reasoning;
- future DevOps execution safety.

Therefore, n8n is replaced by LangGraph.

## 2.2 Keep the System Local First

Your laptop has:

```text
RAM: 32 GB
Storage: 1 TB HDD
GPU: 4 GB
OS: Ubuntu Linux 24.x
```

This is enough for a strong local prototype if the design is efficient.

Recommended local limits:

```text
Run one main LLM at a time.
Use one embedding model.
Keep PostgreSQL and GraphDB local.
Avoid Kubernetes initially.
Avoid unnecessary microservices initially.
```

## 2.3 Separate Responsibilities

Each layer must have one clear job:

```text
FastAPI     -> receive requests
LangGraph   -> orchestrate workflows
Agents      -> perform specialized decisions
PostgreSQL  -> structured storage
pgvector    -> vector retrieval
GraphDB     -> graph reasoning
Ollama      -> local model inference
GitHub      -> version control
```

## 2.4 Use Hybrid Retrieval

Vector retrieval answers:

```text
Which text chunks are semantically similar?
```

Graph retrieval answers:

```text
Which entities are connected, dependent, or inferable?
```

Hybrid retrieval combines both.

This is the foundation of GraphRAG.

---

# 3. What Is Removed from the Old Plan

The old plan included n8n workflows and n8n nodes.

The following are removed:

```text
n8n workflow orchestration
n8n webhooks
n8n credentials
n8n visual flows
n8n action nodes
n8n API execution chains
n8n memory routing
n8n error handling
n8n scheduler
```

The system no longer depends on n8n for:

- ingestion;
- retrieval;
- validation;
- memory routing;
- DevOps execution;
- API workflow control.

---

# 4. What Replaces n8n

n8n is replaced by a Python-native execution model:

```text
LangGraph workflow nodes
FastAPI endpoints
Python service classes
Background workers
CLI scripts
GitHub Actions later
```

Mapping:

| Old n8n Function | New Component |
|---|---|
| n8n webhook | FastAPI endpoint |
| n8n workflow | LangGraph graph |
| n8n node | Python function / agent node |
| n8n credentials | .env + secrets management |
| n8n scheduler | APScheduler / cron / systemd timer |
| n8n action execution | Python tool executor |
| n8n branching | LangGraph conditional edges |
| n8n error path | LangGraph error node |
| n8n logs | PostgreSQL + structured logging |

Effect:

```text
The workflow becomes code.
The workflow can be tested.
The workflow can be committed to GitHub.
The workflow can be reviewed.
The workflow can scale.
```

---

# 5. Target Architecture

## 5.1 High-Level Architecture

```text
User / CLI / Web UI / Voice Interface
        |
        v
FastAPI Control Plane
        |
        v
LangGraph Orchestration Plane
        |
        +--> Router Agent
        +--> Query Rewrite Agent
        +--> Vector Retrieval Agent
        +--> Graph Retrieval Agent
        +--> Memory Agent
        +--> Context Compression Agent
        +--> Reasoning Agent
        +--> Validation Agent
        +--> Tool Execution Agent
        |
        v
Storage + Model Layer
        |
        +--> PostgreSQL
        +--> pgvector
        +--> GraphDB
        +--> Ollama
        +--> Local Filesystem
```

## 5.2 Request Lifecycle

```text
1. User sends a question.
2. FastAPI receives the request.
3. LangGraph initializes workflow state.
4. Router Agent classifies the question.
5. Memory Agent selects relevant memory.
6. Vector Agent retrieves semantically similar chunks.
7. Graph Agent retrieves relationships and dependencies.
8. Reasoning Agent creates answer.
9. Validation Agent checks answer.
10. FastAPI returns final response.
```

## 5.3 Why This Architecture Is Better

It improves:

- traceability;
- retrieval quality;
- memory selection;
- agent specialization;
- cost control;
- local execution;
- future DevOps integration;
- safety for automation.

---

# 6. Ubuntu Linux 24.x Workstation Setup

## 6.1 System Update

Run:

```bash
sudo apt update
sudo apt upgrade -y
```

Purpose:

- update package index;
- install security patches;
- prepare base OS.

Effect:

```text
The workstation becomes stable and current.
```

## 6.2 Install Core Tools

```bash
sudo apt install -y \
  git \
  curl \
  wget \
  unzip \
  build-essential \
  ca-certificates \
  gnupg \
  lsb-release \
  python3 \
  python3-pip \
  python3-venv \
  python3-dev \
  postgresql-client \
  jq \
  tree \
  htop
```

Purpose:

- Git for source control;
- Python for backend;
- curl/wget for downloads;
- build-essential for package compilation;
- PostgreSQL client for DB access;
- jq for JSON processing;
- htop for resource monitoring.

Effect:

```text
Ubuntu becomes ready for Python, Docker, databases, and AI development.
```

## 6.3 Install Docker

```bash
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and log back in.

Test:

```bash
docker --version
docker compose version
docker ps
```

Purpose:

- run PostgreSQL;
- run GraphDB;
- optionally run supporting services.

Effect:

```text
Local infrastructure can be started reproducibly.
```

## 6.4 Install VS Code

Recommended installation:

```bash
sudo snap install code --classic
```

Purpose:

```text
Main development IDE.
```

## 6.5 Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Test:

```bash
ollama --version
```

Pull recommended models:

```bash
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull phi3
ollama pull nomic-embed-text
```

For your laptop, start with:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Effect:

```text
Local LLM and local embedding model are available.
```

---

# 7. Project Repository Strategy

## 7.1 Repository Name

Recommended:

```text
project-rag
```

Alternative:

```text
project-graphrag-agent
rag-matrix
llm-matrix-rag
```

## 7.2 Repository Visibility

Use:

```text
Private repository
```

Reason:

- you may store infrastructure examples;
- you may add logs;
- you may later include internal scripts;
- you avoid accidental exposure.

## 7.3 Clone Repository

```bash
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:YOUR_USER/project-rag.git
cd project-rag
```

If using HTTPS:

```bash
git clone https://github.com/YOUR_USER/project-rag.git
```

## 7.4 Initial Branch Strategy

Branches:

```text
main
develop
feature/*
fix/*
docs/*
```

Workflow:

```bash
git checkout -b feature/base-architecture
```

Effect:

```text
Main branch stays stable.
Development is isolated.
```

---

# 8. VS Code + Codex Integration

## 8.1 Open Project

```bash
cd ~/projects/project-rag
code .
```

## 8.2 Recommended VS Code Extensions

Install:

```text
Python
Pylance
Docker
GitHub Pull Requests
PostgreSQL
YAML
Markdown All in One
Codex
```

## 8.3 How to Use Codex Safely

Good prompts:

```text
Analyze this repository. Do not modify files yet.
```

```text
Create app/rag/chunking.py with a safe chunk_text function. Show the diff before saving.
```

```text
Review this module for security issues and database connection problems.
```

Bad prompts:

```text
Rewrite everything.
Delete unused files.
Commit all files.
Push to GitHub.
```

Rule:

```text
Codex can help write code, but you review every diff before commit.
```

---

# 9. GitHub Safe Workflow

## 9.1 .gitignore

Create:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.env
.env.*
!.env.example
*.log
*.sqlite
*.db
data/raw/
data/processed/
data/private/
exports/
.vscode/settings.json
.DS_Store
```

Purpose:

- prevent secrets;
- prevent local environment files;
- prevent private documents;
- prevent cache files.

Effect:

```text
GitHub remains safe.
```

## 9.2 .env.example

Create:

```env
APP_ENV=local
APP_HOST=0.0.0.0
APP_PORT=8000

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=projectrag
POSTGRES_USER=projectrag
POSTGRES_PASSWORD=change_me

GRAPHDB_URL=http://localhost:7200
GRAPHDB_REPOSITORY=projectrag

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EMBEDDING_MODEL=nomic-embed-text
```

## 9.3 Private .env

```bash
cp .env.example .env
nano .env
```

Never commit `.env`.

## 9.4 Secret Scan

Install:

```bash
source .venv/bin/activate
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

Before commit:

```bash
git status
git diff
grep -R "api_key\|secret\|password\|token" .
```

---

# 10. Python Environment

## 10.1 Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Effect:

```text
Project dependencies do not pollute system Python.
```

## 10.2 Install Dependencies

```bash
pip install --upgrade pip setuptools wheel

pip install \
  fastapi \
  uvicorn[standard] \
  pydantic \
  pydantic-settings \
  python-dotenv \
  sqlalchemy \
  psycopg2-binary \
  pgvector \
  requests \
  rdflib \
  langgraph \
  langchain \
  pytest \
  httpx \
  rich
```

Save:

```bash
pip freeze > requirements.txt
```

---

# 11. Project Folder Structure

Create:

```bash
mkdir -p app/{{api,agents,core,graph,memory,rag,tools,workflows}}
mkdir -p scripts tests docs data/{{raw,processed,private,exports}}
touch app/__init__.py
touch app/main.py
touch app/core/config.py
touch README.md
touch .env.example
touch .gitignore
```

Final structure:

```text
project-rag/
├── app/
│   ├── main.py
│   ├── api/
│   ├── agents/
│   ├── core/
│   ├── graph/
│   ├── memory/
│   ├── rag/
│   ├── tools/
│   └── workflows/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── private/
│   └── exports/
├── docs/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

Purpose:

```text
Every component has a predictable location.
```

---

# 12. Docker Compose Architecture

Create `docker-compose.yml`:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: projectrag-postgres
    environment:
      POSTGRES_DB: projectrag
      POSTGRES_USER: projectrag
      POSTGRES_PASSWORD: projectrag_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U projectrag -d projectrag"]
      interval: 10s
      timeout: 5s
      retries: 5

  graphdb:
    image: ontotext/graphdb:latest
    container_name: projectrag-graphdb
    ports:
      - "7200:7200"
    volumes:
      - graphdb_data:/opt/graphdb/home

volumes:
  postgres_data:
  graphdb_data:
```

Start:

```bash
docker compose up -d
```

Check:

```bash
docker ps
```

Effect:

```text
PostgreSQL and GraphDB run locally in containers.
```

---

# 13. PostgreSQL + pgvector Layer

## 13.1 Purpose

PostgreSQL stores:

- documents;
- chunks;
- embeddings;
- metadata;
- registry;
- memory;
- workflow logs;
- validation records.

pgvector stores embeddings for similarity search.

## 13.2 Database Initialization

Create `scripts/init_postgres.sql`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    source_path TEXT,
    file_hash TEXT UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{{}}'::jsonb,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB DEFAULT '{{}}'::jsonb,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON documents(file_hash);
```

Run:

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

Effect:

```text
PostgreSQL becomes ready for RAG storage.
```

---

# 14. GraphDB Layer

## 14.1 Purpose

GraphDB stores:

- entities;
- relationships;
- infrastructure topology;
- application dependencies;
- semantic facts;
- ontology rules.

It answers relationship questions:

```text
What depends on VM1?
Which service uses database X?
What infrastructure component is affected if Firewall01 fails?
```

## 14.2 Repository Setup

Open:

```text
http://localhost:7200
```

Create repository:

```text
Repository ID: projectrag
Ruleset: RDFS-Plus
```

## 14.3 RDF Model

Example triples:

```text
project:VM1 project:connectedTo project:SubnetA .
project:SubnetA project:belongsTo project:VNetDev .
project:VNetDev project:protectedBy project:Firewall01 .
```

## 14.4 SPARQL Example

```sparql
PREFIX project: <http://projectrag.local/>

SELECT ?dependency
WHERE {{
  project:VM1 project:connectedTo ?dependency .
}}
```

Effect:

```text
The system can reason over relationships instead of only text.
```

---

# 15. Ollama Local LLM Layer

## 15.1 Purpose

Ollama provides:

- local LLM inference;
- local embeddings;
- free prototype execution;
- no external API dependency.

## 15.2 Recommended Models

For your laptop:

```text
Primary LLM: llama3.1:8b
Alternative: qwen2.5:7b
Light model: phi3
Embedding: nomic-embed-text
```

## 15.3 Resource Strategy

Rules:

```text
Use small model for routing.
Use embedding model for retrieval.
Use stronger model for reasoning.
Do not run multiple heavy models simultaneously.
```

Effect:

```text
Good local performance without exhausting RAM/GPU.
```

---

# 16. FastAPI Control Plane

## 16.1 Purpose

FastAPI is the main API layer.

It exposes:

```text
GET  /health
POST /query
POST /ingest
GET  /documents
DELETE /documents/{{id}}
POST /documents/{{id}}/reindex
GET  /graph/entities
POST /graph/query
```

## 16.2 Minimal App

Create `app/main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from app.workflows.rag_workflow import build_workflow

app = FastAPI(title="ProjectRAG")
workflow = build_workflow()

class QueryRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {{"status": "ok", "service": "ProjectRAG"}}

@app.post("/query")
def query(request: QueryRequest):
    state = {{
        "question": request.question,
        "route": "",
        "vector_context": [],
        "graph_context": [],
        "memory_context": [],
        "answer": "",
        "validation": {{}}
    }}
    return workflow.invoke(state)
```

Run:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

Effect:

```text
The system has an API entry point.
```

---

# 17. LangGraph Orchestration Plane

## 17.1 Purpose

LangGraph replaces n8n.

It manages:

- state;
- branching;
- retries;
- agent coordination;
- validation;
- workflow execution.

## 17.2 State Object

```python
from typing import TypedDict, List, Dict, Any

class RAGState(TypedDict):
    question: str
    route: str
    vector_context: List[Dict[str, Any]]
    graph_context: List[Dict[str, Any]]
    memory_context: List[Dict[str, Any]]
    answer: str
    validation: Dict[str, Any]
```

## 17.3 Workflow Nodes

```text
query_router
memory_selector
vector_retriever
graph_retriever
context_merger
reasoner
validator
response_builder
```

## 17.4 Workflow Effect

```text
The old n8n workflow becomes deterministic, testable Python code.
```

---

# 18. LLM Matrix Architecture

## 18.1 Concept

The LLM matrix is a control-plane plus worker-plane model.

```text
Controller
  ├── Router
  ├── Retriever
  ├── Memory
  ├── Reasoner
  ├── Validator
  └── Executor
```

## 18.2 Why It Works

One LLM doing everything is inefficient.

A matrix improves:

- cost;
- latency;
- accuracy;
- memory usage;
- specialization;
- explainability.

## 18.3 Model Allocation Strategy

| Task | Model Type |
|---|---|
| Classification | small model or rules |
| Query rewrite | small/medium model |
| Embedding | embedding model |
| Reasoning | stronger model |
| Validation | medium/strong model |
| Tool execution planning | strong model |

Effect:

```text
The system uses expensive reasoning only where needed.
```

---

# 19. Agent Specifications

## 19.1 Router Agent

Input:

```text
User question
```

Output:

```text
vector | graph | hybrid | action | memory
```

Purpose:

```text
Choose the correct workflow path.
```

Effect:

```text
Avoids unnecessary retrieval and model calls.
```

## 19.2 Vector Retrieval Agent

Purpose:

```text
Search PostgreSQL/pgvector for similar chunks.
```

Effect:

```text
Retrieves relevant document evidence.
```

## 19.3 Graph Retrieval Agent

Purpose:

```text
Search GraphDB for relationships and dependencies.
```

Effect:

```text
Adds topology and semantic reasoning.
```

## 19.4 Memory Agent

Purpose:

```text
Select relevant memory from previous interactions and project knowledge.
```

Effect:

```text
Improves continuity without overloading the prompt.
```

## 19.5 Context Compression Agent

Purpose:

```text
Reduce retrieved context before final reasoning.
```

Effect:

```text
Lower token usage and cleaner answers.
```

## 19.6 Reasoning Agent

Purpose:

```text
Generate final answer from evidence.
```

Effect:

```text
Synthesizes vector, graph, and memory context.
```

## 19.7 Validator Agent

Purpose:

```text
Check answer grounding, consistency, and risk.
```

Effect:

```text
Reduces hallucination.
```

---

# 20. Memory Architecture

## 20.1 Short-Term Memory

Stores:

```text
current request
current workflow state
temporary intermediate results
```

Location:

```text
LangGraph state
```

## 20.2 Working Memory

Stores:

```text
current multi-step task
active retrieval context
selected graph facts
```

Location:

```text
LangGraph state + PostgreSQL workflow_runs
```

## 20.3 Long-Term Memory

Stores:

```text
persistent project facts
architecture decisions
user preferences
historical answers
```

Location:

```text
PostgreSQL
```

## 20.4 Semantic Memory

Stores:

```text
entities
facts
relationships
ontology
```

Location:

```text
GraphDB
```

## 20.5 Procedural Memory

Stores:

```text
runbooks
commands
deployment steps
known workflows
```

Location:

```text
PostgreSQL + GraphDB
```

## 20.6 Episodic Memory

Stores:

```text
previous incidents
previous actions
previous troubleshooting sessions
```

Location:

```text
PostgreSQL
```

Effect:

```text
Memory is structured instead of blindly appended to prompts.
```

---

# 21. RAG Pipeline

## 21.1 Pipeline Flow

```text
Document
 -> Load
 -> Clean
 -> Split
 -> Chunk
 -> Embed
 -> Store in PostgreSQL
 -> Search with pgvector
```

## 21.2 Purpose

RAG gives the LLM access to external knowledge.

## 21.3 Effect

```text
The system answers from project documents instead of model memory.
```

---

# 22. Chunking Strategy

## 22.1 Recommended Defaults

```text
chunk_size: 800–1200 characters initially
overlap: 100–200 characters
```

Later use token-based chunking.

## 22.2 Why Overlap Matters

Overlap preserves context between chunks.

Effect:

```text
Less information loss at chunk boundaries.
```

---

# 23. Embedding Strategy

## 23.1 Local Embeddings

Use:

```text
nomic-embed-text
```

## 23.2 Embedding Flow

```text
Text chunk -> Ollama embedding API -> vector -> pgvector
```

## 23.3 Effect

```text
Text becomes searchable by meaning.
```

---

# 24. GraphRAG Pipeline

## 24.1 Entity Extraction

Input:

```text
document chunk
```

Output:

```text
entities such as VM, subnet, database, service, firewall
```

## 24.2 Relationship Extraction

Input:

```text
entities + text
```

Output:

```text
VM1 connectedTo SubnetA
ServiceA dependsOn DatabaseB
Firewall01 blocks Port443
```

## 24.3 Store in GraphDB

Triples:

```text
subject predicate object
```

## 24.4 Effect

```text
The system can reason over dependency chains.
```

---

# 25. Hybrid Retrieval

## 25.1 Vector Retrieval

Finds similar text.

## 25.2 Graph Retrieval

Finds connected facts.

## 25.3 Merge Layer

Combines:

```text
top vector chunks
top graph paths
selected memory
```

## 25.4 Effect

```text
Answers become both evidence-based and relationship-aware.
```

---

# 26. Duplicate Document Protection

## 26.1 Problem

Without protection, ingestion may store the same document repeatedly.

## 26.2 Solution

Calculate SHA-256 hash for each file.

```python
import hashlib
from pathlib import Path

def calculate_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
```

## 26.3 Effect

```text
Duplicate files are skipped.
Database stays clean.
Retrieval quality stays stable.
```

---

# 27. Document Registry

## 27.1 Purpose

Track ingested files.

Fields:

```text
id
filename
file_hash
created_at
metadata
```

## 27.2 Effect

```text
You know exactly what has been ingested.
```

---

# 28. Document Management Endpoints

## 28.1 List Documents

```text
GET /documents
```

Purpose:

```text
Show all ingested documents.
```

## 28.2 Delete Document

```text
DELETE /documents/{{id}}
```

Purpose:

```text
Remove document and chunks.
```

## 28.3 Reindex Document

```text
POST /documents/{{id}}/reindex
```

Purpose:

```text
Recreate chunks and embeddings.
```

Effect:

```text
The RAG knowledge base becomes manageable.
```

---

# 29. Validation Layer

## 29.1 Validation Checks

Check:

```text
Was answer based on retrieved context?
Are graph facts consistent?
Are citations available?
Is confidence high enough?
Is action safe?
```

## 29.2 Validation Output

```json
{{
  "grounded": true,
  "confidence": 0.86,
  "warnings": [],
  "requires_human_approval": false
}}
```

## 29.3 Effect

```text
Reduces hallucination and unsafe outputs.
```

---

# 30. Observability Layer

## 30.1 Metrics

Track:

```text
latency
retrieval time
embedding time
LLM time
token usage
chunk count
graph query count
validation score
```

## 30.2 Logs

Use structured logs.

Example:

```json
{{
  "event": "query_completed",
  "route": "hybrid",
  "latency_ms": 1234,
  "chunks": 5,
  "graph_paths": 3
}}
```

## 30.3 Effect

```text
You can tune and debug the system.
```

---

# 31. Security Model

## 31.1 Secrets

Never commit:

```text
.env
API keys
SSH keys
cloud credentials
database dumps
private logs
```

## 31.2 Least Privilege

Each component should have only required access.

## 31.3 DevOps Safety

For future automation:

```text
read-only first
recommendation second
human approval third
execution last
```

Effect:

```text
The system is safe before it becomes powerful.
```

---

# 32. Testing Strategy

## 32.1 Unit Tests

Test:

```text
chunking
hashing
embedding client
database client
router logic
```

## 32.2 Integration Tests

Test:

```text
FastAPI endpoint
PostgreSQL connection
GraphDB query
Ollama request
LangGraph workflow
```

## 32.3 RAG Quality Tests

Test:

```text
known question -> expected document
known entity -> expected graph relation
known topology -> expected dependency chain
```

Effect:

```text
Quality becomes measurable.
```

---

# 33. Implementation Roadmap

## Phase 1 — Base Environment

Goal:

```text
Ubuntu + VS Code + GitHub + Python + Docker
```

Deliverable:

```text
Repository opens and runs locally.
```

## Phase 2 — FastAPI

Goal:

```text
Create health and query endpoints.
```

Deliverable:

```text
API responds at /docs.
```

## Phase 3 — PostgreSQL + pgvector

Goal:

```text
Store documents and embeddings.
```

Deliverable:

```text
Vector search works.
```

## Phase 4 — GraphDB

Goal:

```text
Store entities and relationships.
```

Deliverable:

```text
SPARQL queries work.
```

## Phase 5 — Ollama

Goal:

```text
Local LLM and embeddings.
```

Deliverable:

```text
Embeddings generated locally.
```

## Phase 6 — LangGraph

Goal:

```text
Replace n8n orchestration.
```

Deliverable:

```text
Router -> Retriever -> Reasoner -> Validator workflow.
```

## Phase 7 — Hybrid GraphRAG

Goal:

```text
Combine vector and graph retrieval.
```

Deliverable:

```text
Answers use text + relationships.
```

## Phase 8 — Document Management

Goal:

```text
List, delete, reindex documents.
```

Deliverable:

```text
Operational RAG knowledge base.
```

## Phase 9 — Memory

Goal:

```text
Add long-term and semantic memory.
```

Deliverable:

```text
Memory-aware answering.
```

## Phase 10 — DevOps Extension

Goal:

```text
Analyze infrastructure data.
```

Deliverable:

```text
Topology-aware DevOps assistant.
```

---

# 34. Detailed Implementation Steps

## Step 1 — Prepare Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

What it does:

```text
Updates the OS package catalog and installed packages.
```

Effect:

```text
Stable base system.
```

## Step 2 — Install Tools

```bash
sudo apt install -y git curl wget unzip build-essential python3 python3-pip python3-venv docker.io docker-compose-v2
```

What it does:

```text
Installs development and container tools.
```

Effect:

```text
System can build and run the project.
```

## Step 3 — Create Project Directory

```bash
mkdir -p ~/projects
cd ~/projects
```

Effect:

```text
All project files are organized.
```

## Step 4 — Clone GitHub Repository

```bash
git clone git@github.com:YOUR_USER/project-rag.git
cd project-rag
```

Effect:

```text
Local repository is connected to GitHub.
```

## Step 5 — Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Effect:

```text
Python dependencies are isolated.
```

## Step 6 — Install Python Packages

```bash
pip install fastapi uvicorn[standard] langgraph sqlalchemy psycopg2-binary pgvector requests rdflib python-dotenv pydantic pydantic-settings pytest
pip freeze > requirements.txt
```

Effect:

```text
Core Python runtime is ready.
```

## Step 7 — Create Folder Structure

```bash
mkdir -p app/{{agents,rag,graph,memory,workflows,api,core,tools}}
mkdir -p scripts tests docs data/{{raw,processed,private,exports}}
touch app/__init__.py
```

Effect:

```text
Project has clean architecture.
```

## Step 8 — Create Docker Compose

Create PostgreSQL and GraphDB services.

Effect:

```text
Databases can run locally.
```

## Step 9 — Start Databases

```bash
docker compose up -d
docker ps
```

Effect:

```text
PostgreSQL and GraphDB are available.
```

## Step 10 — Initialize PostgreSQL

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

Effect:

```text
Tables and vector extension are ready.
```

## Step 11 — Create GraphDB Repository

Open:

```text
http://localhost:7200
```

Create:

```text
projectrag
```

Effect:

```text
Graph database is ready.
```

## Step 12 — Install Ollama Models

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Effect:

```text
Local LLM and embedding model are ready.
```

## Step 13 — Create FastAPI App

Create `app/main.py`.

Effect:

```text
The project exposes an API.
```

## Step 14 — Create Config Module

Create `app/core/config.py`.

Effect:

```text
Environment variables are loaded safely.
```

## Step 15 — Create PostgreSQL Client

Create `app/memory/postgres.py`.

Effect:

```text
Python can talk to PostgreSQL.
```

## Step 16 — Create GraphDB Client

Create `app/graph/graphdb_client.py`.

Effect:

```text
Python can query GraphDB.
```

## Step 17 — Create Ollama Client

Create `app/tools/ollama_client.py`.

Effect:

```text
Python can request embeddings and LLM output.
```

## Step 18 — Create Chunking Module

Create `app/rag/chunking.py`.

Effect:

```text
Documents can be split into chunks.
```

## Step 19 — Create Ingestion Module

Create `app/rag/ingestion.py`.

Effect:

```text
Documents can be loaded and stored.
```

## Step 20 — Create Vector Retriever

Create `app/agents/vector_retriever.py`.

Effect:

```text
Questions can retrieve relevant chunks.
```

## Step 21 — Create Graph Retriever

Create `app/agents/graph_retriever.py`.

Effect:

```text
Questions can retrieve relationships.
```

## Step 22 — Create Router Agent

Create `app/agents/router.py`.

Effect:

```text
Workflow path is selected automatically.
```

## Step 23 — Create Reasoner Agent

Create `app/agents/reasoner.py`.

Effect:

```text
The system can generate answers.
```

## Step 24 — Create Validator Agent

Create `app/agents/validator.py`.

Effect:

```text
Answers are checked before response.
```

## Step 25 — Create LangGraph Workflow

Create `app/workflows/rag_workflow.py`.

Effect:

```text
The complete RAG workflow runs without n8n.
```

## Step 26 — Connect Workflow to API

Modify `app/main.py`.

Effect:

```text
API calls execute the full workflow.
```

## Step 27 — Add Document Endpoints

Create:

```text
GET /documents
DELETE /documents/{{id}}
POST /documents/{{id}}/reindex
```

Effect:

```text
Knowledge base becomes manageable.
```

## Step 28 — Add Tests

Create tests for:

```text
chunking
hashing
API health
workflow routing
database connection
```

Effect:

```text
Regression protection.
```

## Step 29 — Commit Safely

```bash
git status
git diff
git add app scripts tests docs README.md requirements.txt docker-compose.yml .gitignore .env.example
git commit -m "Add ProjectRAG no-n8n base architecture"
git push origin feature/base-architecture
```

Effect:

```text
Progress is saved safely.
```

---

# 35. File-by-File Blueprint

## app/main.py

Purpose:

```text
FastAPI application entry point.
```

Responsibilities:

- expose API;
- call LangGraph workflow;
- return response.

## app/core/config.py

Purpose:

```text
Load environment variables.
```

Responsibilities:

- database config;
- GraphDB config;
- Ollama config.

## app/workflows/rag_workflow.py

Purpose:

```text
Main LangGraph workflow.
```

Responsibilities:

- connect agents;
- manage state;
- replace n8n.

## app/agents/router.py

Purpose:

```text
Classify query route.
```

## app/agents/vector_retriever.py

Purpose:

```text
Retrieve text chunks from pgvector.
```

## app/agents/graph_retriever.py

Purpose:

```text
Retrieve relations from GraphDB.
```

## app/agents/reasoner.py

Purpose:

```text
Generate final answer.
```

## app/agents/validator.py

Purpose:

```text
Validate answer.
```

## app/rag/chunking.py

Purpose:

```text
Split documents.
```

## app/rag/ingestion.py

Purpose:

```text
Ingest documents.
```

## app/graph/graphdb_client.py

Purpose:

```text
SPARQL interface.
```

## app/memory/postgres.py

Purpose:

```text
PostgreSQL connection and queries.
```

---

# 36. Operational Commands

## Start Infrastructure

```bash
docker compose up -d
```

## Stop Infrastructure

```bash
docker compose down
```

## Start API

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

## Test Health

```bash
curl http://localhost:8000/health
```

## Test Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{{"question": "What depends on VM1?"}}'
```

## Check Logs

```bash
docker logs projectrag-postgres
docker logs projectrag-graphdb
```

---

# 37. Troubleshooting

## Docker Permission Denied

Fix:

```bash
sudo usermod -aG docker $USER
```

Log out and log back in.

## PostgreSQL Connection Refused

Check:

```bash
docker ps
docker logs projectrag-postgres
```

## GraphDB Not Opening

Check:

```bash
docker logs projectrag-graphdb
```

Open:

```text
http://localhost:7200
```

## Ollama Model Too Slow

Use smaller model:

```bash
ollama pull phi3
```

## Python Import Errors

Run from repository root:

```bash
uvicorn app.main:app --reload
```

---

# 38. Professional Recommendations

## Start Simple

Do not add cloud, Kubernetes, Redis, or CI/CD initially.

## Build in Order

```text
API first
Database second
RAG third
GraphDB fourth
LangGraph fifth
Validation sixth
Memory seventh
DevOps agents last
```

## Keep GraphDB Central

GraphDB is not just storage.

It is your semantic reasoning layer.

## Keep PostgreSQL Central

PostgreSQL is your operational truth.

It stores:

- documents;
- chunks;
- memory;
- logs;
- registry.

## Use Codex as Assistant, Not Owner

Codex should help implement.

You remain the reviewer.

---

# 39. Final Architecture Summary

```text
Ubuntu 24.x Laptop
 |
 +-- VS Code + Codex
 |
 +-- GitHub Repository
 |
 +-- Docker Compose
 |    +-- PostgreSQL + pgvector
 |    +-- GraphDB
 |
 +-- Ollama
 |
 +-- FastAPI
 |
 +-- LangGraph
 |
 +-- Agent Matrix
      +-- Router
      +-- Vector Retriever
      +-- Graph Retriever
      +-- Memory Selector
      +-- Context Compressor
      +-- Reasoner
      +-- Validator
```

Final result:

```text
A professional, local-first, no-n8n Multi-Agent GraphRAG platform.
```

---

# 40. Next Engineering Deliverables

Recommended next documents:

```text
01_environment_setup.md
02_database_schema.md
03_graphdb_ontology.md
04_fastapi_design.md
05_langgraph_workflows.md
06_agent_specifications.md
07_rag_pipeline.md
08_graphrag_pipeline.md
09_security_model.md
10_operations_runbook.md
```

Recommended next implementation files:

```text
app/core/config.py
app/main.py
app/workflows/rag_workflow.py
app/tools/ollama_client.py
app/memory/postgres.py
app/graph/graphdb_client.py
app/rag/chunking.py
app/rag/ingestion.py
app/agents/router.py
app/agents/vector_retriever.py
app/agents/graph_retriever.py
app/agents/reasoner.py
app/agents/validator.py
```

---

# 41. Closing Statement

This architecture keeps the strongest part of the original idea: the LLM matrix for adaptive RAG, memory management, and resource allocation.

It removes the weakest part for this use case: n8n orchestration.

The new design is:

```text
more programmable
more testable
more secure
more scalable
better for GraphRAG
better for DevOps automation
better for GitHub
better for Ubuntu development
```

This is the correct professional direction for ProjectRAG.

# Appendix 1 — Router Agent Implementation Notes

This appendix expands the implementation details for routing rules, fallback logic, confidence scoring, and route telemetry.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 2 — Vector Retrieval Implementation Notes

This appendix expands the implementation details for embedding generation, pgvector search, top-k selection, thresholds, and metadata filtering.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 3 — Graph Retrieval Implementation Notes

This appendix expands the implementation details for SPARQL query templates, entity mapping, relationship expansion, and dependency depth limits.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 4 — Memory Management Implementation Notes

This appendix expands the implementation details for short-term state, long-term recall, summarization, and memory pruning.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 5 — Reasoning Implementation Notes

This appendix expands the implementation details for prompt assembly, context prioritization, citation discipline, and final answer construction.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 6 — Validation Implementation Notes

This appendix expands the implementation details for grounding checks, contradiction checks, risk checks, and confidence scoring.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 7 — Document Management Implementation Notes

This appendix expands the implementation details for list, delete, reindex, registry, hashes, and lifecycle control.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 8 — Observability Implementation Notes

This appendix expands the implementation details for structured logging, metrics, latency measurement, and debugging practices.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 9 — Security Implementation Notes

This appendix expands the implementation details for secrets, GitHub hygiene, least privilege, and safe execution boundaries.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit



# Appendix 10 — DevOps Future Extension Notes

This appendix expands the implementation details for read-only inventory, topology import, recommendation mode, approval mode, execution mode.

## Objective

The objective of this area is to make ProjectRAG operationally reliable and easy to extend.

## Design Rules

1. Keep the module small.
2. Keep inputs and outputs explicit.
3. Log important decisions.
4. Store durable facts in PostgreSQL or GraphDB.
5. Do not hide complex workflow logic inside prompts.
6. Prefer deterministic Python logic before using an LLM.
7. Add tests before expanding behavior.

## Recommended Implementation Pattern

Each module should expose a small public function:

```python
def run(state: dict) -> dict:
    ...
```

This makes the module compatible with LangGraph nodes.

## Expected Effects

A clean implementation gives:

- easier debugging;
- easier testing;
- safer changes;
- better performance;
- stronger architecture.

## Operational Checklist

- [ ] Input schema defined
- [ ] Output schema defined
- [ ] Error handling added
- [ ] Logs added
- [ ] Tests added
- [ ] Security reviewed
- [ ] Git diff reviewed before commit


# Appendix 11 — Full Sequential Implementation Backlog

This backlog converts the architecture into concrete engineering work items.


## Step 1 — Environment Work Item 1

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 2 — Environment Work Item 2

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 3 — Environment Work Item 3

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 4 — Environment Work Item 4

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 5 — Environment Work Item 5

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 6 — Environment Work Item 6

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 7 — Environment Work Item 7

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 8 — Environment Work Item 8

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 9 — Environment Work Item 9

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 10 — Environment Work Item 10

### What to do

Implement the next small, reviewable unit of the environment layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 11 — Repository and Security Work Item 11

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 12 — Repository and Security Work Item 12

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 13 — Repository and Security Work Item 13

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 14 — Repository and Security Work Item 14

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 15 — Repository and Security Work Item 15

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 16 — Repository and Security Work Item 16

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 17 — Repository and Security Work Item 17

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 18 — Repository and Security Work Item 18

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 19 — Repository and Security Work Item 19

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 20 — Repository and Security Work Item 20

### What to do

Implement the next small, reviewable unit of the repository and security layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 21 — Database Work Item 21

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 22 — Database Work Item 22

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 23 — Database Work Item 23

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 24 — Database Work Item 24

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 25 — Database Work Item 25

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 26 — Database Work Item 26

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 27 — Database Work Item 27

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 28 — Database Work Item 28

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 29 — Database Work Item 29

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 30 — Database Work Item 30

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 31 — Database Work Item 31

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 32 — Database Work Item 32

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 33 — Database Work Item 33

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 34 — Database Work Item 34

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 35 — Database Work Item 35

### What to do

Implement the next small, reviewable unit of the database layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 36 — GraphDB Work Item 36

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 37 — GraphDB Work Item 37

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 38 — GraphDB Work Item 38

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 39 — GraphDB Work Item 39

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 40 — GraphDB Work Item 40

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 41 — GraphDB Work Item 41

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 42 — GraphDB Work Item 42

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 43 — GraphDB Work Item 43

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 44 — GraphDB Work Item 44

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 45 — GraphDB Work Item 45

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 46 — GraphDB Work Item 46

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 47 — GraphDB Work Item 47

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 48 — GraphDB Work Item 48

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 49 — GraphDB Work Item 49

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 50 — GraphDB Work Item 50

### What to do

Implement the next small, reviewable unit of the graphdb layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 51 — Ollama and Embeddings Work Item 51

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 52 — Ollama and Embeddings Work Item 52

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 53 — Ollama and Embeddings Work Item 53

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 54 — Ollama and Embeddings Work Item 54

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 55 — Ollama and Embeddings Work Item 55

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 56 — Ollama and Embeddings Work Item 56

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 57 — Ollama and Embeddings Work Item 57

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 58 — Ollama and Embeddings Work Item 58

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 59 — Ollama and Embeddings Work Item 59

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 60 — Ollama and Embeddings Work Item 60

### What to do

Implement the next small, reviewable unit of the ollama and embeddings layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 61 — FastAPI Work Item 61

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 62 — FastAPI Work Item 62

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 63 — FastAPI Work Item 63

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 64 — FastAPI Work Item 64

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 65 — FastAPI Work Item 65

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 66 — FastAPI Work Item 66

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 67 — FastAPI Work Item 67

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 68 — FastAPI Work Item 68

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 69 — FastAPI Work Item 69

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 70 — FastAPI Work Item 70

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 71 — FastAPI Work Item 71

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 72 — FastAPI Work Item 72

### What to do

Implement the next small, reviewable unit of the fastapi layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 73 — LangGraph and Agents Work Item 73

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 74 — LangGraph and Agents Work Item 74

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 75 — LangGraph and Agents Work Item 75

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 76 — LangGraph and Agents Work Item 76

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 77 — LangGraph and Agents Work Item 77

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 78 — LangGraph and Agents Work Item 78

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 79 — LangGraph and Agents Work Item 79

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 80 — LangGraph and Agents Work Item 80

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 81 — LangGraph and Agents Work Item 81

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 82 — LangGraph and Agents Work Item 82

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 83 — LangGraph and Agents Work Item 83

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 84 — LangGraph and Agents Work Item 84

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 85 — LangGraph and Agents Work Item 85

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 86 — LangGraph and Agents Work Item 86

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 87 — LangGraph and Agents Work Item 87

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 88 — LangGraph and Agents Work Item 88

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 89 — LangGraph and Agents Work Item 89

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 90 — LangGraph and Agents Work Item 90

### What to do

Implement the next small, reviewable unit of the langgraph and agents layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 91 — RAG and GraphRAG Work Item 91

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 92 — RAG and GraphRAG Work Item 92

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 93 — RAG and GraphRAG Work Item 93

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 94 — RAG and GraphRAG Work Item 94

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 95 — RAG and GraphRAG Work Item 95

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 96 — RAG and GraphRAG Work Item 96

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 97 — RAG and GraphRAG Work Item 97

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 98 — RAG and GraphRAG Work Item 98

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 99 — RAG and GraphRAG Work Item 99

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 100 — RAG and GraphRAG Work Item 100

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 101 — RAG and GraphRAG Work Item 101

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 102 — RAG and GraphRAG Work Item 102

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 103 — RAG and GraphRAG Work Item 103

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 104 — RAG and GraphRAG Work Item 104

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 105 — RAG and GraphRAG Work Item 105

### What to do

Implement the next small, reviewable unit of the rag and graphrag layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 106 — Testing, Operations, and DevOps Extension Work Item 106

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 107 — Testing, Operations, and DevOps Extension Work Item 107

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 108 — Testing, Operations, and DevOps Extension Work Item 108

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 109 — Testing, Operations, and DevOps Extension Work Item 109

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 110 — Testing, Operations, and DevOps Extension Work Item 110

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 111 — Testing, Operations, and DevOps Extension Work Item 111

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 112 — Testing, Operations, and DevOps Extension Work Item 112

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 113 — Testing, Operations, and DevOps Extension Work Item 113

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 114 — Testing, Operations, and DevOps Extension Work Item 114

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 115 — Testing, Operations, and DevOps Extension Work Item 115

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 116 — Testing, Operations, and DevOps Extension Work Item 116

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 117 — Testing, Operations, and DevOps Extension Work Item 117

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 118 — Testing, Operations, and DevOps Extension Work Item 118

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 119 — Testing, Operations, and DevOps Extension Work Item 119

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.


## Step 120 — Testing, Operations, and DevOps Extension Work Item 120

### What to do

Implement the next small, reviewable unit of the testing, operations, and devops extension layer.

### Why it is needed

This step reduces project risk by moving one component from design to working implementation.

### Expected effect

After this step, ProjectRAG becomes more complete, more testable, and closer to a production-grade local prototype.

### Acceptance criteria

- Code or documentation exists.
- The change is committed in Git.
- No secrets are committed.
- The component can be tested or reviewed.
