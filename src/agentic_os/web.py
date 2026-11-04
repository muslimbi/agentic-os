from __future__ import annotations

import argparse
import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .core import HierarchicalAgentOS

_DASHBOARD_PATH = Path(__file__).parent / "static" / "dashboard.html"
_MAX_REQUEST_BYTES = 1_048_576


def create_handler(system: HierarchicalAgentOS) -> type[BaseHTTPRequestHandler]:
    state_lock = threading.RLock()

    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = urlsplit(self.path).path
            if path == "/":
                try:
                    content = _DASHBOARD_PATH.read_bytes()
                except OSError:
                    self._send_json(
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        {"error": "Dashboard page could not be loaded."},
                    )
                    return
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(content)
                return
            if path == "/api/dashboard":
                with state_lock:
                    dashboard = system.dashboard()
                self._send_json(HTTPStatus.OK, dashboard)
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

        def do_POST(self) -> None:
            path = urlsplit(self.path).path
            if path not in {"/api/goals", "/api/companies"}:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
                return
            try:
                length = int(self.headers.get("Content-Length", ""))
                if length < 0 or length > _MAX_REQUEST_BYTES:
                    raise ValueError("Request body must be at most 1 MiB.")
                payload: Any = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("Expected a JSON object.")
                if path == "/api/companies":
                    with state_lock:
                        company = system.add_company(payload.get("name"))
                    self._send_json(HTTPStatus.CREATED, company)
                    return
                goal = payload.get("goal")
                tasks = payload.get("tasks")
                company = payload.get("company")
                if tasks is not None and not isinstance(tasks, list):
                    raise ValueError("Tasks must be a JSON array.")
                with state_lock:
                    run = system.submit_goal(goal, tasks or None, company)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})
                return
            self._send_json(
                HTTPStatus.CREATED,
                {
                    "goal_id": run.goal_id,
                    "status": run.status,
                    "company_id": run.company_id,
                    "company_name": run.company_name,
                    "tasks": run.tasks,
                },
            )

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
            content = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

    return DashboardHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Serve the local Agentic OS dashboard."
    )
    parser.add_argument("--port", type=int, default=8765, help="Local port to use.")
    args = parser.parse_args(argv)
    if not 0 < args.port < 65536:
        parser.error("--port must be between 1 and 65535.")

    server = ThreadingHTTPServer(
        ("127.0.0.1", args.port), create_handler(HierarchicalAgentOS())
    )
    print(f"Agentic OS dashboard running at http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Agentic OS dashboard.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
