"""xarch review that reads, on a project `init` and `new` made, against a decision model served on this machine, never
the network: what it sends (the masked text, the question, the key as the Authorization header only), the reading it
prints ranked as text and as JSON, the answers it keeps in the project's cache and reads back with --offline, a file
with no answer (exit 3), and the key in no output of any run, a refusal or a failure of the decision model."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers
from xarch.cli.app import build

runner = CliRunner()
KEY = "sk-wired-secret-7f3a"
SERVICE = "app/modules/documents/application/services/document_service.py"
VALUES = "app/modules/documents/domain/values.py"
SERVICE_BODY = ('"""Publishing documents."""\nfrom app.kernel.time import Clock\n\n\nclass DocumentService:\n'
                + "".join(f"    def step_{n}(self, clock: Clock) -> None:\n        clock.now()\n\n" for n in range(30)))
VALUES_BODY = ('"""The values of a document; mail docs@example.com."""\nfrom dataclasses import dataclass\n\n\n'
               + "".join(f"@dataclass(frozen=True)\nclass Value{n}:\n    text: str\n\n\n" for n in range(25)))


class ModelServer:
    """A decision model on this machine: it answers each question with a status and a body chosen by the text sent,
    and keeps every request it was sent."""

    def __init__(self, status: int = 200, detail: object = None):
        self.status, self.detail, self.received = status, detail, []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                owner.received.append((self.path, dict(self.headers), body))
                answer = owner.answer(body) if owner.status == 200 else {"detail": owner.detail}
                payload = json.dumps(answer).encode()
                self.send_response(owner.status)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    @staticmethod
    def answer(body: dict) -> dict:
        own = "domain" if "Value0" in body["state"] else "services"
        probabilities = {own: 0.9, "logic": 0.1} if own == "services" else {own: 0.12, "logic": 0.88}
        return {"model": "jev-1.14.0", "usage": {"input_tokens": 2500, "output_tokens": 4},
                "answers": {name: {"type": "choice", "choice": max(probabilities, key=probabilities.get),
                                   "confidence": 0.8, "probabilities": probabilities} for name in body["questions"]}}

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "cli"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "documents"]).exit_code == 0
    (tmp_path / SERVICE).write_text(SERVICE_BODY)
    (tmp_path / VALUES).write_text(VALUES_BODY)


@pytest.fixture
def served():
    server = ModelServer()
    yield server
    server.stop()


def review(*args: str, key: str | None = KEY, url: str = "http://127.0.0.1:9"):
    controllers = build_controllers({} if key is None else {"TYPESAFE_API_KEY": key}, url)
    keyed = build(controllers.rules, controllers.scaffold, controllers.spec, controllers.review, lambda: None)
    return runner.invoke(keyed, ["review", *args])


def test_a_review_sends_the_masked_text_and_the_question_with_the_key_as_the_header_alone_and_prints_its_reading(
        served, tmp_path):
    result = review(SERVICE, VALUES, url=served.url)
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[1] == "Model jev-1.14.0. 2 file(s) found (paths), 2 judged, 0 left out. Asked 2, from cache 0."
    assert lines[2] == f"Sent 2 request(s) to TypeSafe ({served.url}): 5,000 input tokens, 8 output tokens."
    assert lines[6:8] == [f"  {VALUES}   domain   0.12 (line 0.30)   {len(VALUES_BODY):,} chars",
                          f"      what to do: read it against the litmus of domain (`xarch where {VALUES}`). If the "
                          "litmus says it belongs, leave it. In trials, about 1 in 2 to 1 in 3 files read this way "
                          "was really misplaced."]
    assert f"  {SERVICE}   services   0.90 (line 0.30)   {len(SERVICE_BODY):,} chars" in lines
    assert "logic" not in result.output and KEY not in result.output
    (path, headers, body), _ = served.received
    assert (path, headers["Authorization"], body["model"]) == ("/v1/systemone", f"Bearer {KEY}", "jev-1.14.0")
    assert body["state"].startswith('"""Publishing documents."""\nfrom <masked> import Clock\n')
    assert SERVICE not in json.dumps(body) and KEY not in json.dumps(body)
    kept = sorted((tmp_path / ".xarch" / "cache" / "review").iterdir())
    assert len(kept) == 2 and all(KEY not in file.read_text() and "DocumentService" not in file.read_text()
                                  for file in kept)


def test_answers_kept_are_read_back_offline_with_no_key_and_nothing_is_sent(served):
    assert review(SERVICE, VALUES, url=served.url).exit_code == 0
    offline = review(SERVICE, VALUES, "--offline", "--format", "json", key=None, url=served.url)
    assert offline.exit_code == 0, offline.output
    document = json.loads(offline.output)
    assert (document["complete"], document["sent"]) == (True, {"calls": 0, "cached": 2, "input_tokens": 0,
                                                              "output_tokens": 0})
    assert [(item["file"], item["doubtful"]) for item in document["placement"]["files"]] == [(VALUES, True),
                                                                                           (SERVICE, False)]
    assert document["placement"]["files"][0]["distribution"] == {"domain": 0.12, "logic": 0.88} | {
        part: 0.0 for part in document["placement"]["files"][0]["distribution"] if part not in ("domain", "logic")}
    again = review(SERVICE, VALUES, url=served.url)
    assert again.output.splitlines()[1].endswith("Asked 0, from cache 2.")
    assert len(served.received) == 2


def test_offline_a_file_whose_answer_is_not_kept_is_unanswered_and_the_run_exits_3(tmp_path):
    result = review(SERVICE, "--offline", key=None)
    assert result.exit_code == 3, result.output
    assert f"  {SERVICE}: not in the cache, and --offline sends nothing" in result.output.splitlines()
    document = json.loads(review(SERVICE, "--offline", "--format", "json", key=None).output)
    assert (document["complete"], document["unanswered"]) == (False, [{"file": SERVICE, "why": "not-cached"}])


def test_a_cache_folder_given_is_the_one_written_and_read(served, tmp_path):
    assert review(SERVICE, "--cache", "kept", url=served.url).exit_code == 0
    assert len(list((tmp_path / "kept").iterdir())) == 1 and not (tmp_path / ".xarch").exists()
    assert review(SERVICE, "--cache", "kept", "--offline", key=None).exit_code == 0


def test_with_no_key_a_review_that_would_send_is_refused_with_exit_2_and_sends_nothing(served):
    result = review(SERVICE, key=None, url=served.url)
    assert result.exit_code == 2
    assert ("no key: set TYPESAFE_API_KEY, or run --dry-run to see what would be sent, or --offline to use cached "
            "answers only") in result.output
    assert served.received == []


@pytest.mark.parametrize("status, detail", [
    pytest.param(401, f"Invalid API key {KEY}", id="a key refused and echoed back"),
    pytest.param(422, [{"loc": ["body", KEY], "msg": f"bad {KEY}", "type": "x"}], id="a request refused naming the key"),
    pytest.param(502, KEY, id="a failure the documentation does not describe, echoing the key"),
])
def test_a_failure_of_the_decision_model_leaves_the_rest_unanswered_exits_3_and_shows_no_key(status, detail):
    server = ModelServer(status, detail)
    try:
        text = review(SERVICE, VALUES, url=server.url)
        document = review(SERVICE, VALUES, "--format", "json", url=server.url)
    finally:
        server.stop()
    assert (text.exit_code, document.exit_code) == (3, 3)
    assert f"  the decision model said: TypeSafe answered {status}" in text.output
    assert json.loads(document.output)["unanswered"] == [{"file": SERVICE, "why": "failed"},
                                                          {"file": VALUES, "why": "failed"}]
    assert KEY not in text.output + document.output
    assert len(server.received) == 2


def test_the_key_is_in_no_output_of_a_dry_run_or_a_refusal_when_it_is_set():
    runs = [review(SERVICE, "--dry-run"), review(SERVICE, "--dry-run", "--format", "json"),
            review(SERVICE, "--max-files", "0"), review("app/modules", "--max-files", "1"), review("--all", SERVICE),
            review(SERVICE, "--dry-run", "--profile", "nowhere.yaml")]
    assert [result.exit_code for result in runs] == [0, 0, 2, 2, 2, 2]
    assert all(KEY not in result.output for result in runs)
    assert "and the key is set now." in runs[0].output


def test_an_unreachable_decision_model_leaves_the_files_unanswered_and_shows_no_key():
    result = review(SERVICE, "--format", "json", url="http://127.0.0.1:9")
    assert result.exit_code == 3
    document = json.loads(result.output)
    assert document["failure"].startswith("TypeSafe could not be reached") and KEY not in result.output
