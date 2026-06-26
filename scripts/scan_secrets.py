"""Lightweight secret-pattern scan for tracked repository files."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_ALLOWLIST_PATH_PARTS = (
    "alertmanager.local.example.yml",
    "deploy/monitoring/alertmanager/alertmanager.yml",
    ".env.example",
)

_PATTERNS = (
    ("aws_access_key_id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("slack_webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9]+/[A-Za-z0-9]+/[A-Za-z0-9]+")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("generic_assignment", re.compile(r"(?i)\b(password|secret|api[_-]?key|token)\s*[:=]\s*['\"]([^'\"\s#]{20,})['\"]")),
)

_TEXT_SUFFIXES = {
    ".cfg", ".css", ".env", ".example", ".html", ".ini", ".js", ".json", ".md", ".py",
    ".sh", ".sql", ".toml", ".ts", ".tsx", ".txt", ".yaml", ".yml",
}


def _tracked_files() -> list[Path]:
    result = subprocess.run(["git", "ls-files"], check=True, text=True, capture_output=True)
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def _is_scannable(path: Path) -> bool:
    if any(part in str(path) for part in _ALLOWLIST_PATH_PARTS):
        return False
    if path.suffix.lower() in _TEXT_SUFFIXES:
        return True
    return path.name in {"Dockerfile", "Makefile"}


def main() -> int:
    findings: list[str] = []
    for path in _tracked_files():
        if not _is_scannable(path) or not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in _PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path}:{line_no}: possible {name}")

    if findings:
        print("\n".join(findings))
        return 1
    print("secret-scan-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
