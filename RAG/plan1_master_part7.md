# ProjectRAG Master Plan - Part 7
# Advanced GraphRAG Extraction, Retrieval Scoring, and Validation Engineering

**Version:** 1.0  
**Target OS:** Ubuntu Linux 24.x  
**Project root:** `/home/RAG/project-rag`  
**Generated:** 2026-06-16  

---

## Purpose of This Volume

Part 6 created the first buildable implementation blueprint.

Part 7 improves the MVP into a stronger GraphRAG platform by adding:

- automated entity extraction;
- automated relationship extraction;
- GraphDB triple ingestion from documents;
- ontology-aware graph persistence;
- hybrid retrieval scoring;
- context compression;
- reranking;
- better validation;
- workflow observability;
- workflow persistence;
- safe expansion toward DevOps reasoning.

The objective is to move from:

```text
Basic RAG prototype
```

to:

```text
Operational GraphRAG engine
```

---

# 1. GraphRAG Extraction Philosophy

A normal RAG system stores text and retrieves text.

GraphRAG does more:

```text
Text -> Entities -> Relationships -> Graph -> Reasoning
```

This means each document is processed in two parallel ways:

```text
Document
 ├── Vector path
 │   ├── chunk
 │   ├── embed
 │   └── store in pgvector
 │
 └── Graph path
     ├── extract entities
     ├── extract relationships
     ├── map to ontology
     └── store triples in GraphDB
```

Effect:

```text
The system can answer both semantic questions and dependency questions.
```

---

# 2. Entity Extraction Design

## 2.1 Purpose

Entity extraction identifies important objects in text.

For ProjectRAG, entities include:

```text
VMs
subnets
VNets
firewalls
databases
applications
services
APIs
queues
storage volumes
documents
logs
errors
cloud resources
```

## 2.2 Example

Input:

```text
VM1 is connected to SubnetA and depends on Database01.
Database01 is protected by Firewall01.
```

Output:

```json
{
  "entities": [
    {"name": "VM1", "type": "VM"},
    {"name": "SubnetA", "type": "Subnet"},
    {"name": "Database01", "type": "Database"},
    {"name": "Firewall01", "type": "Firewall"}
  ]
}
```

## 2.3 First Implementation Strategy

Use deterministic pattern extraction first.

Why:

```text
It is cheaper.
It is predictable.
It does not require LLM calls.
It is easy to test.
```

Later, add LLM-assisted extraction.

---

# 3. Entity Extraction Module

Create:

```text
app/graph/entity_extractor.py
```

Code skeleton:

```python
import re


ENTITY_PATTERNS = {
    "VM": r"\bVM[A-Za-z0-9_\-]*\b",
    "Database": r"\b(Database|DB)[A-Za-z0-9_\-]*\b",
    "Subnet": r"\bSubnet[A-Za-z0-9_\-]*\b",
    "Firewall": r"\bFirewall[A-Za-z0-9_\-]*\b",
    "VNet": r"\bVNet[A-Za-z0-9_\-]*\b",
    "Service": r"\bService[A-Za-z0-9_\-]*\b",
    "API": r"\bAPI[A-Za-z0-9_\-]*\b",
}


def extract_entities(text: str) -> list[dict]:
    entities = []

    for entity_type, pattern in ENTITY_PATTERNS.items():
        for match in re.findall(pattern, text):
            if isinstance(match, tuple):
                continue

            entities.append({
                "name": match,
                "type": entity_type,
            })

    unique = {}
    for entity in entities:
        key = (entity["name"], entity["type"])
        unique[key] = entity

    return list(unique.values())
```

Effect:

```text
The system can identify infrastructure and application objects from text.
```

---

# 4. Relationship Extraction Design

## 4.1 Purpose

Relationship extraction identifies links between entities.

Relationships are more important than entities alone.

Example:

```text
VM1 depends on Database01.
```

Entity extraction gives:

```text
VM1
Database01
```

Relationship extraction gives:

```text
VM1 dependsOn Database01
```

## 4.2 Supported Relationship Types

Initial relation vocabulary:

