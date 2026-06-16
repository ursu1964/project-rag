"""Learning agent for summarizing execution and storing experience."""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.repositories.experience_repository import (
    add_experience_step,
    create_experience_run,
    store_experience_outcome,
)

logger = get_logger(__name__)


def _summarize_execution(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "objective": state.get("objective") or state.get("question") or "",
        "route": state.get("route"),
        "plan_steps": len(state.get("plan") or []),
        "security": state.get("security") or {},
        "cost": state.get("cost") or {},
        "validation": state.get("validation") or {},
        "execution": state.get("execution") or {"status": "not_attempted"},
    }


def _identify_mistakes(state: dict[str, Any]) -> list[str]:
    mistakes: list[str] = []
    validation = state.get("validation") or {}
    if validation and not validation.get("grounded", False):
        mistakes.append("Validation did not confirm grounded output.")
    if validation.get("warnings"):
        mistakes.extend(f"Validation warning: {warning}" for warning in validation["warnings"])
    if state.get("security", {}).get("blocked"):
        mistakes.append("Execution was blocked by security policy.")
    if not state.get("plan"):
        mistakes.append("No explicit plan was produced.")
    return mistakes


def _identify_successes(state: dict[str, Any]) -> list[str]:
    successes: list[str] = []
    if state.get("plan"):
        successes.append("Created a recommendation plan.")
    if state.get("security"):
        successes.append("Completed security review.")
    if state.get("cost"):
        successes.append("Estimated cost/resource impact.")
    if state.get("validation"):
        successes.append("Completed validation pass.")
    return successes


def _lessons(mistakes: list[str], successes: list[str]) -> list[str]:
    lessons = [
        "Keep recommendations evidence-based.",
        "Require human approval before execution.",
    ]
    if mistakes:
        lessons.append("Review validation warnings and blocked execution before acting.")
    if successes:
        lessons.append("Reuse successful planning, security, cost, and validation structure.")
    return lessons


def _store_experience(state: dict[str, Any], summary: dict[str, Any], lessons: list[str]) -> str | None:
    goal = str(summary.get("objective") or "unspecified goal")
    experience_run_id = create_experience_run(goal, state.get("plan") or {})
    for index, step in enumerate(state.get("plan") or [], start=1):
        add_experience_step(experience_run_id, index, action=step, result={"status": "recommendation_only"})
    store_experience_outcome(
        experience_run_id,
        "completed",
        results=summary,
        lessons_learned=lessons,
    )
    return experience_run_id


def run(state: dict) -> dict:
    summary = _summarize_execution(state)
    mistakes = _identify_mistakes(state)
    successes = _identify_successes(state)
    lessons = _lessons(mistakes, successes)

    experience_run_id = None
    persistence_error = None
    try:
        experience_run_id = _store_experience(state, summary, lessons)
    except Exception as exc:  # Do not let learning persistence break the workflow.
        logger.warning("Experience persistence failed: %s", exc.__class__.__name__)
        persistence_error = exc.__class__.__name__

    learning = {
        "summary": summary,
        "mistakes": mistakes,
        "successes": successes,
        "lessons_learned": lessons,
        "experience_run_id": experience_run_id,
    }
    if persistence_error:
        learning["persistence_error"] = persistence_error

    return {**state, "learning": learning, "lessons_learned": lessons, "experience_run_id": experience_run_id}
