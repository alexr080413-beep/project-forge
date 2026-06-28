from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .data_engine import ExerciseStore, create_mock_exercise_store
from .registry import ForgeStudioRegistry


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def build_dashboard_payload(
    store: ExerciseStore | ForgeStudioRegistry | None = None,
) -> dict[str, Any]:
    """Build the local workspace payload from the shared exercise store."""

    if isinstance(store, ForgeStudioRegistry):
        store = create_mock_exercise_store(registry=store)
    return (store or create_mock_exercise_store()).snapshot()


def create_handler(store: ExerciseStore) -> type[SimpleHTTPRequestHandler]:
    static_root = resources.files("project_forge.forge_studio").joinpath("static")
    repository_root = Path(__file__).resolve().parents[3]
    logo_path = repository_root / "assets" / "forge-logo.png"

    class ForgeStudioRequestHandler(SimpleHTTPRequestHandler):
        server_version = "ForgeStudioMVP/0.1"

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler method
            parsed = urlparse(self.path)
            path = parsed.path
            if path in {"/api/dashboard", "/api/exercise"}:
                self._send_json(build_dashboard_payload(store))
                return
            if path == "/assets/forge-logo.png":
                self._send_file(logo_path)
                return
            if path in {"/", "/index.html"}:
                self._send_file(Path(static_root) / "index.html")
                return
            self._send_static(path)

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler method
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                body = self._read_json_body()
                review_id = str(body.get("review_id", "")).strip()
                if path == "/api/action":
                    action = str(body.get("action", "")).strip()
                    payload = body.get("payload", {})
                    if not isinstance(payload, dict):
                        raise ValueError("payload must be a JSON object")
                    self._send_json(store.apply_action(action, payload))
                    return
                if path == "/api/review/approve":
                    self._send_json(store.approve_review(review_id))
                    return
                if path == "/api/review/reject":
                    self._send_json(store.reject_review(review_id))
                    return
                self.send_error(HTTPStatus.NOT_FOUND)
            except (KeyError, TypeError, ValueError) as error:
                self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)

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

        def _send_json(
            self,
            payload: dict[str, Any],
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            content = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
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

        def _read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("request body must be a JSON object")
            return body

    return ForgeStudioRequestHandler


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    store = create_mock_exercise_store()
    handler = create_handler(store)
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


if __name__ == "__main__":
    main()
