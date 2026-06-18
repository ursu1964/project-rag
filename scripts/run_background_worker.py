"""Run ProjectRAG durable background worker loop.

Suitable for long-running process managers (systemd/docker) and one-shot runs.
"""

from __future__ import annotations

import argparse
from typing import Sequence

from app.core.logging import get_logger
from app.services.background_jobs import run_worker_loop
from app.services.background_worker import build_job_handler_map, dispatch_job

logger = get_logger(__name__)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ProjectRAG background worker")
    parser.add_argument("--worker-id", default="projectrag-worker", help="Worker identity stored in claim metadata")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Polling interval in seconds when queue is idle")
    parser.add_argument("--max-iterations", type=int, default=None, help="Optional max loop iterations (for tests/one-shot runs)")
    parser.add_argument("--once", action="store_true", help="Run a single claim/execute cycle")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    handlers = build_job_handler_map()

    max_iterations = 1 if args.once else args.max_iterations
    logger.info(
        "Starting background worker: worker_id=%s poll_interval=%s max_iterations=%s",
        args.worker_id,
        args.poll_interval,
        max_iterations,
    )

    stats = run_worker_loop(
        job_handler=lambda job: dispatch_job(job, handlers=handlers),
        worker_id=args.worker_id,
        poll_interval_seconds=args.poll_interval,
        max_iterations=max_iterations,
    )

    logger.info("Background worker stopped: %s", stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
