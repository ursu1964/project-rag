"""tenant and JSONB filter performance indexes

Revision ID: 0002_tenant_jsonb_indexes
Revises: 0001_baseline_schema
Create Date: 2026-06-18
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002_tenant_jsonb_indexes"
down_revision = "0001_baseline_schema"
branch_labels = None
depends_on = None

_INDEX_CREATES = (
    """
    CREATE INDEX IF NOT EXISTS idx_documents_tenant_created_at
    ON documents ((COALESCE(metadata->>'tenant_id', 'local')), created_at DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_documents_tenant_file_hash
    ON documents ((COALESCE(metadata->>'tenant_id', 'local')), file_hash)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chunks_tenant_document_chunk_index
    ON chunks ((COALESCE(metadata->>'tenant_id', 'local')), document_id, chunk_index)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chunks_tenant_created_at
    ON chunks ((COALESCE(metadata->>'tenant_id', 'local')), created_at DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_memory_items_tenant_created_at
    ON memory_items ((COALESCE(value->>'tenant_id', 'local')), created_at DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_workflow_runs_tenant_created_at
    ON workflow_runs ((COALESCE(input->>'tenant_id', 'local')), created_at DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_agent_runs_tenant_created_at
    ON agent_runs ((COALESCE(input->>'tenant_id', 'local')), created_at DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_validation_results_workflow_id
    ON validation_results (workflow_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_validation_results_tenant_created_at
    ON validation_results ((COALESCE(details->>'tenant_id', 'local')), created_at DESC)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_experience_runs_tenant_created_at
    ON experience_runs ((COALESCE(plan->>'tenant_id', 'local')), created_at DESC)
    """,
)

_INDEX_DROPS = (
    "DROP INDEX IF EXISTS idx_experience_runs_tenant_created_at",
    "DROP INDEX IF EXISTS idx_validation_results_tenant_created_at",
    "DROP INDEX IF EXISTS idx_validation_results_workflow_id",
    "DROP INDEX IF EXISTS idx_agent_runs_tenant_created_at",
    "DROP INDEX IF EXISTS idx_workflow_runs_tenant_created_at",
    "DROP INDEX IF EXISTS idx_memory_items_tenant_created_at",
    "DROP INDEX IF EXISTS idx_chunks_tenant_created_at",
    "DROP INDEX IF EXISTS idx_chunks_tenant_document_chunk_index",
    "DROP INDEX IF EXISTS idx_documents_tenant_file_hash",
    "DROP INDEX IF EXISTS idx_documents_tenant_created_at",
)


def upgrade() -> None:
    bind = op.get_bind()
    for statement in _INDEX_CREATES:
        bind.exec_driver_sql(statement)


def downgrade() -> None:
    bind = op.get_bind()
    for statement in _INDEX_DROPS:
        bind.exec_driver_sql(statement)
