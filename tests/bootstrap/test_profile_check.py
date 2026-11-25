"""`xarch profile check` through the real app: a profile is validated without an app, every problem at once, and the way
it differs from the profile it is based on is shown as information."""
import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from tests.bootstrap.project import retiring
from xarch.bootstrap.app import app
from xarch.modules.spec.domain.profile_keys import PART

runner = CliRunner()
KNOWN = "holds, imports, litmus, name, package_only, role, shared, tests, untested, uses"


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\n')
    runner.invoke(app, ["profile", "new", "mine", "--from", "web"])


COPY = "architecture/mine/mine.yaml"
XARCH = Path(__file__).parents[2] / "architecture.yaml"
"""xarch's own profile, based on cli."""


def part_of(document: dict, name: str) -> dict:
    """The part of the copied web profile named name, below its module folder."""
    module = document["parts"]["modules/<module>/"]
    return {"domain": module["domain/"], "logic": module["application/"]["logic/"],
            "services": module["application/"]["services/"]}[name]


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
    assert result.output.splitlines()[0] == f"checking {COPY} (custom; based_on: web)"
    for expected in ("loads: ok", "files: all", "examples: ok", "no looser than web", "OK: the profile is valid"):
        assert expected in result.output


def test_xarch_s_own_profile_is_compared_with_cli_the_profile_it_is_based_on_and_matches_it_at_80_percent():
    result = runner.invoke(app, ["profile", "check", str(XARCH)])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == f"checking {XARCH} (custom; based_on: cli)"
    assert lines[4:6] == [
        "  match: 80% with cli (based_on): 12 of 15 parts, 72 of 91 part keys, 21 of 31 tier entries, 11 of 11 guards, "
        "9 of 9 profile keys sit where both profiles have them",
        "    only here: parts main, profile-values, reports; tier wired. only in cli: tier rendering"]
    assert lines[6].startswith("  compared: looser than cli")
    compared = json.loads(runner.invoke(app, ["profile", "check", str(XARCH), "--format", "json"]).output)["compared_with"]
    assert {key: compared[key] for key in ("profile", "chosen_by", "match", "low", "counts", "higher")} == {
        "profile": "cli", "chosen_by": "based_on", "match": 0.8, "low": False,
        "counts": {"parts": [12, 15], "part_keys": [72, 91], "tiers": [21, 31], "guards": [11, 11], "profile": [9, 9]},
        "higher": None}


def test_an_unknown_key_fails_with_the_keys_that_exist(tmp_path):
    edit(tmp_path, lambda d: d.update(colour=1))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1
    assert "unknown key 'colour'" in result.output and "use based_on" in result.output
    assert "examples: not checked" in result.output and "INVALID: 1 problem" in result.output


def test_a_part_importing_a_part_that_does_not_exist_fails(tmp_path):
    edit(tmp_path, lambda d: part_of(d, "domain").update(imports={"may": ["parts.kernel", "parts.ghost"]}))
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
    edit(tmp_path, lambda d: part_of(d, "domain").update(imports={"may": ["parts.kernel", "parts.platform"]}))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 0, result.output
    assert "looser than web" in result.output
    assert "domain may also import parts.platform (parts.domain.imports.may)" in result.output
    shown = json.loads(runner.invoke(app, ["profile", "check", COPY, "--format", "json"]).output)
    assert shown["compared_with"]["looser"] == [
        {"key": "imports.may", "part": "domain", "what": "parts.platform",
         "sentence": "domain may also import parts.platform (parts.domain.imports.may)"}]


