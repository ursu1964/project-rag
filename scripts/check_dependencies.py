"""Generate a simple dependency report from installed packages."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"

CRITICAL = {
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic-settings",
    "psycopg2-binary",
    "pgvector",
    "langgraph",
    "langchain",
    "requests",
    "prometheus-client",
}


def _requirements() -> list[str]:
    packages = []
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        package = line.split("[", 1)[0].split("=", 1)[0].split(">", 1)[0].split("<", 1)[0].strip()
        packages.append(package)
    return packages


def _version(package: str) -> str:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return "not-installed"


def _risk(package: str, version: str) -> str:
    if version == "not-installed":
        return "high"
    if package in CRITICAL:
        return "medium"
    return "low"


def _recommendation(package: str, version: str) -> str:
    if version == "not-installed":
        return "install or remove from requirements"
    if package in CRITICAL:
        return "pin for production and review quarterly"
    return "review quarterly"


def generate_report() -> list[dict[str, str]]:
    report = []
    for package in _requirements():
        version = _version(package)
        report.append(
            {
                "package": package,
                "version": version,
                "risk": _risk(package, version),
                "update_recommendation": _recommendation(package, version),
            }
        )
    return report


def main() -> None:
    rows = generate_report()
    print("package,version,risk,update_recommendation")
    for row in rows:
        print(
            f"{row['package']},{row['version']},{row['risk']},{row['update_recommendation']}"
        )


if __name__ == "__main__":
    main()
