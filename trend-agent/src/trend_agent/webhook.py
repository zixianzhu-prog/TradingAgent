from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .database import connect, insert_articles
from .feeds import article_from_change


def handler(database_path: str) -> type[BaseHTTPRequestHandler]:
    class ChangeHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                connection = connect(database_path)
                inserted, duplicates = insert_articles(connection, [article_from_change(payload)])
                connection.close()
                body = json.dumps({"inserted": inserted, "duplicates": duplicates}).encode("utf-8")
                self.send_response(200)
            except (ValueError, json.JSONDecodeError) as exc:
                body = json.dumps({"error": str(exc)}).encode("utf-8")
                self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return ChangeHandler


def serve(database_path: str, host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), handler(database_path))
    print(f"Listening for changedetection.io webhooks on http://{host}:{port}")
    server.serve_forever()
