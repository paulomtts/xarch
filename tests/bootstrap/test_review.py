"""xarch review on a project `init` and `new` made: what --dry-run would send for the files chosen, masked, as text and
as JSON, with nothing sent; the files left out and why; and every refusal, which exits 2."""
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
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
    return runner.invoke(app, ["review", *args], input=stdin)


def test_a_dry_run_shows_the_masked_text_it_would_send_and_sends_nothing():
    result = review(SERVICE, "--dry-run")
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0].startswith("review: advisory.")
    assert lines[1] == "Nothing was sent (--dry-run)."
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
    assert (sent["file"], sent["part"], sent["chars"], document["sent"]) == (SERVICE, "services", len(BODY), False)


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
    pytest.param([SERVICE], "sends nothing yet", id="a review that would send"),
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


def test_review_changes_nothing_check_finds():
    before = runner.invoke(app, ["check", "--format", "json"])
    review(SERVICE, "--dry-run")
    after = runner.invoke(app, ["check", "--format", "json"])
    assert (before.exit_code, before.output) == (after.exit_code, after.output)
