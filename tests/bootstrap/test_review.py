"""xarch review on a project `init` and `new` made: what --dry-run would send for the files chosen, masked, as text and
as JSON, with nothing sent; the files left out and why; and every refusal, which exits 2. The app is built with no key
in its environment, so that nothing can be sent."""
import json
import os
import subprocess
import sys

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers
from xarch.cli.app import build

runner = CliRunner()
CONTROLLERS = build_controllers({})
KEYLESS = build(CONTROLLERS.rules, CONTROLLERS.scaffold, CONTROLLERS.spec, CONTROLLERS.review, lambda: None)
SERVICE = "app/modules/documents/application/services/document_service.py"
BODY = ('"""Publishing documents; questions to docs@example.com."""\n'
        "from app.kernel.time import Clock\n"
        "from app.modules.documents.domain.values import DocumentId\n"
        "from .helpers import shared\n"
        "\n\n"
        "class DocumentService:\n"
        "    def __init__(self, clock: Clock):\n"
        "        self._clock = clock\n"
        "\n"
        + "".join(f"    def step_{n}(self, id: DocumentId) -> None:\n        shared(id, self._clock.now())\n\n"
                  for n in range(12)))


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "cli"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "documents"]).exit_code == 0
    (tmp_path / SERVICE).write_text(BODY)


def review(*args: str, stdin: str | None = None):
    return runner.invoke(KEYLESS, ["review", *args], input=stdin)


def test_a_dry_run_shows_the_masked_text_it_would_send_and_sends_nothing():
    result = review(SERVICE, "--dry-run")
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0].startswith("review (experimental): advisory.")
    assert lines[1] == "Nothing was sent (--dry-run)."
    assert lines[2] == ("Without --dry-run, review sends to TypeSafe (https://api.typesafe.ai), as the model "
                        "jev-1.14.0, the masked text of each file below that is not in the cache and the question after "
                        "it: nothing else of the project. It sends whenever TYPESAFE_API_KEY is set: the key alone "
                        "allows it, and the key is not set now.")
    assert lines[3].startswith("1 file(s) found (paths), 1 to be judged, 0 left out; 1 request(s)")
    quoted = [line.removeprefix("    | ") for line in lines if line.startswith("    |")]
    assert quoted[:4] == ['"""Publishing documents; questions to person@example.test."""',
                          "from <masked> import Clock", "from <masked> import DocumentId", "from <masked> import shared"]
    assert "docs@example.com" not in result.output and "app.modules.documents" not in result.output


def test_the_question_offers_every_part_of_the_profile_by_its_litmus():
    document = json.loads(review(SERVICE, "--dry-run", "--format", "json").output)
    names = [option["name"] for option in document["question"]["options"]]
    assert names[:4] == ["domain", "logic", "ports", "services"]
    assert all(option["description"] for option in document["question"]["options"])
    (sent,) = document["requests"]
    assert (sent["file"], sent["part"], sent["chars"], document["sent"]) == (SERVICE, "services", len(sent["text"]),
                                                                              False)
    assert json.loads(sent["body"])["state"] == sent["text"] and "Authorization" not in sent["body"]
    assert document["sends"] == {"name": "TypeSafe", "at": "https://api.typesafe.ai", "model": "jev-1.14.0",
                                 "key": "TYPESAFE_API_KEY", "keyed": False, "unusable": None}


def test_a_list_is_read_from_stdin_and_what_is_not_judged_is_said_with_why():
    listed = f"{SERVICE}\n\nREADME.md\napp/modules/documents/domain/gone.py\ntests/architecture/test_rules.py\n"
    document = json.loads(review("--files-from", "-", "--dry-run", "--format", "json", stdin=listed).output)
    assert document["selection"]["by"] == ["files-from"]
    assert [(item["file"], item["why"]) for item in document["selection"]["left_out"]] == [
        ("app/README.md", "missing"), ("app/modules/documents/domain/gone.py", "missing"),
        ("tests/architecture/test_rules.py", "test")]
    assert [sent["file"] for sent in document["requests"]] == [SERVICE]


def test_every_file_of_the_app_leaves_out_those_too_small_to_judge_and_the_package_files_of_the_structure():
    document = json.loads(review("--all", "--dry-run", "--format", "json").output)
    assert [sent["file"] for sent in document["requests"]] == [SERVICE]
    left = {item["file"]: item["why"] for item in document["selection"]["left_out"]}
    assert (left["app/modules/documents/domain/__init__.py"], left["app/modules/__init__.py"]) == ("small", "unplaced")
    assert set(left.values()) == {"small", "unplaced"}


