"""workflow checkpoints and durable retry scheduling

Revision ID: 0003_workflow_ckpt_retry
Revises: 0002_tenant_jsonb_indexes
Create Date: 2026-06-18
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "0003_workflow_ckpt_retry"
down_revision = "0002_tenant_jsonb_indexes"
branch_labels = None
depends_on = None


_UPGRADE_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS workflow_checkpoints (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        workflow_id UUID NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
        step_name TEXT NOT NULL,
        state JSONB NOT NULL DEFAULT '{}'::jsonb,
        status TEXT NOT NULL DEFAULT 'running',
        error TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (workflow_id, step_name)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_workflow_id
    ON workflow_checkpoints(workflow_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_status
    ON workflow_checkpoints(status)
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_updated_at
    ON workflow_checkpoints(updated_at DESC)
    """,
    """
    ALTER TABLE background_jobs
    ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMPTZ
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_background_jobs_next_retry_at
    ON background_jobs(next_retry_at)
    """,
)

_DOWNGRADE_STATEMENTS = (
    "DROP INDEX IF EXISTS idx_background_jobs_next_retry_at",
    "ALTER TABLE background_jobs DROP COLUMN IF EXISTS next_retry_at",
    "DROP INDEX IF EXISTS idx_workflow_checkpoints_updated_at",
    "DROP INDEX IF EXISTS idx_workflow_checkpoints_status",
    "DROP INDEX IF EXISTS idx_workflow_checkpoints_workflow_id",
    "DROP TABLE IF EXISTS workflow_checkpoints",
)


def upgrade() -> None:
    bind = op.get_bind()
    for statement in _UPGRADE_STATEMENTS:
        bind.exec_driver_sql(statement)


def downgrade() -> None:
    bind = op.get_bind()
    for statement in _DOWNGRADE_STATEMENTS:
        bind.exec_driver_sql(statement)
