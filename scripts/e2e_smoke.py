"""End-to-end smoke checks for a running ProjectRAG stack."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Check:
    name: str
    url: str
    expect_json: bool = False
    expected_status: str | None = None


def _fetch(url: str, timeout: float) -> tuple[int, bytes, str]:
    request = urllib.request.Request(url, headers={"user-agent": "projectrag-e2e-smoke/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - local smoke URLs
        return response.status, response.read(), response.headers.get("content-type", "")


def _wait_for(check: Check, attempts: int, interval: float, timeout: float) -> dict[str, Any]:
    last_error = "not attempted"
    for attempt in range(1, attempts + 1):
        try:
            status, body, content_type = _fetch(check.url, timeout=timeout)
            if status < 200 or status >= 400:
                last_error = f"HTTP {status}"
                raise RuntimeError(last_error)

            parsed: Any = None
            if check.expect_json:
                parsed = json.loads(body.decode("utf-8"))
                if check.expected_status and parsed.get("status") != check.expected_status:
                    last_error = f"unexpected status payload: {parsed!r}"
                    raise RuntimeError(last_error)

            return {
                "name": check.name,
                "url": check.url,
                "attempt": attempt,
                "status_code": status,
                "content_type": content_type,
                "payload": parsed,
            }
        except (OSError, urllib.error.URLError, RuntimeError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < attempts:
                time.sleep(interval)

    raise RuntimeError(f"{check.name} failed after {attempts} attempts: {last_error}")


def main() -> int:
    api_url = os.getenv("PROJECTRAG_API_URL", "http://127.0.0.1:8001").rstrip("/")
    frontend_url = os.getenv("PROJECTRAG_FRONTEND_URL", "http://127.0.0.1:3000").rstrip("/")
    attempts = int(os.getenv("PROJECTRAG_E2E_ATTEMPTS", "30"))
    interval = float(os.getenv("PROJECTRAG_E2E_INTERVAL_SECONDS", "2"))
    timeout = float(os.getenv("PROJECTRAG_E2E_TIMEOUT_SECONDS", "5"))

    checks = (
        Check("api_health", f"{api_url}/health", expect_json=True, expected_status="ok"),
        Check("api_v1_health", f"{api_url}/api/v1/health", expect_json=True, expected_status="ok"),
        Check("frontend", frontend_url),
    )

    results = []
    for check in checks:
        results.append(_wait_for(check, attempts=attempts, interval=interval, timeout=timeout))

    print(json.dumps({"status": "ok", "checks": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2), file=sys.stderr)
        raise SystemExit(1)
