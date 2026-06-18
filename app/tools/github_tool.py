"""Safe git read-only tool wrappers."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

_ALLOWED = {"status", "diff"}
_BLOCKED_TERMS = ("delete", "drop", "truncate", "terraform apply", "terraform destroy")


def _blocked(text: str) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in _BLOCKED_TERMS)


def _run_git(args: list[str], repo_path: str | Path = ".") -> dict[str, Any]:
    if not args or args[0] not in _ALLOWED:
        return {"status": "blocked", "stdout": "", "stderr": "Only git status and git diff are allowed"}
    if _blocked(" ".join(args)):
        return {"status": "blocked", "stdout": "", "stderr": "Blocked unsafe git command"}
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "status": "ok" if completed.returncode == 0 else "failed",
        "command": ["git", *args],
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def git_status(repo_path: str | Path = ".") -> dict[str, Any]:
    """Run read-only `git status --short`."""
    return _run_git(["status", "--short"], repo_path)


def git_diff(repo_path: str | Path = ".") -> dict[str, Any]:
    """Run read-only `git diff`."""
    return _run_git(["diff"], repo_path)
