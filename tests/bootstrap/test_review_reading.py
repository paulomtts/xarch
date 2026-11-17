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
SERVICE_SENT = len(SERVICE_BODY.replace("app.kernel.time", "<masked>"))
VALUES_SENT = len(VALUES_BODY.replace("docs@example.com", "person@example.test"))


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
        if "render_pdf" in body["state"] and "def publish" not in body["state"]:
            probabilities = {"services": 0.08, "logic": 0.92}
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
    assert lines[6:8] == [f"  {VALUES}   domain   0.12 (line 0.30)   {VALUES_SENT:,} chars, small",
                          f"      what to do: read it against the litmus of domain (`xarch where {VALUES}`). If the "
                          "litmus says it belongs, leave it. In trials, about 1 in 2 to 1 in 3 files read this way "
                          "was really misplaced."]
    assert f"  {SERVICE}   services   0.90 (line 0.30)   {SERVICE_SENT:,} chars" in lines
    assert lines[-3:] == ["parts (read this run)",
                          "  domain   1 file(s) read: too few to say anything of the part (fewer than 3)",
                          "  services   1 file(s) read: too few to say anything of the part (fewer than 3)"]
    assert "logic" not in result.output and KEY not in result.output
    (path, headers, body), _ = served.received
    assert (path, headers["Authorization"], body["model"]) == ("/v1/systemone", f"Bearer {KEY}", "jev-1.14.0")
    assert body["state"].startswith('"""Publishing documents."""\nfrom <masked> import Clock\n')
    assert SERVICE not in json.dumps(body) and KEY not in json.dumps(body)
    kept = sorted((tmp_path / ".xarch" / "cache" / "review").iterdir())
    assert len(kept) == 2 and all(KEY not in file.read_text() and "DocumentService" not in file.read_text()
                                  for file in kept)


def test_the_body_a_dry_run_shows_is_the_json_the_service_receives_for_the_same_file(served):
    dry = json.loads(review(SERVICE, VALUES, "--dry-run", "--format", "json", url=served.url).output)
    assert review(SERVICE, VALUES, url=served.url).exit_code == 0
    assert [json.loads(item["body"]) for item in dry["requests"]] == [body for _, _, body in served.received]
    assert [item["chars"] for item in dry["requests"]] == [len(body["state"]) for _, _, body in served.received]


@pytest.mark.parametrize("args", [
    pytest.param((SERVICE, VALUES, "--offline"), id="a review offline"),
    pytest.param((SERVICE, VALUES, "--dry-run"), id="a dry run"),
    pytest.param(("calibrate", "--offline"), id="a calibration offline"),
    pytest.param(("calibrate", "--dry-run"), id="a calibration's dry run"),
])
def test_offline_or_a_dry_run_sends_nothing_with_the_key_set_and_the_service_listening(served, args):
    review(*args, url=served.url)
    assert served.received == []


def test_the_request_goes_with_the_user_agent_xarch_and_no_other_header_of_the_project(served):
    assert review(SERVICE, url=served.url).exit_code == 0
    (_, headers, _), = served.received
    assert headers["User-Agent"] == "xarch"
    assert {name.lower() for name in headers} <= {"user-agent", "authorization", "content-type", "content-length",
                                                  "host", "accept-encoding", "connection"}


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
    assert (document["complete"], document["unanswered"]) == (False, [{"file": SERVICE, "why": "not-cached", "piece": None, "eval": None}])


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
    assert json.loads(document.output)["unanswered"] == [{"file": SERVICE, "why": "failed", "piece": None, "eval": None},
                                                          {"file": VALUES, "why": "failed", "piece": None, "eval": None}]
    assert KEY not in text.output + document.output
    assert len(server.received) == 2


def test_the_key_is_in_no_output_of_a_dry_run_or_a_refusal_when_it_is_set():
    runs = [review(SERVICE, "--dry-run"), review(SERVICE, "--dry-run", "--format", "json"),
            review(SERVICE, "--max-files", "0"), review("app/modules", "--max-files", "1"), review("--all", SERVICE),
            review(SERVICE, "--dry-run", "--profile", "nowhere.yaml")]
    assert [result.exit_code for result in runs] == [0, 0, 2, 2, 2, 2]
    assert all(KEY not in result.output for result in runs)
    assert "and the key is set now." in runs[0].output


def test_a_key_is_read_without_the_whitespace_around_it_and_one_of_whitespace_alone_is_no_key(served):
    assert review(SERVICE, key=f"  {KEY}\n", url=served.url).exit_code == 0
    assert [headers["Authorization"] for _, headers, _ in served.received] == [f"Bearer {KEY}"]
    unset = review(VALUES, key=" \n\t", url=served.url)
    assert unset.exit_code == 2 and "no key: set TYPESAFE_API_KEY" in unset.output
    assert len(served.received) == 1


