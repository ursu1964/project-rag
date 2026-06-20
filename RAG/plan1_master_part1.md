# ProjectRAG Master Plan - Part 1
# Foundation, Vision, and No-n8n Architecture

**Version:** 1.0  
**Target OS:** Ubuntu Linux 24.x  
**Generated:** 2026-06-16  

---

## 1. Purpose

This document defines the foundation of ProjectRAG.

The objective is to build a professional local-first AI platform that combines:

- RAG
- GraphRAG
- Multi-agent orchestration
- Advanced memory management
- GraphDB reasoning
- PostgreSQL + pgvector vector retrieval
- Ollama local LLM execution
- FastAPI API layer
- LangGraph workflow orchestration
- GitHub-safe development
- VS Code + Codex assisted coding

This plan removes n8n completely.

The replacement is:

```text
FastAPI + LangGraph + Python agents
```

---

## 2. Original Idea

The original idea was to create a matrix of LLMs that can manage:

- RAG processes
- memory
- model allocation
- reasoning
- validation
- execution
- optimization

This idea is valid.

The correct architecture is not one big LLM doing everything.

The correct architecture is:

```text
Controller Agent
      ↓
Specialized Agents
      ↓
Retrieval + Graph + Memory
      ↓
Reasoning
      ↓
Validation
      ↓
Safe execution later
```

---

## 3. Why Remove n8n

n8n is useful for visual automation, but ProjectRAG needs:

- Python-native orchestration
- version-controlled workflows
- testable logic
- stateful agent workflows
- GraphRAG integration
- future DevOps execution controls
- better security
- better debugging
- GitHub-first engineering

Therefore n8n is removed.

Old architecture:

```text
User -> n8n -> API/tools/databases
```

New architecture:

```text
User -> FastAPI -> LangGraph -> Agents -> PostgreSQL + GraphDB + Ollama
```

---

## 4. Final Base Architecture

```text
Ubuntu Laptop
│
├── VS Code + Codex
├── GitHub repository
├── Python virtual environment
├── FastAPI
├── LangGraph
├── PostgreSQL + pgvector
├── GraphDB
├── Ollama
└── Docker Compose
```

Main runtime flow:

```text
User Question
      ↓
FastAPI
      ↓
LangGraph Workflow
      ↓
Router Agent
      ↓
Memory Agent
      ↓
Vector Retriever
      ↓
Graph Retriever
      ↓
Context Merger
      ↓
Reasoning Agent
      ↓
Validation Agent
      ↓
Final Answer
```

---

## 5. Component Responsibilities

### FastAPI

Purpose:

```text
Expose ProjectRAG as an API.
```

Responsibilities:

- receive user requests
- expose health endpoint
- expose query endpoint
- expose ingestion endpoint
- expose document endpoints
- expose graph endpoints
- expose DevOps planning endpoints later

---

### LangGraph

Purpose:

```text
Replace n8n workflow orchestration.
```

Responsibilities:

- manage workflow state
- coordinate agents
- support branching
- support retries
- support validation
- preserve execution flow as code

---

### PostgreSQL

Purpose:

```text
Operational database.
```

Stores:

- documents
- chunks
- metadata
- memory
- workflow runs
- agent runs
- validation results
- future action plans

---

### pgvector

Purpose:

```text
Semantic vector search.
```

Stores:

- embeddings for document chunks
- similarity search index

Answers:

```text
Which document chunks are semantically similar to the question?
```

---

### GraphDB

Purpose:

```text
Semantic reasoning database.
```

Stores:

- entities
- relationships
- dependencies
- topology
- ontology
- impact graph
- semantic facts

Answers:

```text
What depends on what?
What is connected to what?
What will be affected if something fails?
```

---

### Ollama

Purpose:

```text
Local LLM and embedding runtime.
```

Recommended models:

```text
llama3.1:8b
qwen2.5:7b
phi3
nomic-embed-text
```

Use:

```text
nomic-embed-text for embeddings
llama3.1:8b for reasoning
phi3 for lightweight tasks
```

---

### GitHub

Purpose:

```text
Safe version control.
```

Rules:

- never commit `.env`
- never commit credentials
- never commit private documents
- use branches
- review diffs
- use pull requests later

---

### VS Code + Codex

Purpose:

```text
Development and coding assistant.
```

Use Codex for:

- code generation
- tests
- explanations
- refactoring
- documentation
- security review

Rule:

```text
Codex helps. You approve.
```

---

## 6. User Laptop Target

Your system:

```text
OS: Ubuntu Linux 24.x
RAM: 32 GB
Storage: 1 TB HDD
GPU: 4 GB
```

Recommended resource strategy:

```text
Run one local LLM at a time.
Use Docker for databases.
Avoid Kubernetes initially.
Avoid cloud until local MVP works.
Use PostgreSQL + GraphDB locally.
Use GitHub private repository.
```

---

## 7. Development Principles

1. Build local first.
2. Keep architecture modular.
3. Replace n8n with LangGraph.
4. Store facts in databases, not prompts.
5. Use small models for simple tasks.
6. Use stronger models only for reasoning.
7. Validate all answers.
8. Treat GraphDB as a reasoning layer.
9. Treat PostgreSQL as operational truth.
10. Keep GitHub clean and safe.

---

## 8. First Implementation Goal

The first MVP should do this:

```text
1. Ingest a document.
2. Chunk it.
3. Create embeddings.
4. Store chunks in PostgreSQL/pgvector.
5. Extract relationships.
6. Store relationships in GraphDB.
7. Ask a question.
8. Retrieve vector context.
9. Retrieve graph context.
10. Generate answer.
11. Validate answer.
```

Expected result:

```text
A working no-n8n local GraphRAG prototype.
```

---

## 9. Base Folder Structure

```text
/home/RAG/project-rag/
├── app/
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
│   └── private/
├── docs/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 10. Part 1 Final Outcome

After Part 1, you understand:

- what ProjectRAG is
- why n8n is removed
- what replaces n8n
- what each component does
- why GraphDB is important
- why PostgreSQL remains important
- how the LLM matrix works
- what the first MVP must do

This is the foundation for all later parts.
