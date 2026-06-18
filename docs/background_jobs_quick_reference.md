# Quick Reference: Background Jobs & Golden Evaluations

## Background Jobs - Quick Start

### Create a Job

```python
from app.services.background_jobs import create_job, JobType

# Simple job
job = create_job(
    job_type=JobType.INGEST_DOCUMENT.value,
    resource_id="doc-123"
)
print(f"Job created: {job['id']}")

# With metadata and idempotency
job = create_job(
    job_type=JobType.INGEST_DOCUMENT.value,
    resource_type="document",
    resource_id="doc-123",
    metadata={"filename": "arch.md", "size": 2048},
    max_attempts=5,
    idempotency_key="ingest#file_hash_abc123"
)
```

### Track Job Status

```python
from app.services.background_jobs import get_job, mark_running, mark_completed, mark_failed

# Get job details
job = get_job(job_id)
print(f"Status: {job['status']}, Attempts: {job['attempts']}")

# Mark as running
mark_running(job_id)

# Mark completed with result
mark_completed(job_id, {"chunks": 42, "duration_ms": 1234})

# Mark failed (auto-retries if attempts < max)
mark_failed(job_id, "Connection timeout")
```

### List and Filter Jobs

```python
from app.services.background_jobs import list_jobs, JobStatus

# All jobs
jobs = list_jobs()

# Queued jobs
queued = list_jobs(status=JobStatus.QUEUED.value)

# By type and resource
ingestion_jobs = list_jobs(
    job_type="ingest_document",
    resource_type="document"
)

# With pagination
page = list_jobs(limit=10, offset=20)
```

## Idempotency - Quick Start

### Generate Idempotent Keys

```python
from app.services.idempotency import get_or_create_idempotency_key

# Deterministic key for file ingestion
key = get_or_create_idempotency_key("ingestion", file_hash)

# Deterministic key for evaluation
key = get_or_create_idempotency_key("evaluation", "graph_dataset")

# Same inputs = same key
key1 = get_or_create_idempotency_key("ingestion", "abc123")
key2 = get_or_create_idempotency_key("ingestion", "abc123")
assert key1 == key2
```

### Cache Results

```python
from app.services.idempotency import record_idempotent_result, get_idempotent_result

# Check if already processed
cached = get_idempotent_result(idempotency_key)
if cached:
    return cached  # Return cached result

# Process and cache
result = expensive_operation()
record_idempotent_result(idempotency_key, result, ttl_seconds=3600)
```

## Golden Evaluations - Quick Start

### Load Questions

```python
from app.services.golden_evaluation import load_golden_questions

# Load specific category
graph_questions = load_golden_questions("graph")
print(f"Graph questions: {len(graph_questions)}")
# → Graph questions: 5

vector_questions = load_golden_questions("vector")
print(f"Vector questions: {len(vector_questions)}")
# → Vector questions: 5

hybrid_questions = load_golden_questions("hybrid")
print(f"Hybrid questions: {len(hybrid_questions)}")
# → Hybrid questions: 5

safety_questions = load_golden_questions("safety")
print(f"Safety questions: {len(safety_questions)}")
# → Safety questions: 8
```

### Run Evaluations

```python
from app.services.golden_evaluation import run_golden_evaluation, run_all_golden_evaluations

# Run single category
result = run_golden_evaluation("graph")
print(result)
# {
#   "status": "completed",
#   "category": "graph",
#   "timestamp": "2026-06-18T...",
#   "passed": 5,
#   "failed": 0,
#   "total": 5,
#   "pass_rate": 100.0,
#   "details": [...]
# }

# Run all categories
all_results = run_all_golden_evaluations()
print(all_results)
# {
#   "status": "completed",
#   "categories": {
#     "graph": {...},
#     "vector": {...},
#     "hybrid": {...},
#     "safety": {...}
#   },
#   "summary": {
#     "total_passed": 23,
#     "total_failed": 0,
#     "total_questions": 23,
#     "overall_pass_rate": 100.0
#   }
# }
```

### Integrate with Background Jobs

```python
from app.services.background_jobs import create_job, mark_running, mark_completed
from app.services.golden_evaluation import run_golden_evaluation

# Create evaluation job
job = create_job(
    job_type="evaluate_golden_set",
    resource_type="evaluation_dataset",
    resource_id="graph"
)

try:
    mark_running(job["id"])
    result = run_golden_evaluation("graph", job["id"])
    mark_completed(job["id"], result)
except Exception as e:
    mark_failed(job["id"], str(e))
```