@pytest.mark.parametrize("key", [
    pytest.param("sk-wired\nsecret-7f3a", id="a line break inside the key"),
    pytest.param("sk-wired\x07secret-7f3a", id="a control character"),
    pytest.param("sk-wired-sécret-7f3a", id="a letter outside ASCII"),
])
def test_a_key_a_header_cannot_carry_is_refused_with_exit_2_before_anything_is_sent_and_is_in_no_output(served, key):
    runs = [review(SERVICE, key=key, url=served.url), review(SERVICE, "--format", "json", key=key, url=served.url),
            review(SERVICE, "--dry-run", key=key, url=served.url),
            review("calibrate", "--eval", "placement", key=key, url=served.url)]
    assert [result.exit_code for result in runs] == [2, 2, 2, 2]
    assert ("TYPESAFE_API_KEY cannot be used: it holds a character a request header cannot carry; set it to the key "
            "alone") in runs[0].output
    assert json.loads(runs[1].output)["ok"] is False
    assert not any(part in result.output for result in runs for part in ("sk-wired", "7f3a"))
    assert served.received == []


def test_a_key_echoed_back_escaped_in_json_is_cut_from_what_the_decision_model_said():
    key = 'sk"wired\\secret-7f3a'
    server = ModelServer(401, f"bad key Bearer {key}")
    try:
        result = review(SERVICE, key=key, url=server.url)
    finally:
        server.stop()
    assert result.exit_code == 3 and "TypeSafe answered 401" in result.output
    assert "secret-7f3a" not in result.output


def test_a_cache_that_is_a_file_or_a_list_that_is_not_utf8_is_refused_with_exit_2_before_anything_is_sent(
        served, tmp_path):
    (tmp_path / "taken").write_text("not a folder")
    cached = review(SERVICE, "--cache", "taken", url=served.url)
    assert cached.exit_code == 2 and f"cannot keep answers in {tmp_path / 'taken'}: it is a file, not a folder" in (
        cached.output)
    (tmp_path / "list.txt").write_bytes(b"\xff\xfeapp\n")
    listed = review("--files-from", "list.txt", url=served.url)
    assert listed.exit_code == 2 and "the list given with --files-from is not UTF-8 text" in listed.output
    assert served.received == [] and (tmp_path / "taken").read_text() == "not a folder"


def test_an_answer_kept_through_a_link_is_never_read_nor_written_through(served, tmp_path):
    assert review(SERVICE, url=served.url).exit_code == 0
    (kept,) = (tmp_path / ".xarch" / "cache" / "review").iterdir()
    victim = tmp_path / "victim.txt"
    victim.write_text("precious")
    kept.unlink()
    kept.symlink_to(victim)
    assert review(SERVICE, url=served.url).exit_code == 0
    assert victim.read_text() == "precious" and not kept.is_symlink() and len(served.received) == 2


def test_an_unreachable_decision_model_leaves_the_files_unanswered_and_shows_no_key():
    result = review(SERVICE, "--format", "json", url="http://127.0.0.1:9")
    assert result.exit_code == 3
    document = json.loads(result.output)
    assert document["failure"].startswith("TypeSafe could not be reached") and KEY not in result.output


def test_a_line_the_profile_sets_for_a_part_is_the_one_its_files_are_read_against_and_is_said(served, tmp_path):
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "cli"]).exit_code == 0
    profile = tmp_path / "architecture" / "mine" / "mine.yaml"
    profile.write_text(profile.read_text() + "evals:\n  placement:\n    lines: {domain: 0.1}\n")
    result = review(SERVICE, VALUES, "--profile", str(profile), url=served.url)
    assert result.exit_code == 0, result.output
    assert (f"  {VALUES}   domain   0.12 (line 0.10, set by the profile)   {VALUES_SENT:,} chars, small   the mean "
            "of 3 orders of the options") in result.output.splitlines()
    orders = [list(body["questions"]["placement"]["criteria"]) for _, _, body in served.received
              if "Value0" in body["state"]]
    assert len(orders) == 3 and len({tuple(order) for order in orders}) == 3
    assert all(sorted(order) == sorted(orders[0]) for order in orders)
    assert "  no file judged reads as doubtful here" in result.output.splitlines()
    looser = runner.invoke(app, ["profile", "check", str(profile)]).output
    assert ("domain reads as doubtful only below 0.10, a lower line than the profile it is compared with gives it "
            "(evals.placement.lines)") in looser


