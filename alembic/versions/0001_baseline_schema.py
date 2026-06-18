"""baseline schema from init_postgres.sql

Revision ID: 0001_baseline_schema
Revises:
Create Date: 2026-06-18
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_baseline_schema"
down_revision = None
branch_labels = None
depends_on = None


def _schema_sql() -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / "scripts" / "init_postgres.sql").read_text(encoding="utf-8")


def _split_sql_statements(sql: str) -> list[str]:
    statements: list[str] = []
    parts = sql.split(";")
    for part in parts:
        statement = part.strip()
        if statement:
            statements.append(statement)
    return statements


def upgrade() -> None:
    bind = op.get_bind()
    for statement in _split_sql_statements(_schema_sql()):
        bind.exec_driver_sql(statement)


def downgrade() -> None:
    # Baseline migration downgrade is intentionally not destructive.
    pass
