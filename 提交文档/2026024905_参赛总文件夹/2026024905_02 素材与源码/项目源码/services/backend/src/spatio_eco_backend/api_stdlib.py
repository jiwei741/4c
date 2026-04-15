from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import service


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "SpatioEcoHTTP/0.1"

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            if path == "/api/v1/health":
                payload = service.get_health()
            elif path == "/api/v1/dashboard":
                payload = service.get_dashboard()
            elif path == "/api/v1/data-sources":
                payload = service.get_data_sources()
            elif path == "/api/v1/admin/platform-status":
                payload = service.get_platform_status()
            elif path == "/api/v1/architecture":
                payload = {"items": service.get_dashboard()["architecture"]}
            elif path == "/api/v1/study-area/grid-nodes":
                payload = service.get_grid_nodes()
            elif path == "/api/v1/members":
                payload = {"items": service.get_dashboard()["members"]}
            elif path == "/api/v1/models":
                payload = {"items": service.list_models()}
            elif path == "/api/v1/evidence/summary":
                payload = service.get_evidence_summary()
            elif path == "/api/v1/assistant/faq":
                self._send_json({"error": "method_not_allowed", "path": path}, status=405)
                return
            elif path.startswith("/api/v1/models/"):
                model_key = path.split("/")[-1]
                payload = service.get_model(model_key)
            elif path == "/api/v1/predictions/latest":
                model_key = query.get("model_key", [None])[0]
                payload = service.get_prediction_payload(model_key)
            elif path == "/api/v1/map/predictions":
                model_key = query.get("model_key", [None])[0]
                horizon = query.get("horizon", [None])[0]
                payload = service.get_prediction_layer(model_key, horizon)
            elif path == "/api/v1/map/analytics":
                model_key = query.get("model_key", [None])[0]
                horizon = query.get("horizon", [None])[0]
                compare_model_key = query.get("compare_model_key", [None])[0]
                payload = service.get_prediction_analytics(model_key, horizon, compare_model_key)
            elif path == "/api/v1/scenarios/examples":
                payload = {"items": service.list_scenarios()}
            elif path.startswith("/api/v1/scenarios/examples/"):
                scenario_key = path.split("/")[-1]
                payload = service.get_scenario_example(scenario_key)
            else:
                self._send_json({"error": "not_found", "path": path}, status=404)
                return
        except KeyError as exc:
            self._send_json({"error": "not_found", "detail": str(exc)}, status=404)
            return

        self._send_json(payload)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/v1/scenarios/run":
            payload = service.run_scenario(self._read_json_body())
            self._send_json(payload, status=202)
            return

        if parsed.path == "/api/v1/assistant/faq":
            payload = service.get_faq_assistant_reply(self._read_json_body())
            self._send_json(payload)
            return

        if parsed.path != "/api/v1/scenarios/run":
            self._send_json({"error": "not_found", "path": parsed.path}, status=404)
            return


def run() -> None:
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), ApiHandler)
    print(f"Spatio-Eco backend fallback server listening on http://{host}:{port}")
    server.serve_forever()
