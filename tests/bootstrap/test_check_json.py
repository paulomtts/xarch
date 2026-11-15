"""xarch check --format json: one JSON document on stdout, the same violations the text output prints, each with its
rule and fix, in a stable order; and a refusal is JSON too, with exit code 2."""
import json
import shutil

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "web"]).exit_code == 0
    assert runner.invoke(app, ["new", "modules", "docs"]).exit_code == 0


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
        {"rule": "no-comments", "file": "app/kernel/x.py", "line": 1,
         "message": "a comment: say it in a docstring or a name (no-comments)", "fix": "say it in a docstring or a name"},
        {"rule": "forbidden", "file": "app/modules/docs/domain/clock.py", "line": 1,
         "message": "domain/ of modules/docs may not import socket (forbidden.domain)",
         "fix": "do what needs socket outside domain/, and hand domain/ the result"},
        {"rule": "no-comments", "file": "app/modules/docs/domain/clock.py", "line": 1,
         "message": "a comment: say it in a docstring or a name (no-comments)", "fix": "say it in a docstring or a name"},
        {"rule": "rules", "file": "app/modules/docs/domain/clock.py", "line": 2,
         "message": "domain/ of modules/docs may not import platform/ (app.platform)", "fix": None},
    ]


def test_a_violation_of_a_whole_file_or_folder_has_no_line(tmp_path):
    shutil.rmtree(tmp_path / "app/modules/docs/adapters")
    document = json.loads(runner.invoke(app, ["check", "--format", "json"]).stdout)
    assert document["violations"] == [{"rule": "structure", "file": "app/modules/docs", "line": None,
                                       "message": "missing adapters/", "fix": "create app/modules/docs/adapters/"}]


def test_the_text_output_prints_the_same_violations_as_before(tmp_path):
    (tmp_path / "app/kernel/x.py").write_text("from app.platform import x\n")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert result.stdout.splitlines()[:2] == ["app/kernel/x.py:1: kernel/ may not import platform/ (app.platform)",
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
