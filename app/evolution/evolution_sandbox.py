"""Evolution sandbox for reviewable improvement proposals.

Rules enforced by this module:
- no production self-modification
- no automatic deployment
- no direct code overwrite
- all proposals become reviewable patches
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class EvolutionProposal:
    """Reviewable patch proposal generated in a sandbox-only mode."""

    id: str
    title: str
    rationale: str
    patch: str
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "review_required"
    execution: str = "disabled"


_FORBIDDEN_MARKERS = ("git apply", "git commit", "rm -rf", "sudo", "terraform apply", "terraform destroy")


def validate_proposal_patch(patch: str) -> dict[str, Any]:
    """Validate that a proposal is reviewable text, not an execution instruction."""
    text = str(patch or "")
    violations = [marker for marker in _FORBIDDEN_MARKERS if marker in text.lower()]
    return {
        "valid": bool(text.strip()) and not violations,
        "violations": violations,
        "requires_review": True,
        "execution": "disabled",
    }


def create_patch_proposal(
    title: str,
    rationale: str,
    patch: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a reviewable patch proposal without applying it."""
    validation = validate_proposal_patch(patch)
    proposal = EvolutionProposal(
        id=str(uuid4()),
        title=title,
        rationale=rationale,
        patch=patch,
        metadata=metadata or {},
        status="review_required" if validation["valid"] else "rejected",
    )
    return {
        "proposal": proposal,
        "validation": validation,
        "production_modified": False,
        "automatic_deployment": False,
        "direct_code_overwrite": False,
    }
