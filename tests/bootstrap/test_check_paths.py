"""xarch check PATH ... and --files-from: every check runs on the whole app, the violations of the paths given alone
are shown and decide the exit code, and the others are counted on the partial line and in the JSON document."""
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
COMMENTED = "app/kernel/x.py"
ELSEWHERE = "app/kernel/y.py"


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["init", "--profile", "web"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "docs"]).exit_code == 0
    (tmp_path / COMMENTED).write_text("X = 1  # why\n")
    (tmp_path / ELSEWHERE).write_text("Y = 1  # why\n")


def test_a_path_given_shows_its_violations_alone_and_fails():
    result = runner.invoke(app, ["check", COMMENTED])
    assert result.exit_code == 1
    assert f"{COMMENTED}:1: a comment (no-comments)" in result.stdout and ELSEWHERE not in result.stdout
    assert "1 violation(s) in 1 file(s) of the 1 path(s) given" in result.stdout
    assert "none skipped; 1 violation(s) in other files, not shown" in result.stdout


def test_a_clean_path_passes_and_says_how_many_violations_other_files_have(tmp_path):
    (tmp_path / "app/kernel/clean.py").write_text("Z = 1\n")
    result = runner.invoke(app, ["check", "app/kernel/clean.py"])
    assert result.exit_code == 0
    assert "OK: no violations in the 1 path(s) given" in result.stdout
    assert "2 violation(s) in other files, not shown" in result.stdout


def test_the_paths_may_come_one_per_line_on_stdin_and_with_the_paths_given():
    result = runner.invoke(app, ["check", "--files-from", "-", "--format", "json"], input=f"{COMMENTED}\n\n")
    document = json.loads(result.stdout)
    assert result.exit_code == 1 and document["ok"] is False
    assert [v["file"] for v in document["violations"]] == [COMMENTED]
    assert document["partial"] == {"paths": [COMMENTED], "skipped_checks": [], "elsewhere": 1}
    both = runner.invoke(app, ["check", ELSEWHERE, "--files-from", "-", "--format", "json"], input=f"{COMMENTED}\n")
    assert [v["file"] for v in json.loads(both.stdout)["violations"]] == [COMMENTED, ELSEWHERE]


def test_an_empty_list_on_stdin_shows_no_violation_and_counts_every_one():
    result = runner.invoke(app, ["check", "--files-from", "-", "--format", "json"], input="")
    document = json.loads(result.stdout)
    assert (result.exit_code, document["violations"], document["partial"]["elsewhere"]) == (0, [], 2)


def test_a_check_of_no_path_is_the_whole_check_with_no_partial_line():
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1 and "partial:" not in result.stdout
    assert "2 violation(s) in 2 file(s)" in result.stdout