@pytest.mark.parametrize("args, said", [
    pytest.param(["--dry-run"], "review reads only the files it is given, and none was", id="nothing chosen"),
    pytest.param(["--all", SERVICE, "--dry-run"], "--all takes every file of the app", id="every file with paths"),
    pytest.param(["--all", "--dry-run", "--max-files", "1", "app"], "--all takes every file", id="every file with a folder"),
    pytest.param(["/elsewhere/x.py", "--dry-run"], "lies outside the project", id="a path outside the project"),
    pytest.param([SERVICE], "no key: set TYPESAFE_API_KEY, or run --dry-run to see what would be sent, or --offline to "
                            "use cached answers only", id="a review that would send with no key set"),
])
def test_a_refusal_exits_2_and_says_why(args, said):
    result = review(*args)
    assert result.exit_code == 2
    assert said in result.output


def test_more_files_than_one_run_judges_is_refused_before_anything_is_shown(tmp_path):
    (tmp_path / "app/modules/documents/domain/values.py").write_text(BODY)
    result = review("app/modules", "--dry-run", "--max-files", "1", "--format", "json")
    assert result.exit_code == 2
    assert json.loads(result.output) == {"ok": False, "error": "2 files would be judged, more than one run judges (1): "
                                                              "choose fewer, or raise --max-files; nothing was sent"}


def test_a_file_review_never_sends_is_left_out_with_the_path_and_a_text_review_mask_hides_is_masked(tmp_path):
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "cli"]).exit_code == 0
    profile = tmp_path / "architecture" / "mine" / "mine.yaml"
    profile.write_text(profile.read_text() + "review:\n  never: [modules/*/adapters]\n  mask: [DocumentService, 'step_*']\n")
    adapter = "app/modules/documents/adapters/legal_archive.py"
    (tmp_path / adapter).write_text(BODY)
    result = review(SERVICE, adapter, "--dry-run", "--profile", str(profile))
    assert result.exit_code == 0, result.output
    assert f"  {adapter}: held back by review.never (modules/*/adapters)" in result.output.splitlines()
    assert "class <masked>:" in result.output and "    |     def <masked>(self, id: DocumentId) -> None:" in result.output
    assert "DocumentService" not in result.output.replace("review.mask hides: DocumentService, step_*", "")
    document = json.loads(review(SERVICE, adapter, "--dry-run", "--profile", str(profile), "--format", "json").output)
    assert [sent["file"] for sent in document["requests"]] == [SERVICE]
    assert {"file": adapter, "why": "never", "chars": len(BODY), "pattern": "modules/*/adapters"} in (
        document["selection"]["left_out"])
    assert document["mask"] == ["DocumentService", "step_*"]


def test_a_link_out_of_the_app_is_left_out_and_review_never_holds_back_a_link_to_a_file_it_matches(tmp_path,
                                                                                                     tmp_path_factory):
    outside = tmp_path_factory.mktemp("elsewhere")
    (outside / "outside_secret.py").write_text(BODY.replace("DocumentService", "OutsideSecret"))
    (outside / "inner.py").write_text(BODY.replace("DocumentService", "InnerSecret"))
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "cli"]).exit_code == 0
    profile = tmp_path / "architecture" / "mine" / "mine.yaml"
    profile.write_text(profile.read_text() + "review:\n  never: ['**/secret_*.py']\n")
    adapters = tmp_path / "app/modules/documents/adapters"
    (adapters / "secret_keys.py").write_text(BODY.replace("DocumentService", "SecretKeys"))
    (adapters / "link_out.py").symlink_to(outside / "outside_secret.py")
    (adapters / "alias.py").symlink_to(adapters / "secret_keys.py")
    (adapters / "linkdir").symlink_to(outside, target_is_directory=True)
    linked = ["app/modules/documents/adapters/link_out.py", "app/modules/documents/adapters/alias.py",
              "app/modules/documents/adapters/linkdir/inner.py"]
    document = json.loads(review("app/modules/documents/adapters", *linked, "--dry-run", "--profile", str(profile),
                                 "--format", "json").output)
    assert document["requests"] == []
    assert {(item["file"], item["why"], item["pattern"]) for item in document["selection"]["left_out"]} == {
        ("app/modules/documents/adapters/secret_keys.py", "never", "**/secret_*.py"),
        ("app/modules/documents/adapters/alias.py", "never", "**/secret_*.py"),
        ("app/modules/documents/adapters/link_out.py", "link", None),
        ("app/modules/documents/adapters/linkdir/inner.py", "link", None),
        ("app/modules/documents/adapters/__init__.py", "small", None)}
    text = review(*linked, "--dry-run", "--profile", str(profile)).output
    assert "  app/modules/documents/adapters/link_out.py: a link to a file outside the app, or to no source file" in (
        text.splitlines())
    assert not any(secret in text for secret in ("OutsideSecret", "InnerSecret", "SecretKeys"))