```text
dependsOn
connectedTo
hostedOn
belongsTo
protectedBy
uses
calls
readsFrom
writesTo
contains
managedBy
runsOn
exposes
blockedBy
```

## 4.3 Relation Pattern Examples

```text
X depends on Y        -> X dependsOn Y
X is connected to Y   -> X connectedTo Y
X uses Y              -> X uses Y
X is protected by Y   -> X protectedBy Y
X runs on Y           -> X runsOn Y
X belongs to Y        -> X belongsTo Y
```

---

# 5. Relationship Extraction Module

Create:

```text
app/graph/relationship_extractor.py
```

Code skeleton:

```python
import re


RELATION_PATTERNS = [
    (r"(\w+)\s+depends on\s+(\w+)", "dependsOn"),
    (r"(\w+)\s+is connected to\s+(\w+)", "connectedTo"),
    (r"(\w+)\s+uses\s+(\w+)", "uses"),
    (r"(\w+)\s+is protected by\s+(\w+)", "protectedBy"),
    (r"(\w+)\s+runs on\s+(\w+)", "runsOn"),
    (r"(\w+)\s+belongs to\s+(\w+)", "belongsTo"),
    (r"(\w+)\s+calls\s+(\w+)", "calls"),
    (r"(\w+)\s+reads from\s+(\w+)", "readsFrom"),
    (r"(\w+)\s+writes to\s+(\w+)", "writesTo"),
]


def extract_relationships(text: str) -> list[tuple[str, str, str]]:
    relationships = []

    for pattern, relation in RELATION_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        for source, target in matches:
            relationships.append((source, relation, target))

    return relationships
```

Effect:

```text
Text is transformed into graph-ready relationship triples.
```

---

# 6. Ontology Mapping

## 6.1 Purpose

Ontology mapping normalizes extracted entities and relationships.

Without ontology mapping:

```text
depends on
depends_on
dependsOn
dependency
```

may become different relationships.

With ontology mapping:

```text
all become project:dependsOn
```

## 6.2 Create Ontology Module

Create:

```text
app/graph/ontology.py
```

Code skeleton:

```python
ENTITY_TYPES = {
    "VM",
    "Database",
    "Subnet",
    "Firewall",
    "VNet",
    "Service",
    "API",
    "Application",
    "Queue",
    "Cache",
    "Storage",
}

RELATION_TYPES = {
    "dependsOn",
    "connectedTo",
    "hostedOn",
    "belongsTo",
    "protectedBy",
    "uses",
    "calls",
    "readsFrom",
    "writesTo",
    "contains",
    "managedBy",
    "runsOn",
    "exposes",
    "blockedBy",
}


RELATION_ALIASES = {
    "depends on": "dependsOn",
    "connected to": "connectedTo",
    "protected by": "protectedBy",
    "runs on": "runsOn",
    "belongs to": "belongsTo",
}


def normalize_relation(relation: str) -> str:
    relation = relation.strip()

    if relation in RELATION_TYPES:
        return relation

    lowered = relation.lower()

    if lowered in RELATION_ALIASES:
        return RELATION_ALIASES[lowered]

    return relation
```

Effect:

```text
GraphDB receives consistent predicates.
```

---

# 7. Graph Ingestion Pipeline

## 7.1 Flow

```text
Document chunk
 -> extract entities
 -> extract relationships
 -> normalize relationships
 -> build Turtle
 -> insert into GraphDB
```

## 7.2 Create Graph Ingestion Module

Create:

```text
app/graph/graph_ingestion.py
```

Code skeleton:

```python
from app.graph.entity_extractor import extract_entities
from app.graph.relationship_extractor import extract_relationships
from app.graph.triple_builder import build_turtle
from app.graph.graphdb_client import insert_turtle
from app.graph.ontology import normalize_relation


def ingest_text_to_graph(text: str) -> dict:
    entities = extract_entities(text)
    raw_relationships = extract_relationships(text)

    normalized = []

    for source, relation, target in raw_relationships:
        normalized.append((source, normalize_relation(relation), target))

    if normalized:
        turtle = build_turtle(normalized)
        insert_turtle(turtle)

    return {
        "entities": entities,
        "relationships": normalized,
        "relationship_count": len(normalized),
    }
```