def test_each_public_name_a_copy_accepts_as_only_the_tests_is_a_way_it_is_looser(tmp_path):
    edit(tmp_path, lambda d: d["guards"]["dead-code"].update(tests_only=True, known=["kernel/ids.py:make"]))
    result = runner.invoke(app, ["profile", "check", COPY, "--format", "json"])
    assert result.exit_code == 0, result.output
    compared = json.loads(result.output)["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["match"]) == ("web", "based_on", 1.0)
    assert compared["looser"] == [
        {"key": "known", "part": "", "what": "kernel/ids.py:make",
         "sentence": "the tests-only check accepts kernel/ids.py:make as a name only the tests use (guards.dead-code.known)"}]


def test_json_gives_ok_the_problems_by_check_the_files_and_the_difference(tmp_path):
    good = json.loads(runner.invoke(app, ["profile", "check", COPY, "--format", "json"]).output)
    assert good["ok"] is True and good["profile"] == COPY and good["problems"] == [] and good["files"] > 10
    assert good["compared_with"] == {
        "profile": "web", "chosen_by": "based_on", "match": 1.0, "low": False,
        "counts": {"parts": [12, 12], "part_keys": [69, 69], "tiers": [17, 17], "guards": [11, 11], "profile": [6, 6]},
        "only_here": [], "only_there": [], "elsewhere": [], "higher": None, "anchor": "web", "looser": []}
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


SERVICE = "class Publishing:\n    def publish(self, doc):\n        if not doc.title:\n            raise ValueError(doc)\n"
ASKING = "class Publishing:\n    def publish(self, doc):\n        doc.publish()\n"


def rule(**changes) -> dict:
    return {"ask": "Does this method test the document's fields to decide whether it may change?",
            "answer": "yes-no", "yes": "it tests the fields itself", "no": "it asks the document", "reads": "function",
            "keep": ["public"], "message": "{name} may decide a rule of the document ({value})",
            "fix": "read it against the litmus of its part",
            "examples": {"flagged": {"modules/documents/a.py": SERVICE, "modules/documents/b.py": SERVICE},
                         "clean": {"modules/documents/a.py": ASKING, "modules/documents/b.py": ASKING}}} | changes


def test_an_eval_of_the_profile_own_is_valid_and_one_written_wrong_fails_at_its_address(tmp_path):
    edit(tmp_path, lambda d: d.update(evals={"rule-of-state": rule()}))
    assert runner.invoke(app, ["profile", "check", COPY]).exit_code == 0
    edit(tmp_path, lambda d: d.update(evals={"rule-of-state": rule(answer={"choice": {"a": "x", "b": "y"},
                                                                           "flagged": ["a"]})}))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1
    assert ("evals.rule-of-state.answer.choice: two options are a yes or no: write answer: yes-no, with yes: and no:"
            in result.output)


def test_an_example_in_which_an_eval_reads_nothing_fails_at_its_address(tmp_path):
    examples = {"flagged": {"modules/documents/a.py": SERVICE, "modules/documents/b.py": "VALUE = 1\n"},
                "clean": {"modules/documents/a.py": ASKING, "modules/documents/b.py": ASKING}}
    edit(tmp_path, lambda d: d.update(evals={"rule-of-state": rule(examples=examples)}))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1
    assert ("evals.rule-of-state.examples.flagged.modules/documents/b.py: holds no function the eval reads (in its "
            "scope, passing keep): give it one") in result.output


def test_a_key_xarch_retired_fails_like_any_profile_that_does_not_load_with_its_fixed_text(tmp_path, monkeypatch):
    retiring(monkeypatch, PART, "tested_by", "renamed in 0.3.0: write tier")
    edit(tmp_path, lambda d: part_of(d, "domain").update(tested_by="unit"))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1
    assert f"parts.domain: unknown key 'tested_by': renamed in 0.3.0: write tier; use {KNOWN}" in result.output
    assert "examples: not checked" in result.output and "INVALID: 1 problem" in result.output


def test_a_profile_writing_holds_as_one_word_or_names_on_a_part_fails_like_any_profile_that_does_not_load(tmp_path):
    def old(document: dict) -> None:
        part_of(document, "logic")["holds"] = "functions"
        part_of(document, "services")["holds"] = {"classes": {}}
        part_of(document, "services")["names"] = "*Service"
    edit(tmp_path, old)
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 1
    assert ("parts.logic.holds: 'functions': holds as one word was removed in 0.3.0: write holds: {functions: {}, "
            "records: {}, exceptions: {}}, which allows what holds: functions allowed") in result.output
    assert ("parts.services: unknown key 'names': moved in 0.3.0: write it under the kind it names, such as holds: "
            '{classes: {names: "*Service"}}; use ' + KNOWN) in result.output
    assert "examples: not checked: the profile does not load" in result.output
    checked = runner.invoke(app, ["check", "--profile", COPY])
    assert checked.exit_code == 2


AGAINST_WEB = ("  match: 73% with web (--against): 11 of 16 parts, 67 of 96 part keys, 21 of 31 tier entries, 11 of 11 "
               "guards, 9 of 9 profile keys sit where both profiles have them")
"""The match of xarch's own profile with web, computed on the 0.3.0 profiles."""


def test_xarch_s_own_profile_against_web_is_compared_with_web_for_the_run_and_its_match_is_low():
    result = runner.invoke(app, ["profile", "check", str(XARCH), "--against", "web"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == f"checking {XARCH} (custom; against web, given with --against; based_on: cli)"
    assert lines[4:7] == [
        AGAINST_WEB,
        "    only here: parts cli, main, profile-values, reports; tier wired. only in web: part web; tier rendering",
        "    low: 27% of what check reads under either profile has nothing to compare with in the other, so the list "
        "below says little about how check would do under web"]
    assert lines[7].startswith("  compared: looser than web")
    document = json.loads(runner.invoke(app, ["profile", "check", str(XARCH), "--against", "web", "--format",
                                              "json"]).output)
    assert {key: document["compared_with"][key] for key in ("profile", "chosen_by", "match", "low", "higher")} == {
        "profile": "web", "chosen_by": "against", "match": 0.73, "low": True, "higher": None}


def test_a_bundled_profile_against_another_is_compared_with_it():
    result = runner.invoke(app, ["profile", "check", "cli", "--against", "web"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == "checking cli (bundled; against web, given with --against)"
    assert lines[4] == ("  match: 89% with web (--against): 11 of 13 parts, 64 of 74 part keys, 16 of 18 tier entries, "
                        "11 of 11 guards, 6 of 6 profile keys sit where both profiles have them")
    document = json.loads(runner.invoke(app, ["profile", "check", "cli", "--against", "web", "--format", "json"]).output)
    assert (document["compared_with"]["profile"], document["compared_with"]["chosen_by"]) == ("web", "against")


def test_against_a_path_is_read_from_the_working_folder():
    result = runner.invoke(app, ["profile", "check", "cli", "--against", COPY])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == f"checking cli (bundled; against {COPY}, given with --against)"
    assert lines[4].startswith(f"  match: 89% with {COPY} (--against): 11 of 13 parts")


def test_against_a_profile_that_does_not_load_refuses_the_run(tmp_path):
    (tmp_path / "bad.yaml").write_text("name: x\n")
    text = runner.invoke(app, ["profile", "check", "--against", "bad.yaml"])
    assert text.exit_code == 2
    assert "error: --against does not load: bad.yaml: missing `parts`" in text.output
    document = json.loads(runner.invoke(app, ["profile", "check", "--against", "bad.yaml", "--format", "json"]).stdout)
    assert document == {"ok": False, "error": "--against does not load: bad.yaml: missing `parts`"}


def test_a_profile_that_does_not_load_is_reported_as_it_is_and_against_is_not_read(tmp_path):
    (tmp_path / "bad.yaml").write_text("name: x\n")
    result = runner.invoke(app, ["profile", "check", "bad.yaml", "--against", "nosuch"])
    assert result.exit_code == 1
    assert "missing `parts`" in result.output and "--against" not in result.output


TEAM = "architecture/team/team.yaml"
"""A copy of cli beside the copy of web, for the copy of web to be based on by its path."""


def based_on_team(tmp_path):
    """The copy of web based on a copy of cli by the path ../team/team.yaml, from the copy's own folder."""
    assert runner.invoke(app, ["profile", "new", "team", "--from", "cli"]).exit_code == 0
    edit(tmp_path, lambda d: d.update(based_on="../team/team.yaml"))


def test_a_copy_based_on_a_profile_file_is_compared_with_it_and_rests_on_the_bundled_profile_that_file_is_based_on(
        tmp_path):
    based_on_team(tmp_path)
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == f"checking {COPY} (custom; based_on: ../team/team.yaml, resting on cli)"
    assert "with ../team/team.yaml (based_on): " in result.output
    compared = json.loads(runner.invoke(app, ["profile", "check", COPY, "--format", "json"]).output)["compared_with"]
    assert (compared["profile"], compared["chosen_by"], compared["anchor"]) == ("../team/team.yaml", "based_on", "cli")


def test_a_based_on_path_is_read_from_the_profile_s_folder_whatever_the_working_folder(tmp_path, monkeypatch):
    based_on_team(tmp_path)
    (tmp_path / "elsewhere").mkdir()
    monkeypatch.chdir(tmp_path / "elsewhere")
    result = runner.invoke(app, ["profile", "check", str(tmp_path / COPY)])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == (
        f"checking {tmp_path / COPY} (custom; based_on: ../team/team.yaml, resting on cli)")


def test_a_based_on_path_that_names_no_file_refuses_the_profile(tmp_path):
    edit(tmp_path, lambda d: d.update(based_on="../team/team.yaml"))
    result = runner.invoke(app, ["profile", "check", COPY])
    assert result.exit_code == 2
    assert f"error: {COPY}: based_on: ../team/team.yaml does not load: {TEAM}: cannot read the file" in result.output