def test_an_import_over_several_lines_or_with_blanks_around_its_dots_is_masked_in_what_would_be_sent(tmp_path):
    body = BODY.replace("from app.kernel.time import Clock", "from app . kernel . time import Clock").replace(
        "from app.modules.documents.domain.values import DocumentId",
        "from \\\n    app.modules.documents.domain.values import (\n    DocumentId,\n)")
    (tmp_path / SERVICE).write_text(body)
    document = json.loads(review(SERVICE, "--dry-run", "--format", "json").output)
    (sent,) = document["requests"]
    assert "from <masked> import Clock" in sent["text"] and "from \\\n    <masked> import (" in sent["text"]
    assert "app.modules" not in sent["text"] and "kernel" not in sent["text"]


def test_a_record_that_cannot_be_read_is_refused_with_exit_2_naming_it_and_is_never_rewritten(tmp_path):
    record = tmp_path / ".xarch" / "calibration.json"
    record.parent.mkdir()
    record.write_text('<<<<<<< HEAD\n{"evals": {}}\n=======\n{}\n>>>>>>> other\n')
    runs = [review(SERVICE, "--dry-run"), review(SERVICE, "--offline"), review("calibrate", "--offline")]
    assert [result.exit_code for result in runs] == [2, 2, 2]
    assert all(f"the record {record} cannot be read (it is not JSON)" in result.output for result in runs)
    assert record.read_text().startswith("<<<<<<< HEAD")


def test_placement_s_examples_are_masked_in_a_project_whose_app_has_another_name(tmp_path, monkeypatch):
    (tmp_path / "shop_project").mkdir()
    monkeypatch.chdir(tmp_path / "shop_project")
    assert runner.invoke(app, ["init", "--profile", "cli", "--app", "shop"]).exit_code == 0
    result = review("calibrate", "--dry-run", "--format", "json")
    assert result.exit_code == 0, result.output
    texts = [item["text"] for item in json.loads(result.output)["requests"]]
    assert texts and not any("from app." in text or "import app." in text for text in texts)


def test_check_never_acts_on_review_or_evals_but_a_value_written_wrong_makes_the_profile_invalid_for_it(tmp_path):
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "cli"]).exit_code == 0
    profile = tmp_path / "architecture" / "mine" / "mine.yaml"
    written = profile.read_text()
    before = [runner.invoke(app, ["check", "--profile", str(profile), *strict]) for strict in ([], ["--strict"])]
    profile.write_text(written + "review:\n  mask: [Northwind]\nevals:\n  placement:\n    lines: {domain: 0.1}\n")
    after = [runner.invoke(app, ["check", "--profile", str(profile), *strict]) for strict in ([], ["--strict"])]
    assert [result.exit_code for result in after] == [result.exit_code for result in before]
    profile.write_text(written + "evals:\n  placement:\n    lines: {domain: 2}\n")
    wrong = runner.invoke(app, ["check", "--profile", str(profile)])
    assert wrong.exit_code == 2 and "evals.placement.lines.domain: 2 is not a line" in wrong.output


@pytest.mark.parametrize("written", ["./calibrate", "calibrate/"])
def test_a_path_named_calibrate_written_as_a_path_is_reviewed_not_taken_for_the_word(tmp_path, written):
    (tmp_path / "calibrate").mkdir()
    result = review(written, "--dry-run", "--format", "json")
    assert result.exit_code == 0, result.output
    document = json.loads(result.output)
    assert document["selection"]["by"] == ["paths"] and "question" in document


@pytest.mark.parametrize("args, said", [
    pytest.param(("--dry-run", "--offline"), "--dry-run sends nothing and reads no answer, --offline reads the answers "
                                             "kept: give one", id="a dry run offline"),
    pytest.param(("--context", "imports"), "--context says what is sent before each piece: give it with --pieces",
                 id="context without pieces"),
])
def test_options_that_say_nothing_together_are_refused_with_exit_2(args, said):
    result = review(SERVICE, *args)
    assert result.exit_code == 2 and said in result.output


def test_an_app_folder_that_is_not_there_is_refused_with_exit_2(tmp_path):
    result = review("--all", "--dry-run", "--app", "nowhere")
    assert result.exit_code == 2 and f"{tmp_path / 'nowhere'} is not a directory" in result.output


def test_a_reader_that_closes_the_output_early_leaves_the_review_its_own_exit_code(tmp_path):
    for n in range(12):
        (tmp_path / f"app/modules/documents/domain/value_{n}.py").write_text(BODY * 20)
    run = subprocess.Popen([sys.executable, "-c", "from xarch.bootstrap.app import app; app()", "review", "--dry-run",
                            "--all"], cwd=tmp_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env={**os.environ, "TYPESAFE_API_KEY": ""})
    assert run.stdout is not None and run.stdout.readline()
    run.stdout.close()
    assert run.wait(timeout=60) == 0 and b"Traceback" not in (run.stderr.read() if run.stderr else b"")


def test_review_changes_nothing_check_finds():
    before = runner.invoke(app, ["check", "--format", "json"])
    review(SERVICE, "--dry-run")
    after = runner.invoke(app, ["check", "--format", "json"])
    assert (before.exit_code, before.output) == (after.exit_code, after.output)
