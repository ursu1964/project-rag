# ProjectRAG Master Plan - Part 6
# Complete Implementation Blueprint

**Version:** 1.0  
**Target OS:** Ubuntu Linux 24.x  
**Project root:** `/home/RAG/project-rag`  
**Generated:** 2026-06-16  

---

## Purpose of This Volume

Parts 1–5 defined the architecture.

This volume defines how to build it.

It covers:

- exact repository structure;
- every core Python file;
- every main function;
- database initialization scripts;
- GraphDB client design;
- Ollama client design;
- FastAPI endpoints;
- LangGraph workflow nodes;
- agent skeletons;
- testing skeletons;
- Docker files;
- GitHub-safe workflow;
- execution order.

This is the transition from architecture to implementation.

---

# 1. Final Repository Structure

Create this layout under:

```bash
/home/RAG/project-rag
```

Recommended structure:

```text
project-rag/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_query.py
│   │   ├── routes_documents.py
│   │   ├── routes_graph.py
│   │   └── routes_health.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── memory_agent.py
│   │   ├── vector_retriever.py
│   │   ├── graph_retriever.py
│   │   ├── context_merger.py
│   │   ├── reasoner.py
│   │   ├── validator.py
│   │   └── resource_allocator.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── schemas.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── graphdb_client.py
│   │   ├── ontology.py
│   │   ├── sparql_templates.py
│   │   └── triple_builder.py
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── postgres.py
│   │   ├── memory_store.py
│   │   └── workflow_store.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chunking.py
│   │   ├── document_registry.py
│   │   ├── embeddings.py
│   │   ├── ingestion.py
│   │   ├── vector_store.py
│   │   └── retrieval.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   ├── file_tools.py
│   │   └── safety.py
│   └── workflows/
│       ├── __init__.py
│       └── rag_workflow.py
├── data/
│   ├── raw/
│   ├── processed/
│   ├── private/
│   └── exports/
├── docs/
├── scripts/
│   ├── init_postgres.sql
│   ├── init_db.py
│   ├── ingest_documents.py
│   ├── test_query.py
│   └── export_graph.py
├── tests/
│   ├── test_health.py
│   ├── test_chunking.py
│   ├── test_router.py
│   └── test_workflow.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

Effect:

```text
The repository becomes predictable, testable, and maintainable.
```

---

# 2. Ubuntu Project Bootstrap Commands

Run:

```bash
sudo apt update
sudo apt upgrade -y

sudo apt install -y \
  git curl wget unzip build-essential \
  python3 python3-pip python3-venv python3-dev \
  docker.io docker-compose-v2 \
  postgresql-client jq tree htop

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Then log out and log back in.

Create folders:

```bash
sudo mkdir -p /home/RAG
sudo chown -R $USER:$USER /home/RAG

cd /home/RAG
git clone git@github.com:YOUR_USER/project-rag.git
cd project-rag
```

Create Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip setuptools wheel
```

---

# 3. requirements.txt

Create:

```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
sqlalchemy
psycopg2-binary
pgvector
requests
rdflib
langgraph
langchain
pytest
httpx
rich
python-multipart
```

Install:

```bash
pip install -r requirements.txt
```

Effect:

```text
All core Python dependencies are installed.
```

---

# 4. .gitignore

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
*.dump
data/raw/
data/processed/
data/private/
data/exports/
exports/
.vscode/settings.json
.DS_Store
```

Purpose:

```text
Protect secrets, local data, generated files, and private documents.
```

---

# 5. .env.example

Create:

```env
APP_ENV=local
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=projectrag
POSTGRES_USER=projectrag
POSTGRES_PASSWORD=projectrag_password

GRAPHDB_URL=http://localhost:7200
GRAPHDB_REPOSITORY=projectrag

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EMBEDDING_MODEL=nomic-embed-text

CHUNK_SIZE=1000
CHUNK_OVERLAP=150
TOP_K=5
```

Create private config:

```bash
cp .env.example .env
```

Effect:

```text
Runtime configuration is externalized and GitHub-safe.
```

---

# 6. docker-compose.yml

