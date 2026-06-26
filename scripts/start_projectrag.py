"""One-command local launcher for ProjectRAG."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.launch_dashboards import main  # noqa: E402


if __name__ == "__main__":
    sys.argv = [
        sys.argv[0],
        "--setup",
        "--with-observability",
        "--auto-port",
        "--auto-ui-port",
        "--open",
        *sys.argv[1:],
    ]
    raise SystemExit(main())
