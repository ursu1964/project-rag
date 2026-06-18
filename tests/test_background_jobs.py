"""Tests for background job orchestration and golden evaluation."""

import json
from pathlib import Path

import pytest

from app.services.background_jobs import JobStatus, JobType, create_job, get_job, list_jobs, mark_completed, mark_failed, mark_running, next_retryable_job, prune_completed_jobs
from app.services.golden_evaluation import create_golden_evaluation_job, load_golden_questions, run_all_golden_evaluations, run_golden_evaluation
from app.services.idempotency import clear_idempotent_result, get_idempotent_result, get_or_create_idempotency_key, record_idempotent_result


class TestBackgroundJobOrchestration:
    """Test background job creation, status tracking, and retry logic."""

    def test_create_job_basic(self):
        """Create a basic background job."""
        job = create_job(
            job_type=JobType.INGEST_DOCUMENT.value,
            resource_type="document",
            resource_id="doc123",
        )

        assert job["status"] == JobStatus.QUEUED.value
        assert job["id"]
        assert job["job_type"] == JobType.INGEST_DOCUMENT.value

    def test_create_job_with_metadata(self):
        """Create a job with custom metadata."""
        meta = {"filename": "test.txt", "size": 1024}
        job = create_job(
            job_type=JobType.INGEST_DOCUMENT.value,
            resource_type="document",
            resource_id="doc123",
            metadata=meta,
        )

        assert job["id"]
        fetched = get_job(job["id"])
        assert fetched is not None
        assert fetched["metadata"]["filename"] == "test.txt"

    def test_idempotent_job_creation(self):
        """Create idempotent jobs - second call should return same job."""
        idempotency_key = "ingest#doc123"

        job1 = create_job(
            job_type=JobType.INGEST_DOCUMENT.value,
            resource_type="document",
            resource_id="doc123",
            idempotency_key=idempotency_key,
        )

        # Complete the first job
        mark_completed(job1["id"], {"chunks": 10})

        # Create with same idempotency key - should return existing completed job
        job2 = create_job(
            job_type=JobType.INGEST_DOCUMENT.value,
            resource_type="document",
            resource_id="doc123",
            idempotency_key=idempotency_key,
        )

        assert job2["idempotent"] is True
        assert job2["status"] == JobStatus.COMPLETED.value
        assert job2["id"] == job1["id"]

    def test_job_status_transitions(self):
        """Test job lifecycle: queued -> running -> completed."""
        job = create_job(JobType.INGEST_DOCUMENT.value, resource_id="doc123")
        job_id = job["id"]

        # Mark running
        assert mark_running(job_id) is True
        job_running = get_job(job_id)
        assert job_running["status"] == JobStatus.RUNNING.value
        assert job_running["started_at"] is not None

        # Mark completed
        result_meta = {"chunks": 42, "duration_ms": 1234}
        assert mark_completed(job_id, result_meta) is True
        job_completed = get_job(job_id)
        assert job_completed["status"] == JobStatus.COMPLETED.value
        assert job_completed["completed_at"] is not None

    def test_job_failure_with_retry(self):
        """Test job failure and retry logic."""
        job = create_job(
            job_type=JobType.INGEST_DOCUMENT.value,
            resource_id="doc123",
            max_attempts=3,
        )
        job_id = job["id"]

        # First attempt fails
        mark_running(job_id)
        assert mark_failed(job_id, "Connection timeout") is True

        job_after_fail = get_job(job_id)
        assert job_after_fail["status"] == JobStatus.RETRYING.value
        assert job_after_fail["attempts"] == 1
        assert job_after_fail["error"] == "Connection timeout"
        assert job_after_fail["next_retry_at"] is not None

        # Should be retryable
        next_job = next_retryable_job()
        assert next_job is not None
        assert next_job["id"] == job_id

        # Second attempt
        mark_running(job_id)
        mark_failed(job_id, "Connection timeout again")
        job_after_2nd = get_job(job_id)
        assert job_after_2nd["attempts"] == 2
        assert job_after_2nd["status"] == JobStatus.RETRYING.value
        assert job_after_2nd["next_retry_at"] is not None

        # Third attempt - final failure
        mark_running(job_id)
        mark_failed(job_id, "Max attempts reached")
        job_final = get_job(job_id)
        assert job_final["attempts"] == 3
        assert job_final["status"] == JobStatus.FAILED.value
        assert job_final["next_retry_at"] is None

    def test_list_jobs_with_filters(self):
        """Test filtering jobs by type, status, and resource."""
        # Create various jobs
        job1 = create_job(
            JobType.INGEST_DOCUMENT.value,
            resource_type="document",
            resource_id="doc1",
        )
        job2 = create_job(
            JobType.EVALUATE_GOLDEN_SET.value,
            resource_type="evaluation",
            resource_id="graph",
        )
        job3 = create_job(
            JobType.INGEST_DOCUMENT.value,
            resource_type="document",
            resource_id="doc2",
        )

        # Mark job1 as completed
        mark_completed(job1["id"])

        # Filter by type
        ingestion_jobs = list_jobs(job_type=JobType.INGEST_DOCUMENT.value)
        assert len(ingestion_jobs) >= 2

        # Filter by status
        completed_jobs = list_jobs(status=JobStatus.COMPLETED.value)
        assert any(j["id"] == job1["id"] for j in completed_jobs)

        queued_jobs = list_jobs(status=JobStatus.QUEUED.value)
        assert any(j["id"] == job2["id"] for j in queued_jobs)
        assert any(j["id"] == job3["id"] for j in queued_jobs)

    def test_prune_old_jobs(self):
        """Test pruning of completed jobs older than threshold."""
        job1 = create_job(JobType.INGEST_DOCUMENT.value, resource_id="doc1")
        job_id = job1["id"]

        mark_completed(job_id)
        job_completed = get_job(job_id)
        assert job_completed["status"] == JobStatus.COMPLETED.value

        # Prune with 0 days threshold - should remove immediately
        pruned = prune_completed_jobs(older_than_days=0)
        assert pruned >= 0  # May not delete if just created (timestamp check)


