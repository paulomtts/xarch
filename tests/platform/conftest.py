"""A local HTTP server for the clients under test: it answers each request with the next scripted reply and records
what it was sent, so no test reaches the network."""
import json
import socket
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


@dataclass(frozen=True)
class Reply:
    status: int = 200
    body: object = None
    headers: dict = field(default_factory=dict)
    raw: bytes | None = None
    stall: bool = False


@dataclass(frozen=True)
class Received:
    method: str
    path: str
    headers: dict
    body: bytes


class ScriptedServer:
    def __init__(self):
        self.replies: list[Reply] = []
        self.requests: list[Received] = []
        self.release = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def _answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                owner.requests.append(Received(self.command, self.path, {k.lower(): v for k, v in self.headers.items()},
                                               self.rfile.read(length)))
                reply = owner.replies.pop(0) if owner.replies else Reply(500, {"detail": "nothing scripted"})
                if reply.stall:
                    owner.release.wait(5)
                    return
                payload = reply.raw if reply.raw is not None else json.dumps(reply.body).encode()
                self.send_response(reply.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                for name, value in reply.headers.items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = _answer

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.httpd.daemon_threads = True
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()

    def script(self, *replies: Reply) -> None:
        self.replies.extend(replies)

    def stop(self) -> None:
        self.release.set()
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def server():
    scripted = ScriptedServer()
    yield scripted
    scripted.stop()


@pytest.fixture
def unused_url():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}"