def test_a_part_whose_files_read_low_across_the_board_is_summed_up_and_points_at_its_litmus_first(served, tmp_path):
    more = [f"app/modules/documents/domain/values_{n}.py" for n in (1, 2)]
    for n, path in enumerate(more, 1):
        (tmp_path / path).write_text(VALUES_BODY + f"\nEXTRA_{n} = {n}\n")
    result = review(SERVICE, VALUES, *more, url=served.url)
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[lines.index("parts (read this run)") + 1:] == [
        "  domain   3 files read   3 doubtful   line 0.30",
        "      3 of its 3 files read as doubtful, more than a quarter, which usually means its litmus does not describe "
        "them: read the litmus (`xarch where` on one of its files) before the files; if the litmus and the files are "
        "right, set evals.placement.lines.domain in the profile",
        "  services   1 file(s) read: too few to say anything of the part (fewer than 3)"]
    document = json.loads(review(SERVICE, VALUES, *more, "--offline", "--format", "json", key=None).output)
    assert document["placement"]["parts"][0] == {"part": "domain", "read": 3, "doubtful": 3, "line": 0.3,
                                                 "line_by_hand": False, "summed": True, "litmus_note": True,
                                                 "examples": None}



PIECED = "app/modules/documents/application/services/publishing.py"
PIECED_BODY = ('"""Publishing documents."""\nfrom app.kernel.time import Clock\n\n\n'
               + "def publish(clock: Clock) -> None:\n" + "    clock.now()\n" * 80 + "\n\n"
               + "def export(clock: Clock) -> None:\n" + "    render_pdf(clock)\n" * 60 + "\n\n"
               + "def archive(clock: Clock) -> None:\n" + "    clock.now()\n" * 70 + "\n\n"
               + "def tiny() -> None:\n    pass\n")


def test_with_pieces_the_pieces_of_a_file_are_ranked_inside_it_and_read_back_offline(served, tmp_path):
    (tmp_path / PIECED).write_text(PIECED_BODY)
    result = review(PIECED, "--pieces", url=served.url)
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    at = lines.index(f"pieces of {PIECED} (ranked inside this file only: the lowest 3 of 3 judged)")
    assert [line.split()[:3] for line in lines[at + 1:at + 4]] == [["1.", "export", "function"],
                                                                     ["2.", "publish", "function"],
                                                                     ["3.", "archive,", "tiny"]]
    assert lines[at + 1].startswith("  1. export   function   lines 88-148   0.08   ")
    asked = [body["questions"]["placement"]["instructions"] for _, _, body in served.received]
    assert sum(ask.endswith("This text is one piece of a larger file.") for ask in asked) == 3
    assert all(not body["state"].startswith('"""Publishing') for _, _, body in served.received[1:])
    document = json.loads(review(PIECED, "--pieces", "--offline", "--format", "json", key=None).output)
    (pieces,) = document["pieces"]
    assert [(item["rank"], item["name"], item["kind"]) for item in pieces["lowest"]] == [
        (1, "export", "function"), (2, "publish", "function"), (3, "archive, tiny", "function")]
    assert (pieces["judged"], pieces["too_small"], pieces["context"], pieces["answered"]) == (3, 0, "none", True)
    assert pieces["lowest"][0]["distribution"] == {"services": 0.08, "logic": 0.92} | {
        part: 0.0 for part in pieces["lowest"][0]["distribution"] if part not in ("services", "logic")}
    assert "logic" not in result.output


def test_a_dry_run_with_pieces_shows_each_piece_request_it_would_send_and_context_sends_the_opening_lines(tmp_path):
    (tmp_path / PIECED).write_text(PIECED_BODY)
    result = review(PIECED, "--pieces", "--dry-run", key=None)
    assert result.exit_code == 0, result.output
    assert f"request 2 of 4: {PIECED} piece publish (function, lines 5-85, services, " in result.output
    assert f"request 4 of 4: {PIECED} piece archive, tiny (function, lines 151-225, services, " in result.output
    with_context = json.loads(review(PIECED, "--pieces", "--context", "imports", "--dry-run", "--format", "json",
                                     key=None).output)
    texts = [item["text"] for item in with_context["requests"] if item["piece"]]
    assert len(texts) == 3 and all(text.startswith('"""Publishing documents."""\nfrom <masked> import Clock\n')
                                   for text in texts)
    assert with_context["context"] == "imports" and with_context["pieces"] is True


def test_every_file_of_the_app_in_pieces_is_refused_with_exit_2():
    result = review("--all", "--pieces", key=None)
    assert result.exit_code == 2
    assert "--pieces ranks the pieces of files already chosen, never of every file" in result.output
