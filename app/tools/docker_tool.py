"""Safe Docker read-only tool wrappers."""

from __future__ import annotations

import subprocess
from typing import Any

_BLOCKED_TERMS = (
    "delete",
    "drop",
    "truncate",
    "docker rm",
    "docker volume rm",
    "terraform apply",
    "terraform destroy",
)


def _blocked(text: str) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in _BLOCKED_TERMS)


def _run(args: list[str]) -> dict[str, Any]:
    command_text = " ".join(args)
    if _blocked(command_text):
        return {"status": "blocked", "command": args, "stdout": "", "stderr": "Blocked unsafe command"}
    completed = subprocess.run(args, capture_output=True, text=True, check=False)
    return {
        "status": "ok" if completed.returncode == 0 else "failed",
        "command": args,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def docker_ps() -> dict[str, Any]:
    """Run read-only `docker ps`."""
    return _run(["docker", "ps"])


def docker_logs(container_name: str, tail: int = 100) -> dict[str, Any]:
    """Run read-only `docker logs` for a specific container."""
    safe_tail = max(1, min(int(tail), 1000))
    if _blocked(container_name):
        return {"status": "blocked", "stdout": "", "stderr": "Blocked unsafe container name"}
    return _run(["docker", "logs", "--tail", str(safe_tail), str(container_name)])
