"""Launch ProjectRAG dashboards in one command.

Starts:
- FastAPI API (required by Streamlit cockpit)
- Streamlit cockpit dashboard
- Optional observability stack services (Alertmanager/Grafana/Prometheus) via Docker Compose if present
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch ProjectRAG dashboards at once")
    parser.add_argument("--host", default=os.getenv("APP_HOST", "127.0.0.1"), help="API host")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("APP_PORT", "8001")),
        help="API port (use 8001 unless you intentionally free 8000)",
    )
    parser.add_argument(
        "--ui-port",
        type=int,
        default=int(os.getenv("UI_PORT", "8501")),
        help="Streamlit UI port",
    )
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload mode")
    parser.add_argument(
        "--auto-port",
        action="store_true",
        help="Auto-select next free API port if --port is busy",
    )
    parser.add_argument(
        "--auto-ui-port",
        action="store_true",
        help="Auto-select next free UI port if --ui-port is busy",
    )
    parser.add_argument(
        "--port-scan-limit",
        type=int,
        default=200,
        help="How many consecutive ports to scan when auto-port mode is enabled",
    )
    parser.add_argument(
        "--with-observability",
        action="store_true",
        help="Try to start Alertmanager/Grafana/Prometheus services from Docker Compose if configured",
    )
    parser.add_argument(
        "--compose-file",
        default="docker-compose.yml",
        help="Compose file used for observability services",
    )
    parser.add_argument(
        "--observability-services",
        default="alertmanager,grafana,prometheus",
        help="Comma-separated service names to start from compose",
    )
    return parser.parse_args()


def _is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def _find_free_port(host: str, start_port: int, scan_limit: int) -> int | None:
    limit = max(int(scan_limit), 1)
    for port in range(start_port, start_port + limit):
        if _is_port_available(host, port):
            return port
    return None


def _start_api(repo_root: Path, host: str, port: int, reload_enabled: bool) -> subprocess.Popen:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload_enabled:
        cmd.append("--reload")
    return subprocess.Popen(cmd, cwd=repo_root)


def _start_ui(repo_root: Path, port: int, api_url: str) -> subprocess.Popen:
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "ui/streamlit_app.py",
        "--server.port",
        str(port),
    ]
    env = os.environ.copy()
    env["PROJECTRAG_API_URL"] = api_url
    return subprocess.Popen(cmd, cwd=repo_root, env=env)


def _shutdown(processes: list[subprocess.Popen]) -> None:
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
    for proc in processes:
        if proc.poll() is None:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


def _compose_services(compose_file: str, repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["docker", "compose", "-f", compose_file, "config", "--services"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _start_observability(
    compose_file: str,
    services: list[str],
    repo_root: Path,
    env_overrides: dict[str, str] | None = None,
) -> None:
    cmd = ["docker", "compose", "-f", compose_file, "up", "-d", *services]
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(cmd, cwd=repo_root, check=False, env=env)
    if result.returncode == 0:
        print(f"Observability services started: {', '.join(services)}")
    else:
        print(
            "Warning: Failed to start observability services. "
            "You can still use the Streamlit cockpit dashboard.",
            file=sys.stderr,
        )


def main() -> int:
    args = _parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    api_port = args.port
    ui_port = args.ui_port

    if not _is_port_available(args.host, api_port):
        if args.auto_port:
            selected = _find_free_port(args.host, api_port + 1, args.port_scan_limit)
            if selected is None:
                print(
                    f"Error: No free API port found after {api_port} within scan limit {args.port_scan_limit}.",
                    file=sys.stderr,
                )
                return 1
            print(f"API port {api_port} busy; auto-selected API port {selected}.")
            api_port = selected
        else:
            print(
                f"Error: API port {api_port} is already in use. "
                "Use --auto-port or choose another --port.",
                file=sys.stderr,
            )
            return 1

    if not _is_port_available("127.0.0.1", ui_port):
        if args.auto_ui_port:
            selected = _find_free_port("127.0.0.1", ui_port + 1, args.port_scan_limit)
            if selected is None:
                print(
                    f"Error: No free UI port found after {ui_port} within scan limit {args.port_scan_limit}.",
                    file=sys.stderr,
                )
                return 1
            print(f"UI port {ui_port} busy; auto-selected UI port {selected}.")
            ui_port = selected
        else:
            print(
                f"Error: UI port {ui_port} is already in use. "
                "Use --auto-ui-port or choose another --ui-port.",
                file=sys.stderr,
            )
            return 1

    configured_services: list[str] = []
    using_compose_api = False

    if args.with_observability:
        if shutil.which("docker") is None:
            print("Warning: docker not found; skipping observability startup.")
        else:
            configured_services = _compose_services(args.compose_file, repo_root)
            requested = [s.strip() for s in args.observability_services.split(",") if s.strip()]
            available = [s for s in requested if s in configured_services]
            if available:
                _start_observability(
                    args.compose_file,
                    available,
                    repo_root,
                    env_overrides={"APP_PORT": str(api_port)},
                )
                using_compose_api = "api" in configured_services
            else:
                print(
                    "Observability services not found in compose file. "
                    "Skipping Alertmanager/Grafana/Prometheus startup."
                )

    processes: list[subprocess.Popen] = []
    try:
        api_url = f"http://{args.host if args.host != '0.0.0.0' else '127.0.0.1'}:{api_port}"
        if using_compose_api:
            print(f"Using Docker Compose API service at {api_url}")
        else:
            api_proc = _start_api(repo_root, args.host, api_port, args.reload)
            processes.append(api_proc)

        ui_proc = _start_ui(repo_root, ui_port, api_url)
        processes.append(ui_proc)

        print(f"API running at {api_url}")
        print(f"Cockpit dashboard running at http://127.0.0.1:{ui_port}")
        print("Press Ctrl+C to stop started processes.")

        while True:
            time.sleep(1)
            for proc in processes:
                code = proc.poll()
                if code is not None:
                    print(f"A process exited with code {code}. Shutting down...")
                    _shutdown(processes)
                    return code
    except KeyboardInterrupt:
        print("\nStopping dashboards...")
        _shutdown(processes)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
