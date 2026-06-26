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
import urllib.request
import webbrowser
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
        default="otel-collector,blackbox,alertmanager,prometheus,grafana",
        help="Comma-separated service names to start from compose",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Start local infrastructure and run database/GraphDB initialization before launching dashboards",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open dashboard URLs in the default browser once services are launched",
    )
    parser.add_argument(
        "--wait-timeout",
        type=int,
        default=90,
        help="Seconds to wait for services during setup/open checks",
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


def _run_step(cmd: list[str], repo_root: Path, env: dict[str, str] | None = None) -> int:
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=repo_root, env=env, check=False).returncode


def _wait_for_url(url: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if 200 <= response.status < 500:
                    return True
        except Exception:
            time.sleep(1)
    return False


def _wait_for_port(host: str, port: int, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(1)
    return False


def _start_infrastructure(compose_file: str, repo_root: Path, wait_timeout: int) -> int:
    services = ["postgres", "redis", "qdrant", "graphdb"]
    code = _run_step(["docker", "compose", "-f", compose_file, "up", "-d", *services], repo_root)
    if code != 0:
        return code

    postgres_port = int(os.getenv("POSTGRES_PORT", "5433"))
    if not _wait_for_port("127.0.0.1", postgres_port, wait_timeout):
        print(
            f"Error: PostgreSQL did not become reachable on port {postgres_port}.", file=sys.stderr
        )
        return 1
    if not _wait_for_url(
        os.getenv("GRAPHDB_URL", "http://localhost:7200").rstrip("/") + "/rest/repositories",
        wait_timeout,
    ):
        print("Error: GraphDB did not become reachable.", file=sys.stderr)
        return 1
    return 0


def _initialize_local_state(repo_root: Path) -> int:
    steps = [
        [
            "docker",
            "exec",
            "projectrag-postgres",
            "psql",
            "-U",
            "projectrag",
            "-d",
            "projectrag",
            "-f",
            "/docker-entrypoint-initdb.d/01-init.sql",
        ],
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        [sys.executable, "-m", "scripts.init_graphdb_repository"],
    ]
    for cmd in steps:
        code = _run_step(cmd, repo_root)
        if code != 0:
            return code
    return 0


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
    cmd = ["docker", "compose", "-f", compose_file, "up", "-d", "--no-deps", *services]
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


def _select_observability_ports() -> dict[str, str]:
    ports = {
        "PROMETHEUS_PORT": int(os.getenv("PROMETHEUS_PORT", "9091")),
        "ALERTMANAGER_PORT": int(os.getenv("ALERTMANAGER_PORT", "9094")),
        "GRAFANA_PORT": int(os.getenv("GRAFANA_PORT", "3001")),
    }
    selected: dict[str, str] = {}
    for name, port in ports.items():
        if not _is_port_available("127.0.0.1", port):
            free_port = _find_free_port("127.0.0.1", port + 1, 200)
            if free_port is None:
                print(f"Warning: No free port found for {name} after {port}.", file=sys.stderr)
                selected[name] = str(port)
                continue
            print(f"{name} {port} busy; auto-selected {free_port}.")
            port = free_port
        selected[name] = str(port)
    return selected


def _open_dashboards(urls: list[tuple[str, str]], wait_timeout: int) -> None:
    for name, url in urls:
        if _wait_for_url(url, wait_timeout):
            print(f"Opening {name}: {url}")
            webbrowser.open_new_tab(url)
        else:
            print(f"Warning: {name} was not reachable yet: {url}", file=sys.stderr)


def main() -> int:
    args = _parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    api_port = args.port
    ui_port = args.ui_port

    if args.setup:
        if shutil.which("docker") is None:
            print("Error: docker is required for --setup.", file=sys.stderr)
            return 1
        code = _start_infrastructure(args.compose_file, repo_root, args.wait_timeout)
        if code != 0:
            return code
        code = _initialize_local_state(repo_root)
        if code != 0:
            return code

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
    observability_ports: dict[str, str] = {}

    if args.with_observability:
        if shutil.which("docker") is None:
            print("Warning: docker not found; skipping observability startup.")
        else:
            configured_services = _compose_services(args.compose_file, repo_root)
            requested = [s.strip() for s in args.observability_services.split(",") if s.strip()]
            available = [s for s in requested if s in configured_services]
            if available:
                observability_ports = _select_observability_ports()
                _start_observability(
                    args.compose_file,
                    available,
                    repo_root,
                    env_overrides={"APP_PORT": str(api_port), **observability_ports},
                )
            else:
                print(
                    "Observability services not found in compose file. "
                    "Skipping Alertmanager/Grafana/Prometheus startup."
                )

    processes: list[subprocess.Popen] = []
    try:
        api_url = f"http://{args.host if args.host != '0.0.0.0' else '127.0.0.1'}:{api_port}"
        api_proc = _start_api(repo_root, args.host, api_port, args.reload)
        processes.append(api_proc)

        ui_proc = _start_ui(repo_root, ui_port, api_url)
        processes.append(ui_proc)

        print(f"API running at {api_url}")
        print(f"Cockpit dashboard running at http://127.0.0.1:{ui_port}")
        if args.open:
            dashboard_urls = [
                ("ProjectRAG Cockpit", f"http://127.0.0.1:{ui_port}"),
                ("API docs", f"{api_url}/docs"),
                ("GraphDB", os.getenv("GRAPHDB_URL", "http://127.0.0.1:7200")),
            ]
            if args.with_observability:
                dashboard_urls.extend(
                    [
                        (
                            "Grafana",
                            f"http://127.0.0.1:{observability_ports.get('GRAFANA_PORT', os.getenv('GRAFANA_PORT', '3001'))}",
                        ),
                        (
                            "Prometheus",
                            f"http://127.0.0.1:{observability_ports.get('PROMETHEUS_PORT', os.getenv('PROMETHEUS_PORT', '9091'))}",
                        ),
                        (
                            "Alertmanager",
                            f"http://127.0.0.1:{observability_ports.get('ALERTMANAGER_PORT', os.getenv('ALERTMANAGER_PORT', '9094'))}",
                        ),
                    ]
                )
            _open_dashboards(dashboard_urls, args.wait_timeout)
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