Effect:

```text
Documents now populate both vector storage and GraphDB.
```

---

# 8. Update RAG Ingestion to Include GraphDB

Modify:

```text
app/rag/ingestion.py
```

Add:

```python
from app.graph.graph_ingestion import ingest_text_to_graph
```

Inside `ingest_file`, after text is loaded:

```python
graph_result = ingest_text_to_graph(text)
```

Return:

```python
"graph": graph_result
```

Expected result:

```text
Every ingested file creates:
- document record
- vector chunks
- graph triples
```

---

# 9. GraphDB Verification Query

After ingesting sample text:

```text
VM1 is connected to SubnetA.
VM1 depends on Database01.
Database01 is protected by Firewall01.
```

Run SPARQL:

```sparql
PREFIX project: <http://projectrag.local/>

SELECT ?relation ?target
WHERE {
  project:VM1 ?relation ?target .
}
```

Expected results:

```text
project:connectedTo project:SubnetA
project:dependsOn project:Database01
```

Effect:

```text
GraphDB knowledge extraction is verified.
```

---

# 10. Hybrid Retrieval Scoring

## 10.1 Purpose

Not all retrieved context is equally important.

The system should score evidence.

Evidence sources:

```text
vector chunks
graph relationships
memory items
metadata matches
```

## 10.2 Score Formula

Initial simple formula:

```text
final_score =
  vector_score * 0.45
+ graph_score  * 0.35
+ memory_score * 0.10
+ metadata_score * 0.10
```

For infrastructure topology questions:

```text
final_score =
  graph_score  * 0.55
+ vector_score * 0.25
+ memory_score * 0.10
+ metadata_score * 0.10
```

For document explanation questions:

```text
final_score =
  vector_score * 0.60
+ graph_score  * 0.20
+ memory_score * 0.10
+ metadata_score * 0.10
```

Effect:

```text
Retrieval becomes route-aware.
```

---

# 11. Retrieval Scorer Module

Create:

```text
app/rag/scoring.py
```

Code skeleton:

```python
def score_vector_result(distance: float) -> float:
    return max(0.0, 1.0 - float(distance))


def score_graph_result(result: dict) -> float:
    if not result:
        return 0.0

    return 0.85


def score_memory_result(result: dict) -> float:
    if not result:
        return 0.0

    return 0.50


def weighted_score(
    route: str,
    vector_score: float,
    graph_score: float,
    memory_score: float,
    metadata_score: float = 0.0,
) -> float:
    if route == "graph":
        weights = {
            "vector": 0.25,
            "graph": 0.55,
            "memory": 0.10,
            "metadata": 0.10,
        }
    elif route == "vector":
        weights = {
            "vector": 0.60,
            "graph": 0.20,
            "memory": 0.10,
            "metadata": 0.10,
        }
    else:
        weights = {
            "vector": 0.45,
            "graph": 0.35,
            "memory": 0.10,
            "metadata": 0.10,
        }

    return (
        vector_score * weights["vector"]
        + graph_score * weights["graph"]
        + memory_score * weights["memory"]
        + metadata_score * weights["metadata"]
    )
```

Effect:

```text
The context merger can rank evidence more intelligently.
```

---

# 12. Context Compression

## 12.1 Problem

The retriever may return too much text.

Too much context causes:

```text
slow answers
higher memory use
lower reasoning quality
more hallucination risk
```

## 12.2 Solution

Compress retrieved context before reasoning.

Compression strategy:

```text
Keep:
- document name
- chunk text
- graph facts
- confidence score

Remove:
- redundant text
- low-score chunks
- duplicate facts
```

---

# 13. Context Compressor Module

Create:

```text
app/agents/context_compressor.py
```

Code skeleton:

```python
MAX_CHARS_PER_CHUNK = 800


def compress_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> str:
    text = text.strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "..."


def run(state: dict) -> dict:
    vector_context = state.get("vector_context", [])

    compressed_vector = []

    for item in vector_context:
        compressed_vector.append({
            "filename": item.get("filename"),
            "distance": item.get("distance"),
            "chunk_text": compress_text(item.get("chunk_text", "")),
        })

    state["compressed_context"] = {
        "vector": compressed_vector,
        "graph": state.get("graph_context", []),
        "memory": state.get("memory_context", []),
    }

    return state
```

Effect:

```text
Reasoning receives less noise and better structured evidence.
```

---

# 14. Improved Reasoner Prompt

Modify:

```text
app/agents/reasoner.py
```

Use structured prompt:

```python
prompt = f'''
You are ProjectRAG, a local GraphRAG assistant.

Rules:
1. Answer only from provided context.
2. If context is insufficient, say exactly what is missing.
3. Separate vector evidence from graph evidence.
4. For infrastructure questions, prioritize graph relationships.
5. Do not invent entities or dependencies.

Question:
{question}

Route:
{state.get("route")}

Context:
{context}

Return:
- Direct answer
- Evidence used
- Limitations
'''
```

Effect:

```text
The final answer becomes more transparent and safer.
```

---

# 15. Advanced Validator Design

## 15.1 Validator Responsibilities

The validator should check:

```text
answer_exists
context_exists
graph_context_used
vector_context_used
unsupported_claims
risk_level
confidence
requires_human_approval
```

## 15.2 Validation Output Schema

```json
{
  "grounded": true,
  "confidence": 0.82,
  "risk_level": "low",
  "warnings": [],
  "requires_human_approval": false
}
```

---

# 16. Improved Validator Module

Modify:

```text
app/agents/validator.py
```

Code skeleton:

```python
def run(state: dict) -> dict:
    answer = state.get("answer", "")
    route = state.get("route", "")
    vector_context = state.get("vector_context", [])
    graph_context = state.get("graph_context", [])

    warnings = []

    if not answer.strip():
        warnings.append("Answer is empty.")

    if not vector_context and not graph_context:
        warnings.append("No retrieved evidence found.")

    if route == "graph" and not graph_context:
        warnings.append("Graph route selected but no graph evidence found.")

    if route == "vector" and not vector_context:
        warnings.append("Vector route selected but no vector evidence found.")

    grounded = len(warnings) == 0

    confidence = 0.85 if grounded else 0.35

    risk_level = "low"
    if "delete" in state.get("question", "").lower():
        risk_level = "high"

    requires_approval = risk_level == "high"

    state["validation"] = {
        "grounded": grounded,
        "confidence": confidence,
        "risk_level": risk_level,
        "warnings": warnings,
        "requires_human_approval": requires_approval,
    }

    return state
```

Effect:

```text
The answer now includes operational confidence and safety information.
```

---

# 17. Workflow Logging

## 17.1 Purpose

Every query should be traceable.

Track:

```text
question
route
start time
end time
duration
agent status
validation result
```

This is essential for:

```text
debugging
performance tuning
RAG quality analysis
audit
future DevOps automation safety
```

---

# 18. Workflow Store Module

Create:

```text
app/memory/workflow_store.py
```

Code skeleton:

```python
import uuid
from app.memory.postgres import execute


def create_workflow_run(question: str, route: str = "") -> str:
    workflow_id = str(uuid.uuid4())

    execute(
        '''
        INSERT INTO workflow_runs (
            id, workflow_name, question, route, status
        )
        VALUES (%s, %s, %s, %s, %s)
        ''',
        (workflow_id, "rag_workflow", question, route, "running"),
    )

    return workflow_id


def complete_workflow_run(workflow_id: str, status: str = "completed"):
    execute(
        '''
        UPDATE workflow_runs
        SET status = %s, ended_at = now()
        WHERE id = %s
        ''',
        (status, workflow_id),
    )
```

Effect:

```text
Workflow executions become auditable.
```

---

# 19. Agent Run Logging

Create:

```text
app/memory/agent_store.py
```

Code skeleton:

```python
import uuid
from app.memory.postgres import execute


def log_agent_run(
    workflow_id: str,
    agent_name: str,
    status: str,
    latency_ms: int = 0,
    input_summary: str = "",
    output_summary: str = "",
):
    execute(
        '''
        INSERT INTO agent_runs (
            id, workflow_id, agent_name, status,
            latency_ms, input_summary, output_summary
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            str(uuid.uuid4()),
            workflow_id,
            agent_name,
            status,
            latency_ms,
            input_summary,
            output_summary,
        ),
    )
```

Effect:

```text
Each agent execution can be reviewed later.
```

---

# 20. Validation Result Persistence

Create:

```text
app/memory/validation_store.py
```

Code skeleton:

```python
import uuid
from app.memory.postgres import execute


def store_validation_result(workflow_id: str, validation: dict):
    execute(
        '''
        INSERT INTO validation_results (
            id, workflow_id, grounded, confidence_score,
            warnings, requires_human_approval
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ''',
        (
            str(uuid.uuid4()),
            workflow_id,
            validation.get("grounded"),
            validation.get("confidence"),
            validation.get("warnings", []),
            validation.get("requires_human_approval", False),
        ),
    )
```

Effect:

```text
Validation is no longer temporary; it becomes part of system history.
```

---

# 21. Update LangGraph Workflow with Compressor

Modify:

```text
app/workflows/rag_workflow.py
```

Add node:

```python
from app.agents import context_compressor
```

Add:

```python
workflow.add_node("compress", context_compressor.run)
```

Replace edges:

```python
workflow.add_edge("graph", "merge")
workflow.add_edge("merge", "compress")
workflow.add_edge("compress", "reason")
```

Effect:

```text
The reasoning agent receives cleaner context.
```

---

# 22. Graph-Aware Questions

The system should support:

```text
What depends on VM1?
What is connected to SubnetA?
What is protected by Firewall01?
What breaks if Database01 fails?
Which services use DB01?
Which applications call API-Gateway?
```

These are graph-first questions.

Expected route:

```text
graph
```

Expected evidence:

```text
GraphDB relationships
```

---

# 23. Vector-Aware Questions

The system should support:

```text
Summarize the architecture document.
What does the document say about memory?
Explain the ingestion process.
According to the logs, what happened?
```

Expected route:

```text
vector
```

Expected evidence:

```text
Document chunks
```

---

# 24. Hybrid Questions

The system should support:

```text
Explain what will happen if Firewall01 fails, using the documentation.
What does the plan say about VM dependencies?
Which document explains the database that VM1 depends on?
```

Expected route:

```text
hybrid
```

Expected evidence:

```text
Vector chunks + graph paths
```

---

# 25. Test Data for GraphRAG

Create:

```text
data/raw/topology_example.txt
```

Content:

```text
VM1 is connected to SubnetA.
VM1 depends on Database01.
Database01 is protected by Firewall01.
ServiceA calls API01.
API01 uses Database01.
ApplicationA runs on VM1.
SubnetA belongs to VNetDev.
```

Run:

```bash
python -m scripts.ingest_documents
```

Then query:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What depends on Database01?"}'
```

Expected:

```text
The system should retrieve graph relationships involving Database01.
```

---

# 26. GraphDB Manual Insert Test

Create:

```text
scripts/insert_sample_graph.py
```

Code:

```python
from app.graph.triple_builder import build_turtle
from app.graph.graphdb_client import insert_turtle


triples = [
    ("VM1", "connectedTo", "SubnetA"),
    ("VM1", "dependsOn", "Database01"),
    ("Database01", "protectedBy", "Firewall01"),
]

turtle = build_turtle(triples)
print(turtle)
insert_turtle(turtle)
print("Inserted sample graph.")
```

Run:

```bash
python -m scripts.insert_sample_graph
```

Effect:

```text
GraphDB can be tested independently from document ingestion.
```

---

# 27. Graph Query Test Script

Create:

```text
scripts/query_graph.py
```

Code:

```python
from app.graph.graphdb_client import sparql_query
from app.graph.sparql_templates import dependency_query