Create:

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
docker ps
```

Effect:

```text
PostgreSQL and GraphDB are running locally.
```

---

# 7. scripts/init_postgres.sql

Create:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    source_path TEXT,
    file_hash TEXT UNIQUE NOT NULL,
    mime_type TEXT,
    source_type TEXT DEFAULT 'file',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    token_count INT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memory_items (
    id UUID PRIMARY KEY,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT now(),
    last_accessed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id UUID PRIMARY KEY,
    workflow_name TEXT NOT NULL,
    question TEXT,
    route TEXT,
    status TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT now(),
    ended_at TIMESTAMP,
    duration_ms INT,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY,
    workflow_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    latency_ms INT,
    input_summary TEXT,
    output_summary TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS validation_results (
    id UUID PRIMARY KEY,
    workflow_id UUID REFERENCES workflow_runs(id) ON DELETE CASCADE,
    grounded BOOLEAN,
    confidence_score NUMERIC,
    warnings JSONB DEFAULT '[]'::jsonb,
    requires_human_approval BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_created ON chunks(created_at);
CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_items(memory_type);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX IF NOT EXISTS idx_agent_runs_workflow ON agent_runs(workflow_id);
```

Run:

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

Effect:

```text
Operational database schema is initialized.
```

---

# 8. app/core/config.py

Create:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "projectrag"
    postgres_user: str = "projectrag"
    postgres_password: str = "projectrag_password"

    graphdb_url: str = "http://localhost:7200"
    graphdb_repository: str = "projectrag"

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    embedding_model: str = "nomic-embed-text"

    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
```

Effect:

```text
Configuration is centralized and type-safe.
```

---

# 9. app/memory/postgres.py

Create:

```python
import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings


def get_connection():
    return psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        cursor_factory=RealDictCursor,
    )


