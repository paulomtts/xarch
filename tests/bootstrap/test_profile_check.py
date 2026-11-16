"""`xarch profile check` through the real app: a profile is validated without an app, every problem at once, and the way
it differs from the profile it is based on is shown as information."""
import json

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\n')
    runner.invoke(app, ["profile", "new", "mine", "--from", "web"])


COPY = "architecture/mine/mine.yaml"


def edit(tmp_path, change):
    path = tmp_path / COPY
    document = yaml.safe_load(path.read_text())
    change(document)
    path.write_text(yaml.safe_dump(document, sort_keys=False))


def test_a_bundled_profile_and_the_configured_one_are_valid():
    assert runner.invoke(app, ["profile", "check", "web"]).exit_code == 0
    result = runner.invoke(app, ["profile", "check"])
    assert result.exit_code == 0 and result.output.splitlines()[0] == "checking cli (bundled)"


def test_a_valid_copy_says_what_was_checked_and_that_it_is_no_looser_than_the_profile_it_is_based_on():
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == f"checking {COPY} (custom; closest bundled: web)"
    for expected in ("loads: ok", "files: all", "examples: ok", "no looser than web", "OK: the profile is valid"):
        assert expected in result.output


def test_an_unknown_key_fails_with_the_keys_that_exist(tmp_path):
    edit(tmp_path, lambda d: d.update(colour=1))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1
    assert "unknown key 'colour'" in result.output and "use based_on" in result.output
    assert "examples: not checked" in result.output and "INVALID: 1 problem" in result.output


def test_a_part_importing_a_part_that_does_not_exist_fails(tmp_path):
    edit(tmp_path, lambda d: d["parts"]["domain"].update(may_import=["kernel", "ghost"]))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1 and "ghost" in result.output and "INVALID" in result.output


def test_a_file_the_profile_points_to_that_is_gone_fails_naming_it(tmp_path):
    (tmp_path / "architecture" / "mine" / "agents.md").unlink()
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1 and "agents.md" in result.output


def test_an_example_that_imports_what_its_part_may_not_fails_with_the_example_and_the_key(tmp_path):
    example = next((tmp_path / "architecture" / "mine" / "examples" / "shared").rglob("controller.py"))
    example.write_text(example.read_text() + "\nfrom app.platform import clock\n")
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1 and "examples:" in result.output and "may not import" in result.output


def test_a_looser_copy_is_still_valid_and_the_difference_is_information(tmp_path):
    edit(tmp_path, lambda d: d["parts"]["domain"].update(may_import=["kernel", "platform"]))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 0, result.output
    assert "looser than web" in result.output and "domain may also import" in result.output


def test_each_public_name_a_copy_accepts_as_only_the_tests_is_a_way_it_is_looser(tmp_path):
    edit(tmp_path, lambda d: d["guards"]["dead-code"].update(tests_only=True, known=["kernel/ids.py:make"]))
    result = runner.invoke(app, ["profile", "check", COPY, "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["compared_with"] == {"profile": "web", "looser": [
        {"key": "known", "part": "", "what": "kernel/ids.py:make",
         "sentence": "the tests-only check accepts kernel/ids.py:make as a name only the tests use (guards.dead-code.known)"}]}


def test_json_gives_ok_the_problems_by_check_the_files_and_the_difference(tmp_path):
    good = json.loads(runner.invoke(app, ["profile", "check", COPY, "--format", "json"]).output)
    assert good["ok"] is True and good["profile"] == COPY and good["problems"] == [] and good["files"] > 10
    assert good["compared_with"] == {"profile": "web", "looser": []}
    edit(tmp_path, lambda d: d.update(colour=1))
    bad = runner.invoke(app, ["profile", "check", COPY, "--format", "json"])
    assert bad.exit_code == 1
    document = json.loads(bad.output)
    assert document["ok"] is False and document["problems"][0]["check"] == "load"
    assert "colour" in document["problems"][0]["message"]


def test_a_profile_that_cannot_be_chosen_is_refused_with_exit_2(tmp_path):
    assert runner.invoke(app, ["profile", "check", "nope"]).exit_code == 2
    (tmp_path / "pyproject.toml").write_text("")
    none = runner.invoke(app, ["profile", "check"])
    assert none.exit_code == 2 and "no profile" in none.output
    refused = json.loads(runner.invoke(app, ["profile", "check", "nope", "--format", "json"]).output)
    assert refused["ok"] is False and "unknown profile" in refused["error"]


def test_a_path_that_holds_no_file_is_a_problem_of_the_profile():
    result = runner.invoke(app, ["profile", "check", "nowhere.yaml"])
    assert result.exit_code == 1 and "cannot read the file" in result.output