if __name__ == "__main__":
    result = sparql_query(dependency_query("VM1"))
    print(result)
```

Run:

```bash
python -m scripts.query_graph
```

Effect:

```text
GraphDB retrieval is validated independently.
```

---

# 28. Improved Route Logic

The router should classify:

```text
graph:
depend, connected, topology, impact, breaks, relationship

vector:
document, summarize, explain, according to, text, plan

hybrid:
default when both are possible
```

Later:

```text
Use LLM-based classification with JSON output.
```

---

# 29. Future LLM Router

Future router prompt:

```text
Classify the user question.

Return only JSON:
{
  "route": "vector|graph|hybrid|action",
  "confidence": 0.0-1.0,
  "reason": "short reason"
}
```

Effect:

```text
The router becomes smarter while keeping structured output.
```

---

# 30. Production GraphRAG Risks

Risks:

```text
Bad entity extraction
Wrong relationship extraction
Duplicate relationships
Overconnected graph
Low-quality ontology
Unsupported reasoning
Slow SPARQL queries
```

Mitigations:

```text
normalize ontology
deduplicate triples
validate relationship types
track provenance
limit graph traversal depth
test with known topology
```

---

# 31. Provenance Strategy

Every graph triple should eventually include provenance.

Example:

```text
VM1 dependsOn Database01
sourceDocument topology_example.txt
sourceChunk chunk-123
confidence 0.91
```

This requires RDF reification or named graphs.

Initial simple version:

```text
Store provenance in PostgreSQL.
```

Later advanced version:

```text
Use named graphs in GraphDB.
```

Effect:

```text
Every graph fact becomes auditable.
```

---

# 32. Graph Traversal Depth

Do not allow unlimited graph expansion.

Recommended limits:

```text
depth 1: direct relationships
depth 2: dependency chain
depth 3: impact analysis
depth >3: only with explicit request
```

Effect:

```text
Graph queries remain fast and explainable.
```

---

# 33. DevOps Safety Layer

For any future execution action:

```text
analyze
recommend
approve
execute
verify
rollback
```

Never go directly from:

```text
question -> execution
```

Required stages:

```text
read-only evidence
proposed action
risk classification
human approval
execution
audit log
```

Effect:

```text
The system remains safe for infrastructure automation.
```

---

# 34. Acceptance Criteria for Part 7

Part 7 is complete when:

```text
Entity extraction module exists.
Relationship extraction module exists.
Ontology normalization exists.
Graph ingestion module exists.
Document ingestion writes to GraphDB.
Context compression exists.
Improved validator exists.
Workflow logging exists.
Agent logging exists.
Validation persistence exists.
Sample graph insert works.
Sample graph query works.
Hybrid query returns vector and graph context.
```

---

# 35. Implementation Order

Use this order:

```text
1. entity_extractor.py
2. relationship_extractor.py
3. ontology.py update
4. graph_ingestion.py
5. update ingestion.py
6. insert_sample_graph.py
7. query_graph.py
8. scoring.py
9. context_compressor.py
10. update reasoner.py
11. update validator.py
12. workflow_store.py
13. agent_store.py
14. validation_store.py
15. update rag_workflow.py
16. run graph insert test
17. run document ingestion test
18. run hybrid query test
19. commit to GitHub
```

---

# 36. Git Commit

After implementation:

```bash
git checkout -b feature/advanced-graphrag-extraction

git status
git diff

git add app scripts tests docs
git commit -m "Add advanced GraphRAG extraction and validation design"
git push origin feature/advanced-graphrag-extraction
```

Effect:

```text
The advanced GraphRAG layer is safely versioned.
```

---

# 37. Final Result of Part 7

After implementing this volume, ProjectRAG will support:

```text
automatic entity extraction
automatic relationship extraction
GraphDB triple ingestion
hybrid vector + graph retrieval
context compression
improved validation
workflow persistence
agent execution logging
GraphRAG test scripts
safe path toward DevOps reasoning
```

This transforms the project from a RAG prototype into an early GraphRAG reasoning platform.
