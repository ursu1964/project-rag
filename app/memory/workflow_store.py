"""Simple workflow run persistence."""

from __future__ import annotations

from app.repositories.workflow_repository import (
    complete_workflow_run,
    create_workflow_run,
    store_workflow_output,
)

__all__ = ["complete_workflow_run", "create_workflow_run", "store_workflow_output"]
