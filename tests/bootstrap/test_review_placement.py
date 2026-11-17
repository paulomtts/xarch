"""xarch review calibrate --eval placement on a project `init --profile cli` made: placement held to the bundled
profile's own examples. The answers are a recording built from a fake's table (each example read on its own part),
served on this machine and kept in the project's cache, never the network; calibrate then reads them offline, and an
example whose answer the recording does not hold is named. A real recording of the bundled examples is the owner's."""
import io
import json
import threading
import tokenize
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xarch as xarch_package
from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers
from xarch.cli.app import build

runner = CliRunner()
KEY = "sk-wired-secret-41b2"
ON_ITS_PART = 0.85
"""What the fake's table puts on the part an example lies in."""


class Recording:
    """A decision model on this machine that answers from a table, the probability on each part by the text sent,
    and keeps every text it was sent."""

    def __init__(self, table: dict[str, dict[str, float]]):
        self.table, self.sent = table, []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                owner.sent.append(body["state"])
                probabilities = owner.table[body["state"]]
                answers = {name: {"type": "choice", "choice": max(probabilities, key=probabilities.get),
                                  "confidence": 0.9, "probabilities": probabilities} for name in body["questions"]}
                payload = json.dumps({"model": "jev-1.14.0", "usage": {"input_tokens": 1, "output_tokens": 1},
                                      "answers": answers}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def xarch(*args: str, key: str | None = KEY, url: str = "http://127.0.0.1:9"):
    controllers = build_controllers({} if key is None else {"TYPESAFE_API_KEY": key}, url)
    keyed = build(controllers.rules, controllers.scaffold, controllers.spec, controllers.review, lambda: None)
    return runner.invoke(keyed, list(args))


def table(planned: dict) -> dict[str, dict[str, float]]:
    """The fake's table: each example read mostly on the part it lies in, the rest shared by the other parts."""
    parts = json.loads(planned["requests"][0]["body"])["questions"]["placement"]["criteria"]
    rest = (1 - ON_ITS_PART) / (len(parts) - 1)
    return {item["text"]: {part: ON_ITS_PART if part == item["part"] else rest for part in parts}
            for item in planned["requests"]}


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "cli"]).exit_code == 0


@pytest.fixture
def recorded():
    planned = json.loads(xarch("review", "calibrate", "--eval", "placement", "--dry-run", "--format", "json").output)
    server = Recording(table(planned))
    assert xarch("review", "calibrate", "--eval", "placement", url=server.url).exit_code == 0
    yield planned, server
    server.stop()


def test_placement_is_held_to_every_bundled_example_in_a_part_and_each_part_with_one_agrees_on_the_recording(recorded):
    planned, server = recorded
    assert planned["evals"] == ["placement"] and len(planned["requests"]) == len(server.sent) > 20
    result = xarch("review", "calibrate", "--eval", "placement", "--offline", key=None)
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[1] == f"Model jev-1.14.0. Asked 0, from cache {len(server.sent)}."
    assert not any("examples disagree" in line for line in lines)
    assert "  services   passed (1 example(s) of its own)" in lines
    review = xarch("review", "app", "--offline", "--format", "json", key=None)
    assert json.loads(review.output)["placement"]["calibration"]["examples"]["state"] == "calibrated"


def test_an_example_whose_answer_the_recording_does_not_hold_is_named_and_nothing_of_placement_is_recorded_anew(
        recorded, tmp_path):
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "cli"]).exit_code == 0
    example = tmp_path / "architecture/mine/examples/shared/modules/documents/domain/values.py"
    example.write_text(example.read_text() + "\n")
    result = xarch("review", "calibrate", "--eval", "placement", "--offline", "--profile",
                   "architecture/mine/mine.yaml", key=None)
    assert result.exit_code == 3
    assert ("  placement: clean example modules/documents/domain/values.py: not in the cache, and --offline sends nothing"
            in result.output.splitlines())


def bundled_comments() -> set[str]:
    """The text of every comment of the bundled example files, as the language's own tokens find them."""
    found: set[str] = set()
    for path in (Path(xarch_package.__file__).parent / "architectures" / "examples").rglob("*.py"):
        tokens = tokenize.generate_tokens(io.StringIO(path.read_text(encoding="utf-8")).readline)
        found |= {token.string for token in tokens if token.type == tokenize.COMMENT}
    return found


def test_no_comment_of_a_bundled_example_is_in_what_placement_s_dry_run_shows_nor_in_what_the_service_receives(
        recorded):
    planned, server = recorded
    comments = bundled_comments()
    assert len(comments) > 40
    shown = [item["text"] for item in planned["requests"]]
    assert planned["masked"] == ["own-imports", "e-mail", "comments"]
    assert [item["chars"] for item in planned["requests"]] == [len(text) for text in shown]
    assert sorted(server.sent) == sorted(shown)
    assert not [(comment, text) for comment in comments for text in shown + server.sent if comment in text]
