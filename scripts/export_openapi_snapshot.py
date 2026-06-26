"""Export or validate the committed OpenAPI contract snapshot."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

SNAPSHOT_PATH = Path("docs/openapi.snapshot.json")


def _openapi_schema() -> dict[str, Any]:
    os.environ.setdefault("GRAPHDB_ENSURE_REPOSITORY_ON_STARTUP", "false")
    from app.main import create_app

    return create_app().openapi()


def _canonical(schema: dict[str, Any]) -> str:
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export or validate docs/openapi.snapshot.json")
    parser.add_argument("--check", action="store_true", help="Fail if the snapshot differs from current app schema")
    parser.add_argument("--output", default=str(SNAPSHOT_PATH), help="Snapshot path")
    args = parser.parse_args()

    output = Path(args.output)
    current = _canonical(_openapi_schema())
    if args.check:
        expected = output.read_text(encoding="utf-8")
        if current != expected:
            raise SystemExit(
                f"OpenAPI snapshot is stale: run `python -m scripts.export_openapi_snapshot --output {output}`"
            )
        print("openapi-snapshot-ok")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(current, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