def fetch_all(query: str, params: tuple = ()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()


def execute(query: str, params: tuple = ()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
```

Effect:

```text
All PostgreSQL operations use one connection utility.
```

---

# 10. app/tools/ollama_client.py

Create:

```python
import requests
from app.core.config import settings


def create_embedding(text: str) -> list[float]:
    response = requests.post(
        f"{settings.ollama_url}/api/embeddings",
        json={
            "model": settings.embedding_model,
            "prompt": text,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def generate(prompt: str) -> str:
    response = requests.post(
        f"{settings.ollama_url}/api/generate",
        json={
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json().get("response", "")
```

Effect:

```text
The application can call local embeddings and local LLM generation.
```

---

# 11. app/rag/chunking.py

Create:

```python
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks
```

Effect:

```text
Documents can be split into overlapping searchable units.
```

---

# 12. app/rag/document_registry.py

Create:

```python
import hashlib
import uuid
from pathlib import Path
from app.memory.postgres import fetch_all, execute


def calculate_file_hash(file_path: Path) -> str:
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def document_exists(file_hash: str) -> bool:
    rows = fetch_all(
        "SELECT id FROM documents WHERE file_hash = %s LIMIT 1",
        (file_hash,),
    )
    return len(rows) > 0


def register_document(
    filename: str,
    source_path: str,
    file_hash: str,
    metadata: dict | None = None,
) -> str:
    document_id = str(uuid.uuid4())

    execute(
        '''
        INSERT INTO documents (id, filename, source_path, file_hash, metadata)
        VALUES (%s, %s, %s, %s, %s)
        ''',
        (document_id, filename, source_path, file_hash, metadata or {}),
    )

    return document_id
```

Effect:

```text
Duplicate ingestion is prevented.
```

---

# 13. app/rag/vector_store.py

Create:

```python
import uuid
from app.memory.postgres import execute, fetch_all


def insert_chunk(
    document_id: str,
    chunk_index: int,
    chunk_text: str,
    embedding: list[float],
    metadata: dict | None = None,
):
    chunk_id = str(uuid.uuid4())

    execute(
        '''
        INSERT INTO chunks (
            id, document_id, chunk_index, chunk_text, embedding, token_count, metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            chunk_id,
            document_id,
            chunk_index,
            chunk_text,
            embedding,
            len(chunk_text.split()),
            metadata or {},
        ),
    )

    return chunk_id


def similarity_search(embedding: list[float], top_k: int = 5):
    query = '''
    SELECT
        c.id,
        c.chunk_text,
        c.metadata,
        d.filename,
        c.embedding <-> %s::vector AS distance
    FROM chunks c
    JOIN documents d ON d.id = c.document_id
    ORDER BY c.embedding <-> %s::vector
    LIMIT %s
    '''

    return fetch_all(query, (embedding, embedding, top_k))
```

Effect:

```text
Chunks can be inserted and searched semantically.
```

---

# 14. app/rag/ingestion.py

Create:

```python
from pathlib import Path
from app.core.config import settings
from app.rag.chunking import chunk_text
from app.rag.document_registry import (
    calculate_file_hash,
    document_exists,
    register_document,
)
from app.rag.vector_store import insert_chunk
from app.tools.ollama_client import create_embedding


def ingest_file(file_path: Path) -> dict:
    file_hash = calculate_file_hash(file_path)

    if document_exists(file_hash):
        return {
            "status": "skipped",
            "reason": "duplicate",
            "filename": file_path.name,
        }

    text = file_path.read_text(encoding="utf-8", errors="ignore")

    document_id = register_document(
        filename=file_path.name,
        source_path=str(file_path),
        file_hash=file_hash,
        metadata={"source": "local_file"},
    )

    chunks = chunk_text(
        text,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )

    inserted = 0

    for index, chunk in enumerate(chunks):
        embedding = create_embedding(chunk)
        insert_chunk(
            document_id=document_id,
            chunk_index=index,
            chunk_text=chunk,
            embedding=embedding,
            metadata={"file_hash": file_hash},
        )
        inserted += 1

    return {
        "status": "ingested",
        "filename": file_path.name,
        "document_id": document_id,
        "chunks": inserted,
    }


def ingest_directory(directory: Path) -> list[dict]:
    results = []

    for file_path in directory.glob("*.txt"):
        results.append(ingest_file(file_path))

    return results
```

Effect:

```text
Text files can be ingested into PostgreSQL and pgvector.
```

---

# 15. app/graph/graphdb_client.py

Create:

```python
import requests
from app.core.config import settings


def sparql_query(query: str) -> dict:
    url = f"{settings.graphdb_url}/repositories/{settings.graphdb_repository}"

    response = requests.get(
        url,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=60,
    )

    response.raise_for_status()
    return response.json()


def insert_turtle(turtle_data: str):
    url = f"{settings.graphdb_url}/repositories/{settings.graphdb_repository}/statements"

    response = requests.post(
        url,
        data=turtle_data.encode("utf-8"),
        headers={"Content-Type": "text/turtle"},
        timeout=60,
    )

    response.raise_for_status()
    return {"status": "ok"}
```

Effect:

```text
Python can query and write to GraphDB.
```

---

# 16. app/graph/sparql_templates.py

Create:

```python
PREFIX = "PREFIX project: <http://projectrag.local/>"


def dependency_query(entity: str) -> str:
    return f'''
{PREFIX}

SELECT ?target ?relation
WHERE {{
  project:{entity} ?relation ?target .
}}
LIMIT 50
'''


def reverse_dependency_query(entity: str) -> str:
    return f'''
{PREFIX}

SELECT ?source ?relation
WHERE {{
  ?source ?relation project:{entity} .
}}
LIMIT 50
'''
```

Effect:

```text
Common graph queries are reusable.
```

---

# 17. app/graph/triple_builder.py

Create:

```python
def sanitize_entity(value: str) -> str:
    return (
        value.strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace(".", "_")
        .replace("/", "_")
    )


def build_triple(subject: str, predicate: str, obj: str) -> str:
    s = sanitize_entity(subject)
    p = sanitize_entity(predicate)
    o = sanitize_entity(obj)

    return f"project:{s} project:{p} project:{o} ."


def build_turtle(triples: list[tuple[str, str, str]]) -> str:
    lines = ["@prefix project: <http://projectrag.local/> .", ""]

    for subject, predicate, obj in triples:
        lines.append(build_triple(subject, predicate, obj))

    return "\n".join(lines)
```

Effect:

```text
Extracted relationships can be persisted as RDF triples.
```

---

# 18. app/agents/router.py

Create:

```python
def run(state: dict) -> dict:
    question = state["question"].lower()

    graph_terms = ["depend", "connected", "topology", "relationship", "impact", "break"]
    vector_terms = ["document", "explain", "summarize", "text", "according to"]

    if any(term in question for term in graph_terms):
        route = "graph"
    elif any(term in question for term in vector_terms):
        route = "vector"
    else:
        route = "hybrid"

    state["route"] = route
    return state
```

Effect:

```text
The system chooses the retrieval strategy.
```

---

# 19. app/agents/vector_retriever.py

Create:

```python
from app.core.config import settings
from app.tools.ollama_client import create_embedding
from app.rag.vector_store import similarity_search


def run(state: dict) -> dict:
    question = state["question"]
    embedding = create_embedding(question)

    results = similarity_search(
        embedding=embedding,
        top_k=settings.top_k,
    )

    state["vector_context"] = [dict(row) for row in results]
    return state
```

Effect:

```text
Relevant text chunks are retrieved from pgvector.
```

---

# 20. app/agents/graph_retriever.py

Create:

```python
import re
from app.graph.graphdb_client import sparql_query
from app.graph.sparql_templates import dependency_query


def extract_candidate_entity(question: str) -> str | None:
    matches = re.findall(r"\b[A-Z][A-Za-z0-9_\-]+\b", question)
    return matches[0] if matches else None


def run(state: dict) -> dict:
    question = state["question"]
    entity = extract_candidate_entity(question)

    if not entity:
        state["graph_context"] = []
        return state

    query = dependency_query(entity)
    result = sparql_query(query)

    state["graph_context"] = result.get("results", {}).get("bindings", [])
    return state
```

Effect:

```text
GraphDB relationships are retrieved for entity-based questions.
```

---

# 21. app/agents/memory_agent.py

Create:

```python
from app.memory.postgres import fetch_all


def run(state: dict) -> dict:
    question = state["question"]

    rows = fetch_all(
        '''
        SELECT id, memory_type, content, metadata
        FROM memory_items
        WHERE content ILIKE %s
        ORDER BY created_at DESC
        LIMIT 5
        ''',
        (f"%{question[:40]}%",),
    )

    state["memory_context"] = [dict(row) for row in rows]
    return state
```

Effect:

```text
Relevant persisted memory can be injected into the workflow.
```

---

# 22. app/agents/context_merger.py

Create:

```python
def run(state: dict) -> dict:
    merged = {
        "memory": state.get("memory_context", []),
        "vector": state.get("vector_context", []),
        "graph": state.get("graph_context", []),
    }

    state["merged_context"] = merged
    return state
```

Effect:

```text
All evidence is normalized before reasoning.
```

---

# 23. app/agents/reasoner.py

Create:

```python
from app.tools.ollama_client import generate


def run(state: dict) -> dict:
    question = state["question"]
    context = state.get("merged_context", {})

    prompt = f'''
You are ProjectRAG, a local GraphRAG assistant.

Answer the question using only the provided context.

Question:
{question}

Context:
{context}

Answer clearly and include limitations if context is incomplete.
'''

    state["answer"] = generate(prompt)
    return state
```

Effect:

```text
The final answer is generated from retrieved evidence.
```

---

# 24. app/agents/validator.py

Create:

```python
def run(state: dict) -> dict:
    answer = state.get("answer", "")
    vector_context = state.get("vector_context", [])
    graph_context = state.get("graph_context", [])

    grounded = bool(vector_context or graph_context) and len(answer.strip()) > 0

    state["validation"] = {
        "grounded": grounded,
        "confidence": 0.75 if grounded else 0.25,
        "warnings": [] if grounded else ["No supporting context found"],
        "requires_human_approval": False,
    }

    return state
```

Effect:

```text
The system checks whether the answer has supporting evidence.
```

---

# 25. app/workflows/rag_workflow.py

Create:

```python
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END

from app.agents import (
    router,
    memory_agent,
    vector_retriever,
    graph_retriever,
    context_merger,
    reasoner,
    validator,
)


class RAGState(TypedDict, total=False):
    question: str
    route: str
    memory_context: list[dict[str, Any]]
    vector_context: list[dict[str, Any]]
    graph_context: list[dict[str, Any]]
    merged_context: dict[str, Any]
    answer: str
    validation: dict[str, Any]


def build_workflow():
    workflow = StateGraph(RAGState)

    workflow.add_node("router", router.run)
    workflow.add_node("memory", memory_agent.run)
    workflow.add_node("vector", vector_retriever.run)
    workflow.add_node("graph", graph_retriever.run)
    workflow.add_node("merge", context_merger.run)
    workflow.add_node("reason", reasoner.run)
    workflow.add_node("validate", validator.run)

    workflow.set_entry_point("router")

    workflow.add_edge("router", "memory")
    workflow.add_edge("memory", "vector")
    workflow.add_edge("vector", "graph")
    workflow.add_edge("graph", "merge")
    workflow.add_edge("merge", "reason")
    workflow.add_edge("reason", "validate")
    workflow.add_edge("validate", END)

    return workflow.compile()
```

Effect:

```text
This is the direct replacement for the old n8n workflow.
```

---

# 26. app/api/routes_health.py

Create:

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "ProjectRAG"}
```

---

# 27. app/api/routes_query.py

Create:

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.workflows.rag_workflow import build_workflow

router = APIRouter()
workflow = build_workflow()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
def query(request: QueryRequest):
    state = {
        "question": request.question,
        "route": "",
        "memory_context": [],
        "vector_context": [],
        "graph_context": [],
        "merged_context": {},
        "answer": "",
        "validation": {},
    }

    return workflow.invoke(state)
```

---

# 28. app/api/routes_documents.py

Create:

```python
from pathlib import Path
from fastapi import APIRouter
from app.memory.postgres import fetch_all
from app.rag.ingestion import ingest_directory

router = APIRouter()


@router.get("/documents")
def list_documents():
    rows = fetch_all(
        '''
        SELECT id, filename, source_path, file_hash, created_at
        FROM documents
        ORDER BY created_at DESC
        '''
    )
    return {"documents": [dict(row) for row in rows]}


@router.post("/ingest")
def ingest():
    results = ingest_directory(Path("data/raw"))
    return {"results": results}
```

---

# 29. app/api/routes_graph.py

Create:

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.graph.graphdb_client import sparql_query

router = APIRouter()


class GraphQueryRequest(BaseModel):
    query: str


@router.post("/graph/query")
def query_graph(request: GraphQueryRequest):
    return sparql_query(request.query)
```

---

# 30. app/main.py

Create:

```python
from fastapi import FastAPI
from app.api.routes_health import router as health_router
from app.api.routes_query import router as query_router
from app.api.routes_documents import router as documents_router
from app.api.routes_graph import router as graph_router

app = FastAPI(title="ProjectRAG", version="1.0.0")

app.include_router(health_router)
app.include_router(query_router)
app.include_router(documents_router)
app.include_router(graph_router)
```

Run:

```bash
uvicorn app.main:app --reload
```

Effect:

```text
The API is modular and ready for extension.
```

---

# 31. scripts/ingest_documents.py

Create:

```python
from pathlib import Path
from app.rag.ingestion import ingest_directory


if __name__ == "__main__":
    results = ingest_directory(Path("data/raw"))

    for result in results:
        print(result)
```

Run:

```bash
python -m scripts.ingest_documents
```

---

# 32. scripts/test_query.py

Create:

```python
from app.workflows.rag_workflow import build_workflow


if __name__ == "__main__":
    workflow = build_workflow()

    result = workflow.invoke({
        "question": "What depends on VM1?",
        "route": "",
        "memory_context": [],
        "vector_context": [],
        "graph_context": [],
        "merged_context": {},
        "answer": "",
        "validation": {},
    })

    print(result)
```

---

# 33. tests/test_chunking.py

Create:

```python
from app.rag.chunking import chunk_text


def test_chunk_text_returns_chunks():
    text = "A" * 3000
    chunks = chunk_text(text, chunk_size=1000, overlap=100)

    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)
```

---

# 34. tests/test_router.py

Create:

```python
from app.agents.router import run


def test_router_graph_route():
    state = {"question": "What depends on VM1?"}
    result = run(state)

    assert result["route"] == "graph"


def test_router_vector_route():
    state = {"question": "Summarize the document"}
    result = run(state)

    assert result["route"] == "vector"
```

---

# 35. tests/test_health.py

Create:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

---

# 36. First End-to-End Test

Start infrastructure:

```bash
docker compose up -d
```

Initialize database:

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

Start Ollama:

```bash
ollama serve
```

In another terminal:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Create sample file:

```bash
cat > data/raw/example.txt << 'EOF'
VM1 is connected to SubnetA.
VM1 depends on Database01.
Database01 is protected by Firewall01.
EOF
```

Ingest:

```bash
source .venv/bin/activate
python -m scripts.ingest_documents
```

Run API:

```bash
uvicorn app.main:app --reload
```

Query:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What does VM1 depend on?"}'
```

Expected effect:

```text
The system retrieves context and generates an answer.
```

---

# 37. GitHub Commit Sequence

Run:

```bash
git status
git diff
```

Check secrets:

```bash
grep -R "api_key\|secret\|token\|password" . --exclude-dir=.venv --exclude=.env
```

Add files:

```bash
git add app scripts tests docs requirements.txt docker-compose.yml .gitignore .env.example
```

Commit:

```bash
git commit -m "Add no-n8n ProjectRAG implementation blueprint"
```

Push:

```bash
git push origin feature/base-implementation
```

Effect:

```text
Implementation foundation is safely stored in GitHub.
```

---

# 38. Implementation Order Checklist

Use this exact order:

```text
1. Ubuntu packages
2. Docker
3. GitHub clone
4. Python virtual environment
5. requirements.txt
6. .gitignore
7. .env.example
8. docker-compose.yml
9. PostgreSQL start
10. GraphDB start
11. PostgreSQL schema
12. Ollama models
13. config.py
14. postgres.py
15. ollama_client.py
16. chunking.py
17. document_registry.py
18. vector_store.py
19. ingestion.py
20. graphdb_client.py
21. sparql_templates.py
22. triple_builder.py
23. router agent
24. vector retriever agent
25. graph retriever agent
26. memory agent
27. context merger
28. reasoner
29. validator
30. LangGraph workflow
31. FastAPI routes
32. scripts
33. tests
34. first ingestion
35. first query
36. GitHub commit
```

---

# 39. Known Limitations of This First Implementation

This first implementation is intentionally simple.

Limitations:

```text
Entity extraction is basic.
GraphDB ingestion is not fully automated yet.
Router uses rules, not model-based classification.
Validator uses simple checks.
Memory search is basic ILIKE matching.
No reranking yet.
No authentication yet.
No production monitoring yet.
```

These are acceptable for the MVP.

---

# 40. Next Engineering Improvements

After MVP works, add:

```text
1. Automated entity extraction
2. Automated relationship extraction
3. GraphDB triple ingestion from documents
4. Better vector search thresholds
5. Reranking
6. Better validation using LLM judge
7. Workflow logging to PostgreSQL
8. API authentication
9. UI dashboard
10. DevOps inventory importer
```

---

# 41. Final Result of Part 6

After implementing this volume, ProjectRAG will have:

```text
Ubuntu-ready local runtime
Dockerized PostgreSQL + GraphDB
Ollama local model support
FastAPI API
LangGraph workflow
Agent matrix skeleton
RAG ingestion
Vector search
GraphDB client
Memory foundation
Validation foundation
Tests
Safe GitHub workflow
```

This is the first real buildable version of ProjectRAG without n8n.
