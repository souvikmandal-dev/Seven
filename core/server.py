import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

from Brain import Brain


HOST = "127.0.0.1"
PORT = 8000
MAX_MESSAGE_LENGTH = 10_000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_DIRECTORY = PROJECT_ROOT / "ui"

brain = Brain()
brain_lock = Lock()


class SevenRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIRECTORY), **kwargs)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found.")
            return

        if self.headers.get_content_type() != "application/json":
            self.send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {
                "error": "Content-Type must be application/json."
            })
            return

        content_length = self.headers.get("Content-Length")

        try:
            content_length = int(content_length)
        except (TypeError, ValueError):
            self.send_json(HTTPStatus.BAD_REQUEST, {
                "error": "A valid request body is required."
            })
            return

        if content_length > MAX_MESSAGE_LENGTH:
            self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {
                "error": "Messages must be 10,000 characters or fewer."
            })
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(HTTPStatus.BAD_REQUEST, {
                "error": "The request body must contain valid JSON."
            })
            return

        user_input = payload.get("message") if isinstance(payload, dict) else None

        if not isinstance(user_input, str) or not user_input.strip():
            self.send_json(HTTPStatus.BAD_REQUEST, {
                "error": "Please provide a message for Seven."
            })
            return

        if len(user_input) > MAX_MESSAGE_LENGTH:
            self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {
                "error": "Messages must be 10,000 characters or fewer."
            })
            return

        with brain_lock:
            response = brain.talk(user_input.strip())

        self.send_json(HTTPStatus.OK, {"response": response})

    def send_json(self, status, payload):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(response)


def run_server():
    if not UI_DIRECTORY.is_dir():
        raise RuntimeError(f"UI directory not found: {UI_DIRECTORY}")

    server = ThreadingHTTPServer((HOST, PORT), SevenRequestHandler)
    print(f"Seven UI is running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSeven UI server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