## Common Patterns

### Idempotent Document Ingestion

```python
from app.rag.ingestion import ingest_file
from app.services.background_jobs import create_job, mark_running, mark_completed
from app.services.idempotency import get_or_create_idempotency_key

def safe_ingest_document(file_path: str):
    """Ingest document with idempotency and job tracking."""
    file_hash = calculate_file_hash(file_path)
    idempotency_key = get_or_create_idempotency_key("ingestion", file_hash)
    
    # Create background job
    job = create_job(
        job_type="ingest_document",
        resource_id=file_hash,
        idempotency_key=idempotency_key,
        metadata={"file_path": file_path}
    )
    
    try:
        mark_running(job["id"])
        result = ingest_file(file_path)
        mark_completed(job["id"], result)
        return result
    except Exception as e:
        mark_failed(job["id"], str(e))
        raise
```

### Periodic Golden Evaluation Check

```python
from app.services.background_jobs import create_job, next_retryable_job, JobStatus
from app.services.golden_evaluation import run_all_golden_evaluations
import time

def periodic_evaluation_check(interval_seconds: int = 3600):
    """Run golden evaluations periodically."""
    while True:
        job = create_job(
            job_type="evaluate_golden_set",
            resource_type="evaluation_dataset",
            resource_id="all_categories"
        )
        
        mark_running(job["id"])
        result = run_all_golden_evaluations()
        
        if result["summary"]["total_failed"] > 0:
            mark_failed(job["id"], f"Evaluation failed: {result}")
        else:
            mark_completed(job["id"], result)
        
        time.sleep(interval_seconds)
```

## Testing

### Run Only Local Tests (No Database Required)

```bash
pytest tests/test_background_jobs.py::TestGoldenEvaluation -v
pytest tests/ -k "not external_dependency" -q
```

### Run All Tests (Requires PostgreSQL)

```bash
pytest tests/test_background_jobs.py -v
pytest tests/ -q
```

### Mark Custom Tests as External Dependency

```python
import pytest

@pytest.mark.external_dependency
def test_my_database_feature():
    # This test requires PostgreSQL
    pass
```

## Status Codes

```python
from app.services.background_jobs import JobStatus

JobStatus.QUEUED.value      # "queued"      - Waiting to run
JobStatus.RUNNING.value     # "running"     - Currently executing
JobStatus.COMPLETED.value   # "completed"   - Successfully finished
JobStatus.FAILED.value      # "failed"      - Max retries exceeded
JobStatus.RETRYING.value    # "retrying"    - Waiting for retry
JobStatus.SKIPPED.value     # "skipped"     - Idempotent duplicate
```

## Environment Variables

```bash
# Laptop environment (default)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=projectrag
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Enable cloud connectors (when ready)
ENABLE_CLOUD_CONNECTORS=false  # Default - keep cloud dormant

# Enforce RBAC and auth (production)
ENFORCE_RBAC=false  # Default - local mode permissive
LOCAL_MODE=true     # Default - no Docker required
```

## Troubleshooting

### Issue: "Table 'background_jobs' does not exist"
**Solution**: Initialize database schema
```bash
# With psql
psql -U postgres -d projectrag < scripts/init_postgres.sql

# Or with Docker
docker-compose up -d postgres
docker-compose exec postgres psql -U postgres -d projectrag < scripts/init_postgres.sql
```

### Issue: "psycopg2.ProgrammingError: can't adapt type 'dict'"
**Solution**: This is fixed in the latest code - upgrade to the new services

### Issue: Tests marked as external_dependency are skipped
**Solution**: This is expected. Run with:
```bash
pytest -m "not external_dependency"  # Run local tests
pytest -m "external_dependency"      # Run DB tests
```

## References

- Implementation Report: [docs/phase_a_implementation_report.md](../docs/phase_a_implementation_report.md)
- Background Jobs Service: [app/services/background_jobs.py](../app/services/background_jobs.py)
- Idempotency Service: [app/services/idempotency.py](../app/services/idempotency.py)
- Golden Evaluation Service: [app/services/golden_evaluation.py](../app/services/golden_evaluation.py)
- Test Suite: [tests/test_background_jobs.py](../tests/test_background_jobs.py)
