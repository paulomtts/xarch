"""xarch review calibrate and the evals of the profile's own, on a project `init` made with a copy of the cli profile
holding one eval of each answer form, against a decision model served on this machine, never the network: an eval
does not run until it is calibrated, and the review says what to run; calibrate holds each to its examples and
records the verdicts; the review then runs them, offline from the cache too; and an eval changed since is stale."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers
from xarch.cli.app import build

runner = CliRunner()
KEY = "sk-wired-secret-9c1d"
COPY = "architecture/mine/mine.yaml"
SERVICE = "app/modules/documents/application/services/publishing.py"
DECIDES = ("from app.kernel.time import Clock\n\n\nclass PublishingService:\n    def publish(self, doc) -> None:\n"
           "        if not doc.title.strip():\n            raise ValueError(doc)\n        doc.published_at = 1\n")
ASKS = "class PublishingService:\n    def publish(self, doc) -> None:\n        doc.publish()\n"
NOW = "from datetime import datetime\n\n\ndef stale(doc) -> bool:\n    return datetime.now() > doc.due\n"
PURE = "def stale(doc, now) -> bool:\n    return now > doc.due\n"
SENDS = "from typing import Protocol\n\n\nclass Export(Protocol):\n    def send(self, doc, to: str) -> None: ...\n"
FINDS = "from typing import Protocol\n\n\nclass Finder(Protocol):\n    def find(self, title: str) -> list: ...\n"
SERVICE_BODY = ('"""Publishing documents: a long enough use case to be judged by placement and by the evals."""\n'
                + DECIDES + "".join(f"\n    def step_{n}(self) -> None:\n        return None\n" for n in range(25)))


def examples(flagged: str, clean: str, folder: str) -> dict:
    return {"flagged": {f"modules/documents/application/{folder}/a.py": flagged,
                        f"modules/documents/application/{folder}/b.py": flagged + "\n"},
            "clean": {f"modules/documents/application/{folder}/a.py": clean,
                      f"modules/documents/application/{folder}/b.py": clean + "\n"}}


EVALS = {
    "rule-outside-entity": {
        "ask": "Does this method itself decide whether a document may change, by testing its fields?",
        "answer": "yes-no", "yes": "it tests the document's fields", "no": "it asks the document",
        "reads": "function", "in": {"part": "services"}, "keep": ["public"],
        "message": "{name} may decide a rule of a document itself ({value})",
        "fix": "read it against the litmus of domain/", "examples": examples(DECIDES, ASKS, "services")},
    "logic-purity": {
        "ask": "How much of this function's work reads or writes something outside its arguments?",
        "answer": {"score": ["none", "a constant of its own", "a constant of another", "the clock or a file",
                             "it writes"], "flagged_from": 3},
        "reads": "function", "in": {"part": "logic"}, "message": "{name} may reach outside ({value})",
        "fix": "read it against the litmus of logic/", "examples": examples(NOW, PURE, "logic")},
    "document-sender": {
        "ask": "What does this port let its caller do with a document?",
        "answer": {"choice": {"finds": "it finds documents", "saves": "it saves documents",
                              "sends": "it sends documents out"}, "flagged": ["sends"]},
        "reads": "class", "in": {"part": "ports"}, "message": "{name} may send documents out ({value})",
        "fix": "read it against the litmus of ports/", "examples": examples(SENDS, FINDS, "ports")}}


class ModelServer:
    """A decision model on this machine: a yes or no reads yes where the text tests a title, a score reads level 3
    where it reads the clock, a choice reads `sends` where the text sends; it keeps every request it was sent."""

    def __init__(self):
        self.received = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                owner.received.append(body)
                payload = json.dumps(owner.answer(body)).encode()
                self.send_response(200)
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
        state, answers = body["state"], {}
        for name, question in body["questions"].items():
            if question["type"] == "noul":
                answers[name] = {"type": "noul", "noul": 0.9 if "title" in state else 0.1}
            elif question["type"] == "score":
                level = "3" if "now()" in state else "0"
                answers[name] = {"type": "score", "score": int(level), "confidence": 0.9, "legend": {},
                                 "probabilities": {level: 1.0}}
            else:
                options = list(question["criteria"])
                chosen = "sends" if "sends" in options and "def send" in state else sorted(options)[0]
                answers[name] = {"type": "choice", "choice": chosen, "confidence": 0.9,
                                 "probabilities": {option: 0.9 if option == chosen else 0.1 / (len(options) - 1)
                                                   for option in options}}
        return {"model": "jev-1.14.0", "usage": {"input_tokens": 100, "output_tokens": 2}, "answers": answers}

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "cli"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "documents"]).exit_code == 0
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "cli"]).exit_code == 0
    document = yaml.safe_load((tmp_path / COPY).read_text())
    document["evals"] = EVALS
    (tmp_path / COPY).write_text(yaml.safe_dump(document, sort_keys=False))
    (tmp_path / "pyproject.toml").write_text(f'[tool.xarch]\nprofile = "{COPY}"\n')
    (tmp_path / SERVICE).write_text(SERVICE_BODY)


@pytest.fixture
def served():
    server = ModelServer()
    yield server
    server.stop()


def xarch(*args: str, key: str | None = KEY, url: str = "http://127.0.0.1:9"):
    controllers = build_controllers({} if key is None else {"TYPESAFE_API_KEY": key}, url)
    keyed = build(controllers.rules, controllers.scaffold, controllers.spec, controllers.review, lambda: None)
    return runner.invoke(keyed, list(args))


def test_the_profile_with_an_eval_of_each_form_is_valid_and_check_is_unchanged():
    assert runner.invoke(app, ["profile", "check"]).exit_code == 0
    assert runner.invoke(app, ["check"]).exit_code == 0


def test_an_eval_not_calibrated_does_not_run_and_the_review_says_what_to_run():
    result = xarch("review", SERVICE, "--offline", key=None)
    assert ("  rule-outside-entity   not run: uncalibrated: it was never held to its examples; run `xarch review "
            "calibrate --eval rule-outside-entity`") in result.output.splitlines()


def test_calibrate_holds_each_eval_to_its_examples_records_the_verdicts_and_review_then_runs_them(served, tmp_path):
    result = xarch("review", "calibrate", url=served.url)
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert "rule-outside-entity   passed: line 0.50 (set from the examples)" in lines
    assert "logic-purity   passed: line 0.75 (set from the examples)" in lines
    assert "document-sender   passed: line 0.50 (set from the examples)" in lines
    assert lines[-1] == "recorded in .xarch/calibration.json: commit it, so that every review reads the same verdicts"
    record = (tmp_path / ".xarch" / "calibration.json").read_text()
    assert "PublishingService" not in record and "Does this method" not in record and KEY not in record
    assert {body["questions"]["placement"]["type"] for body in served.received} == {"noul", "score", "choice"}
    sent = xarch("review", SERVICE, url=served.url)
    assert sent.exit_code == 0 and "PublishingService.publish may decide a rule of a document itself (0.90)" in sent.output
    read = xarch("review", SERVICE, "--offline", "--format", "json", key=None)
    assert read.exit_code == 0, read.output
    rule = {item["id"]: item for item in json.loads(read.output)["evals"]}["rule-outside-entity"]
    assert (rule["state"], rule["asked"], [r["name"] for r in rule["readings"]]) == (
        "calibrated", 26, ["PublishingService.publish"])


def test_an_eval_changed_since_it_was_calibrated_is_stale_and_does_not_run(served, tmp_path):
    assert xarch("review", "calibrate", url=served.url).exit_code == 0
    document = yaml.safe_load((tmp_path / COPY).read_text())
    document["evals"]["rule-outside-entity"]["ask"] = "Does this method test a document's fields to decide a change?"
    (tmp_path / COPY).write_text(yaml.safe_dump(document, sort_keys=False))
    result = xarch("review", SERVICE, "--offline", key=None)
    assert ("  rule-outside-entity   not run: stale: its question, answer, scope, line or examples changed since it "
            "was held to its examples; run `xarch review calibrate --eval rule-outside-entity`"
            in result.output.splitlines())


def test_offline_a_calibration_reads_the_answers_kept_and_with_none_kept_is_incomplete(served):
    assert xarch("review", "calibrate", "--offline", key=None).exit_code == 3
    assert xarch("review", "calibrate", url=served.url).exit_code == 0
    again = xarch("review", "calibrate", "--offline", "--eval", "logic-purity", key=None)
    assert again.exit_code == 0 and "Asked 0, from cache 4." in again.output


def test_an_eval_whose_examples_fail_exits_1_and_says_what_to_do(served, tmp_path):
    document = yaml.safe_load((tmp_path / COPY).read_text())
    document["evals"]["rule-outside-entity"]["examples"] = examples(DECIDES, DECIDES.replace("pass", "x"), "services")
    (tmp_path / COPY).write_text(yaml.safe_dump(document, sort_keys=False))
    result = xarch("review", "calibrate", "--eval", "rule-outside-entity", url=served.url)
    assert result.exit_code == 1
    assert "make it one short rule about what the text shows; add a clean example of the case it must not catch" in (
        result.output)


def test_calibrate_refuses_files_an_eval_it_does_not_write_and_no_key():
    assert xarch("review", "calibrate", SERVICE).exit_code == 2
    unknown = xarch("review", "calibrate", "--eval", "other", key=None)
    assert unknown.exit_code == 2 and "no eval of the profile's own named other" in unknown.output
    assert xarch("review", "calibrate", key=None).exit_code == 2
    assert xarch("review", SERVICE, "--eval", "logic-purity", key=None).exit_code == 2


THIRD = "modules/documents/application/services/drafts/c.py"
THIRD_CODE = DECIDES.replace("PublishingService", "DraftingService")


def written(tmp_path, never: list[str] | None, third: bool = True) -> None:
    document = yaml.safe_load((tmp_path / COPY).read_text())
    if third:
        document["evals"]["rule-outside-entity"]["examples"]["flagged"][THIRD] = THIRD_CODE
    document.pop("review", None)
    if never is not None:
        document["review"] = {"never": never}
    (tmp_path / COPY).write_text(yaml.safe_dump(document, sort_keys=False))


def stands(eval_id: str) -> str:
    found = json.loads(xarch("review", SERVICE, "--offline", "--format", "json", key=None).output)
    return {item["id"]: item for item in found["evals"]}[eval_id]["state"]


def test_an_example_review_never_matches_is_never_sent_in_a_calibration_nor_its_dry_run_and_is_listed_held_back(
        served, tmp_path):
    written(tmp_path, ["**/drafts"])
    assert runner.invoke(app, ["profile", "check"]).exit_code == 0
    dry = xarch("review", "calibrate", "--eval", "rule-outside-entity", "--dry-run", url=served.url)
    assert dry.exit_code == 0, dry.output
    assert f"  rule-outside-entity: flagged example {THIRD}: held back by review.never (**/drafts)" in (
        dry.output.splitlines())
    assert "DraftingService" not in dry.output
    planned = json.loads(xarch("review", "calibrate", "--dry-run", "--format", "json", url=served.url).output)
    assert THIRD not in [item["example"] for item in planned["requests"]]
    assert planned["held_back"] == [{"id": "rule-outside-entity", "kind": "flagged", "example": THIRD,
                                     "pattern": "**/drafts"}] and planned["too_few"] == []
    done = xarch("review", "calibrate", "--format", "json", url=served.url)
    assert done.exit_code == 0, done.output
    found = json.loads(done.output)
    assert found["held_back"] == planned["held_back"]
    assert {item["id"]: item["passed"] for item in found["calibrated"]}["rule-outside-entity"] is True
    assert served.received and not any("DraftingService" in body["state"] for body in served.received)
    assert stands("rule-outside-entity") == "calibrated"


def test_a_record_made_with_an_example_does_not_stand_once_review_never_holds_it_back_nor_the_reverse(served,
                                                                                                    tmp_path):
    written(tmp_path, None)
    assert xarch("review", "calibrate", "--eval", "rule-outside-entity", url=served.url).exit_code == 0
    assert stands("rule-outside-entity") == "calibrated"
    written(tmp_path, ["**/drafts"])
    assert stands("rule-outside-entity") == "stale"
    assert xarch("review", "calibrate", "--eval", "rule-outside-entity", url=served.url).exit_code == 0
    assert stands("rule-outside-entity") == "calibrated"
    written(tmp_path, ["**/no-such-folder"])
    assert stands("rule-outside-entity") == "stale"
    written(tmp_path, ["**/drafts", "**/no-such-folder"])
    assert stands("rule-outside-entity") == "calibrated"


def test_an_eval_review_never_leaves_with_too_few_examples_is_not_held_sends_nothing_of_it_and_exits_1(served,
                                                                                                      tmp_path):
    written(tmp_path, ["modules/documents/application/logic/a.py"], third=False)
    dry = xarch("review", "calibrate", "--eval", "logic-purity", "--dry-run", url=served.url)
    assert dry.exit_code == 0, dry.output
    assert ("  logic-purity: fewer than 2 of its flagged examples remain: it is not held, and nothing of it is sent"
            in dry.output.splitlines())
    result = xarch("review", "calibrate", url=served.url)
    assert result.exit_code == 1, result.output
    assert ("logic-purity   not held: fewer than 2 of its flagged examples remain once review.never holds some back: "
            "write more examples it does not match, or narrow review.never") in result.output.splitlines()
    assert served.received and not any("def stale(" in body["state"] for body in served.received)
    assert stands("logic-purity") == "failed"
    assert stands("rule-outside-entity") == "calibrated"


def test_placement_never_sends_a_docs_example_review_never_matches_and_its_part_is_measured_elsewhere_only(served,
                                                                                                         tmp_path):
    written(tmp_path, ["modules/documents/adapters"], third=False)
    planned = json.loads(xarch("review", "calibrate", "--eval", "placement", "--dry-run", "--format", "json",
                               url=served.url).output)
    assert [(item["id"], item["kind"], item["example"]) for item in planned["held_back"]] == [
        ("placement", "clean", "modules/documents/adapters/db_document_repo.py"),
        ("placement", "clean", "modules/documents/adapters/moderation_content_review.py")]
    assert not any(item["example"].startswith("modules/documents/adapters/") for item in planned["requests"])
    done = json.loads(xarch("review", "calibrate", "--eval", "placement", "--format", "json", url=served.url).output)
    assert {part["part"]: part["verdict"] for part in done["placement"]["parts"]}["adapters"] == "elsewhere"
    assert done["held_back"] == planned["held_back"]
    assert len(served.received) == len(planned["requests"])


NOTED = ("from app.kernel.time import Clock  # NOTE-1 the clock is kernel's\n\n\n# NOTE-2 a service: it orchestrates\n"
         "class PublishingService:\n    def publish(self, doc) -> None:\n        # NOTE-3 the rule lives in domain\n"
         "        if not doc.title.strip():  # NOTE-4 a title\n            raise ValueError('# kept: a string')\n")


def test_an_eval_s_own_examples_are_sent_with_their_comments_cut_in_a_calibration_and_its_dry_run_alike(served,
                                                                                                       tmp_path):
    document = yaml.safe_load((tmp_path / COPY).read_text())
    document["evals"] = {"rule-outside-entity": {**EVALS["rule-outside-entity"],
                                                 "examples": examples(NOTED, ASKS, "services")}}
    (tmp_path / COPY).write_text(yaml.safe_dump(document, sort_keys=False))
    planned = json.loads(xarch("review", "calibrate", "--eval", "rule-outside-entity", "--dry-run", "--format",
                               "json").output)
    shown = [item["text"] for item in planned["requests"]]
    assert planned["masked"] == ["own-imports", "e-mail", "comments"]
    assert shown[0] == ("    def publish(self, doc) -> None:\n\n        if not doc.title.strip():\n"
                        "            raise ValueError('# kept: a string')\n")
    assert xarch("review", "calibrate", "--eval", "rule-outside-entity", url=served.url).exit_code == 0
    sent = [body["state"] for body in served.received]
    assert set(sent) == set(shown) and not any("NOTE-" in text for text in shown + sent)
    assert any("# kept: a string" in text for text in sent)