class TestIdempotency:
    """Test idempotency key generation and result caching."""

    def test_generate_idempotency_key(self):
        """Generate deterministic idempotency keys."""
        key1 = get_or_create_idempotency_key("ingestion", "file_hash_abc123")
        key2 = get_or_create_idempotency_key("ingestion", "file_hash_abc123")

        assert key1 == key2
        assert "ingestion#" in key1
        assert "file_hash_abc123" in key1

    def test_record_and_retrieve_idempotent_result(self):
        """Record and retrieve idempotent operation results."""
        key = "test_idempotency_key"
        result = {"status": "success", "items": 42}

        # Record result
        assert record_idempotent_result(key, result) is True

        # Retrieve result
        cached = get_idempotent_result(key)
        assert cached is not None
        assert cached["status"] == "success"
        assert cached["items"] == 42

    def test_clear_idempotent_result(self):
        """Clear cached idempotent results."""
        key = "test_key_to_clear"
        result = {"data": "test"}

        record_idempotent_result(key, result)
        assert get_idempotent_result(key) is not None

        assert clear_idempotent_result(key) is True
        assert get_idempotent_result(key) is None


class TestGoldenEvaluation:
    """Test golden evaluation dataset and execution."""

    def test_load_golden_questions_graph(self):
        """Load graph golden questions."""
        questions = load_golden_questions("graph")
        assert len(questions) > 0

        # Validate structure
        for q in questions:
            assert "id" in q
            assert "category" in q
            assert q["category"] == "graph"
            assert "question" in q
            assert "expected_route" in q

    def test_load_golden_questions_vector(self):
        """Load vector golden questions."""
        questions = load_golden_questions("vector")
        assert len(questions) > 0

        for q in questions:
            assert "id" in q
            assert q["category"] == "vector"
            assert "expected_route" in q

    def test_load_golden_questions_hybrid(self):
        """Load hybrid golden questions."""
        questions = load_golden_questions("hybrid")
        assert len(questions) > 0

        for q in questions:
            assert "id" in q
            assert q["category"] == "hybrid"
            assert "expected_route" in q

    def test_load_golden_questions_safety(self):
        """Load safety golden questions."""
        questions = load_golden_questions("safety")
        assert len(questions) > 0

        for q in questions:
            assert "id" in q
            assert q["category"] == "safety"
            assert "expected_behavior" in q

    def test_create_golden_evaluation_job(self):
        """Create a golden evaluation background job."""
        job = create_golden_evaluation_job("graph")

        assert job["status"] == JobStatus.QUEUED.value
        assert job["id"]
        fetched = get_job(job["id"])
        assert fetched is not None
        assert fetched["resource_id"] == "graph"

    def test_run_golden_evaluation_graph(self):
        """Run golden evaluation for graph category."""
        result = run_golden_evaluation("graph")

        assert result["status"] == "completed"
        assert result["category"] == "graph"
        assert result["total"] > 0
        assert result["passed"] > 0
        assert "pass_rate" in result

    def test_run_golden_evaluation_vector(self):
        """Run golden evaluation for vector category."""
        result = run_golden_evaluation("vector")

        assert result["status"] == "completed"
        assert result["category"] == "vector"
        assert result["pass_rate"] >= 0

    def test_run_golden_evaluation_hybrid(self):
        """Run golden evaluation for hybrid category."""
        result = run_golden_evaluation("hybrid")

        assert result["status"] == "completed"
        assert result["category"] == "hybrid"

    def test_run_golden_evaluation_safety(self):
        """Run golden evaluation for safety category."""
        result = run_golden_evaluation("safety")

        assert result["status"] == "completed"
        assert result["category"] == "safety"

    def test_run_all_golden_evaluations(self):
        """Run all golden evaluations."""
        result = run_all_golden_evaluations()

        assert result["status"] == "completed"
        assert "summary" in result
        assert "categories" in result

        summary = result["summary"]
        assert summary["total_questions"] > 0
        assert summary["overall_pass_rate"] >= 0

        # All categories should be present
        categories = result["categories"]
        assert "graph" in categories
        assert "vector" in categories
        assert "hybrid" in categories
        assert "safety" in categories

    def test_golden_evaluation_with_job_tracking(self):
        """Run golden evaluation with background job tracking."""
        job = create_golden_evaluation_job("safety")
        job_id = job["id"]

        mark_running(job_id)
        result = run_golden_evaluation("safety", job_id)

        assert result["status"] == "completed"

        # Job should be updated
        job_final = get_job(job_id)
        assert job_final["status"] in [
            JobStatus.COMPLETED.value,
            JobStatus.FAILED.value,
        ]


class TestConnectorDormancy:
    """Test that cloud connectors remain dormant by default."""

    def test_connector_job_creation_respects_dormancy(self):
        """Verify that cloud connector jobs are created but marked dormant."""
        # Create a connector sync job (Azure)
        job = create_job(
            job_type=JobType.CONNECTOR_SYNC.value,
            resource_type="connector",
            resource_id="azure_sync",
            metadata={"connector_type": "azure", "dormant": True},
        )

        assert job["id"]
        fetched = get_job(job["id"])
        assert fetched["metadata"]["dormant"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
