"""Local launcher for ProjectRAG API and optional Streamlit UI."""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch ProjectRAG services locally")
    parser.add_argument("--host", default=os.getenv("APP_HOST", "127.0.0.1"), help="API host")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("APP_PORT", "8000")),
        help="API port",
    )
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload mode")
    parser.add_argument("--with-ui", action="store_true", help="Launch Streamlit UI alongside API")
    parser.add_argument(
        "--ui-port",
        type=int,
        default=int(os.getenv("UI_PORT", "8501")),
        help="Streamlit UI port",
    )
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
        help="How many consecutive ports to scan when auto port mode is enabled",
    )
    return parser.parse_args()


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
                    f"Error: No free API port found after {api_port} within scan limit "
                    f"{args.port_scan_limit} on host {args.host}.",
                    file=sys.stderr,
                )
                return 1
            print(f"API port {api_port} busy; auto-selected API port {selected}.")
            api_port = selected
        else:
            print(
                f"Error: API port {api_port} on host {args.host} is already in use. "
                "Stop existing process or choose another --port, or use --auto-port.",
                file=sys.stderr,
            )
            return 1

    if args.with_ui and not _is_port_available("127.0.0.1", ui_port):
        if args.auto_ui_port:
            selected = _find_free_port("127.0.0.1", ui_port + 1, args.port_scan_limit)
            if selected is None:
                print(
                    f"Error: No free UI port found after {ui_port} within scan limit "
                    f"{args.port_scan_limit}.",
                    file=sys.stderr,
                )
                return 1
            print(f"UI port {ui_port} busy; auto-selected UI port {selected}.")
            ui_port = selected
        else:
            print(
                f"Error: UI port {ui_port} is already in use. "
                "Stop existing process or choose another --ui-port, or use --auto-ui-port.",
                file=sys.stderr,
            )
            return 1

    processes: list[subprocess.Popen] = []

    try:
        api_proc = _start_api(repo_root, args.host, api_port, args.reload)
        processes.append(api_proc)
        print(f"API running at http://{args.host}:{api_port}")

        if args.with_ui:
            api_url = f"http://{args.host if args.host != '0.0.0.0' else '127.0.0.1'}:{api_port}"
            ui_proc = _start_ui(repo_root, ui_port, api_url)
            processes.append(ui_proc)
            print(f"UI running at http://127.0.0.1:{ui_port}  (API → {api_url})")

        print("Press Ctrl+C to stop all started processes.")

        while True:
            time.sleep(1)
            for proc in processes:
                code = proc.poll()
                if code is not None:
                    print(f"A process exited with code {code}. Shutting down...")
                    _shutdown(processes)
                    return code
    except KeyboardInterrupt:
        print("\nStopping services...")
        _shutdown(processes)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
