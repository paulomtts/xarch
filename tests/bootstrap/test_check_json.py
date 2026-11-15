"""xarch check --format json: one JSON document on stdout, the same violations the text output prints, each with its
rule and fix, in a stable order; and a refusal is JSON too, with exit code 2."""
import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

import xarch
from xarch.bootstrap.app import app

runner = CliRunner()
BUNDLED = Path(xarch.__file__).parent / "architectures"


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "web"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "docs"]).exit_code == 0


def test_a_clean_project_is_ok_with_no_violations():
    result = runner.invoke(app, ["check", "--format", "json"])
    document = json.loads(result.stdout)
    assert result.exit_code == 0
    assert (document["ok"], document["profile"], document["violations"]) == (True, "web", [])


def test_each_violation_carries_its_rule_file_line_message_and_fix_sorted_by_file_line_and_rule(tmp_path):
    (tmp_path / "app/modules/docs/domain/clock.py").write_text("import socket  # why\nfrom app.platform import x\n")
    (tmp_path / "app/kernel/x.py").write_text("x = 1  # why\n")
    result = runner.invoke(app, ["check", "--format", "json"])
    document = json.loads(result.stdout)
    assert result.exit_code == 1 and document["ok"] is False
    assert document["violations"] == [
        {"rule": "no-comments", "file": "app/kernel/x.py", "line": 1, "message": "a comment (no-comments)",
         "fix": "say it in a docstring or a name, and delete the comment", "hint": None},
        {"rule": "forbidden", "file": "app/modules/docs/domain/clock.py", "line": 1,
         "message": "domain/ of modules/docs may not import socket (parts.domain.forbidden)",
         "fix": "do what needs socket outside domain/, and hand domain/ the result", "hint": None},
        {"rule": "no-comments", "file": "app/modules/docs/domain/clock.py", "line": 1,
         "message": "a comment (no-comments)", "fix": "say it in a docstring or a name, and delete the comment",
         "hint": None},
        {"rule": "rules", "file": "app/modules/docs/domain/clock.py", "line": 2,
         "message": "domain/ of modules/docs may not import platform/ (app.platform)",
         "fix": "import only domain/, kernel/ in domain/ of modules/docs (parts.domain.may_import), or move this code to "
                "adapters/, which may import it", "hint": None},
    ]


def test_a_violation_of_a_whole_file_or_folder_has_no_line(tmp_path):
    shutil.rmtree(tmp_path / "app/modules/docs/adapters")
    document = json.loads(runner.invoke(app, ["check", "--format", "json"]).stdout)
    assert document["violations"] == [{"rule": "structure", "file": "app/modules/docs", "line": None,
                                       "message": "missing adapters/", "fix": "create app/modules/docs/adapters/",
                                       "hint": None}]


def test_the_text_output_prints_each_violation_with_its_fix_under_it(tmp_path):
    (tmp_path / "app/kernel/x.py").write_text("from app.platform import x\n")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert result.stdout.splitlines()[:3] == [
        "app/kernel/x.py:1: kernel/ may not import platform/ (app.platform)",
        "    fix: import only kernel/ in kernel/ (parts.kernel.may_import), or move this code to adapters/, which may "
        "import it",
        "1 violation(s) in 1 file(s)"]


@pytest.mark.parametrize("arguments, error", [
    (["--profile", "nowhere"], "unknown profile 'nowhere'"),
    (["--app", "missing"], "missing is not a directory"),
])
def test_a_refusal_is_a_json_error_with_exit_code_2(arguments, error):
    result = runner.invoke(app, ["check", "--format", "json", *arguments])
    document = json.loads(result.stdout)
    assert result.exit_code == 2
    assert document["ok"] is False and error in document["error"]


def with_hints(tmp_path) -> None:
    shutil.copytree(BUNDLED, tmp_path / "arch")
    text = (BUNDLED / "web.yaml").read_text() + "\nhints:\n  rules: the layers are in docs/project/architecture.md\n"
    (tmp_path / "arch/mine.yaml").write_text(text)
    (tmp_path / "app/kernel/x.py").write_text("from app.platform import x\nimport socket\n")


def test_the_hint_of_a_profile_follows_the_fix_of_every_violation_of_its_rule_in_text_and_in_json(tmp_path):
    with_hints(tmp_path)
    lines = runner.invoke(app, ["check", "--profile", "arch/mine.yaml"]).stdout.splitlines()
    assert lines[:6] == [
        "app/kernel/x.py:1: kernel/ may not import platform/ (app.platform)",
        "    fix: import only kernel/ in kernel/ (parts.kernel.may_import), or move this code to adapters/, which may import it",
        "    hint: the layers are in docs/project/architecture.md",
        "app/kernel/x.py:2: kernel/ may not import socket (parts.kernel.forbidden)",
        "    fix: do what needs socket outside kernel/, and hand kernel/ the result",
        "2 violation(s) in 1 file(s)"]
    document = json.loads(runner.invoke(app, ["check", "--profile", "arch/mine.yaml", "--format", "json"]).stdout)
    assert [(v["rule"], v["hint"]) for v in document["violations"]] == [
        ("rules", "the layers are in docs/project/architecture.md"), ("forbidden", None)]


def test_a_profile_with_a_hint_for_an_unknown_rule_is_refused(tmp_path):
    shutil.copytree(BUNDLED, tmp_path / "arch")
    (tmp_path / "arch/mine.yaml").write_text((BUNDLED / "web.yaml").read_text() + "\nhints:\n  nothing: x\n")
    result = runner.invoke(app, ["check", "--profile", "arch/mine.yaml"])
    assert result.exit_code == 2
    assert "hints.nothing: unknown rule id 'nothing': use built-by, closed-tree, cycles, dead-code" in result.output
