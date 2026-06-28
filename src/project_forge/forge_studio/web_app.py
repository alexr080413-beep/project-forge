from __future__ import annotations

import argparse
import json
import mimetypes
from dataclasses import asdict, is_dataclass
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .mock_data import create_mock_registry, create_mock_workspace
from .models import InjectStatus, StudioReviewStatus, UserRole
from .registry import ForgeStudioRegistry


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def build_dashboard_payload(registry: ForgeStudioRegistry) -> dict[str, Any]:
    """Build the local workspace payload from Forge Studio MVP models."""

    workspace = create_mock_workspace()
    exercises = registry.list_exercises()
    active_exercise = exercises[0] if exercises else None
    exercise_id = active_exercise.id if active_exercise else None
    review_items = registry.list_review_items(exercise_id)
    injects = registry.list_injects(exercise_id)
    timeline_events = registry.list_timeline_events(exercise_id)
    users = registry.list_users()
    active_inject_statuses = {
        InjectStatus.PENDING_REVIEW,
        InjectStatus.APPROVED,
        InjectStatus.SCHEDULED,
    }
    controller_roles = {
        UserRole.EXERCISE_DIRECTOR,
        UserRole.INTELLIGENCE_CHIEF,
        UserRole.EXERCISE_CONTROL_OFFICER,
        UserRole.CONTROLLER,
        UserRole.REVIEWER,
        UserRole.ADMINISTRATOR,
    }
    pending_statuses = {StudioReviewStatus.PENDING, StudioReviewStatus.IN_REVIEW}
    timeline_summary = sorted(timeline_events, key=lambda item: item.timestamp)
    open_injects = [item for item in injects if item.status is not InjectStatus.COMPLETED]
    products_generated = _stat_value(workspace["exercise"]["statistics"], "Products")

    return {
        "active_exercise": _to_jsonable(active_exercise) if active_exercise else None,
        "workspace": workspace,
        "metrics": {
            "exercise_status": workspace["exercise"]["status"],
            "exercise_phase": workspace["exercise"]["phase"],
            "exercise_health": workspace["exercise"]["health"],
            "current_operational_time": workspace["exercise"]["operational_time"],
            "pending_reviews": sum(item.status in pending_statuses for item in review_items),
            "open_injects": len(open_injects),
            "active_injects": sum(item.status in active_inject_statuses for item in injects),
            "products_generated": products_generated,
            "timeline_events": len(timeline_events),
            "controller_count": sum(user.role in controller_roles and user.active for user in users),
        },
        "activity": workspace["activity"],
        "timeline_summary": [_to_jsonable(event) for event in timeline_summary],
        "pending_reviews": [
            _to_jsonable(item) for item in review_items if item.status in pending_statuses
        ],
        "injects": [_to_jsonable(item) for item in injects],
        "active_injects": [_to_jsonable(item) for item in open_injects],
        "controllers": [_to_jsonable(user) for user in users if user.role in controller_roles],
    }


def create_handler(registry: ForgeStudioRegistry) -> type[SimpleHTTPRequestHandler]:
    static_root = resources.files("project_forge.forge_studio").joinpath("static")
    repository_root = Path(__file__).resolve().parents[3]
    logo_path = repository_root / "assets" / "forge-logo.png"

    class ForgeStudioRequestHandler(SimpleHTTPRequestHandler):
        server_version = "ForgeStudioMVP/0.1"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler method
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/api/dashboard":
                self._send_json(build_dashboard_payload(registry))
                return
            if path == "/assets/forge-logo.png":
                self._send_file(logo_path)
                return
            if path in {"/", "/index.html"}:
                self._send_file(Path(static_root) / "index.html")
                return
            self._send_static(path)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send_static(self, path: str) -> None:
            relative = path.lstrip("/")
            candidate = (Path(static_root) / relative).resolve()
            root = Path(static_root).resolve()
            if not candidate.is_file() or root not in candidate.parents:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self._send_file(candidate)

        def _send_json(self, payload: dict[str, Any]) -> None:
            content = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def _send_file(self, path: Path) -> None:
            if not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            content = path.read_bytes()
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    return ForgeStudioRequestHandler


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    registry = create_mock_registry()
    handler = create_handler(registry)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Forge Studio MVP running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nForge Studio MVP stopped.")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Forge Studio MVP web app.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if is_dataclass(value):
        return {key: _to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


def _stat_value(statistics: object, label: str) -> int:
    if not isinstance(statistics, list):
        return 0
    for item in statistics:
        if not isinstance(item, dict):
            continue
        if item.get("label") == label:
            try:
                return int(str(item.get("value", "0")))
            except ValueError:
                return 0
    return 0


if __name__ == "__main__":
    main()
