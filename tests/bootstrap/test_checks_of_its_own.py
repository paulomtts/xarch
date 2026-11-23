"""Checks a profile writes itself, through the real app: `profile check` holds each to its words and its examples,
`check` runs it and lists it under `enforcement` with how much it read (one that read nothing fails `--strict`), a
check whose words do not exist or do not apply is refused by `check` with every problem and listed by `profile check`
while the others are still held and counted, a hint may name it, the same rule
written by a key and by hand finds the same, and `profile explain` says what each slot the format reads means, in its
order."""
import json

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
CHECK = {"read": "class", "in": {"part": "store"}, "keep": ["public"], "may_only": {"name": ["*Store"]},
         "message": "{name} is no store, as every class of {where} is ({key})",
         "fix": "rename {name} to end in Store", "examples": {"flagged": {"store/x.py": "class Thing: ...\n"},
                                                              "clean": {"store/x.py": "class DocumentStore: ...\n"}}}


def project(tmp_path, checks: dict, files: dict[str, str], **extra) -> None:
    profile = {"name": "mine", "parts": {"store": {"path": "store", "role": "saves documents", **extra}},
               "checks": checks}
    (tmp_path / "mine.yaml").write_text(yaml.safe_dump(profile, sort_keys=False))
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "mine.yaml"\n')
    for path, text in files.items():
        (tmp_path / "app" / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "app" / path).write_text(text)


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_profile_check_runs_each_check_s_examples_and_check_finds_what_it_is_written_to(tmp_path):
    project(tmp_path, {"store-names": CHECK}, {"store/a.py": "class Thing: ...\n", "store/b.py": "class DocStore: ...\n"})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 0, checked.output
    assert "  checks: ok: its check finds what its examples say" in checked.output
    found = runner.invoke(app, ["check", "--format", "json"])
    document = json.loads(found.output)
    assert [(v["rule"], v["file"], v["line"], v["message"]) for v in document["violations"]] == [
        ("store-names", "app/store/a.py", 1, "Thing is no store, as every class of store/ is (checks.store-names)")]
    assert document["enforcement"]["checks"] == [{"id": "store-names", "read": 2,
                                                 "said": "checks.store-names read 2 facts"}]


def test_a_check_that_reads_nothing_is_listed_and_fails_strict(tmp_path):
    project(tmp_path, {"store-names": CHECK}, {"store/a.py": "x = 1\n"})
    found = runner.invoke(app, ["check", "--strict"])
    assert found.exit_code == 1
    assert ("  reads nothing: checks.store-names reads nothing in the project, so it passes for want of anything to "
            "check: widen what it reads, or drop it") in found.output
    assert runner.invoke(app, ["check"]).exit_code == 0


@pytest.mark.parametrize("changes, said", [
    pytest.param({"keep": ["publc"]}, "checks.store-names.keep: no filter is named 'publc': did you mean public or "
                                      "placed?", id="a filter misspelt"),
    pytest.param({"keep": ["public", "receiver"]},
                 "checks.store-names.keep: receiver does not apply to class: it reads receiver, which it does not "
                 "carry; it applies to callback", id="a filter the kind does not carry"),
    pytest.param({"examples": {"flagged": {"store/x.py": "class ThingStore: ...\n"},
                               "clean": {"store/x.py": "class Thing: ...\n"}}},
                 "checks.store-names.examples.flagged: the check finds nothing in it: make the code hold what the "
                 "check is written to find, or correct the check", id="an example that does not fire"),
])
def test_a_check_broken_is_said_by_profile_check_at_its_address(tmp_path, changes, said):
    project(tmp_path, {"store-names": {**CHECK, **changes}}, {"store/a.py": "class Thing: ...\n"})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 1 and f"    {said}" in checked.output.splitlines()


def test_a_check_badly_written_does_not_stop_profile_check_counting_every_check_and_holding_the_others(tmp_path):
    misfiring = {**CHECK, "examples": {"flagged": {"store/x.py": "class ThingStore: ...\n"},
                                       "clean": {"store/x.py": "class DocumentStore: ...\n"}}}
    project(tmp_path, {"misspelt": {**CHECK, "keep": ["publc"]}, "store-names": misfiring}, {})
    checked = runner.invoke(app, ["profile", "check", "--format", "json"])
    assert checked.exit_code == 1
    document = json.loads(checked.output)
    assert (document["checks"], document["problems"]) == (2, [
        {"check": "checks", "message": "checks.misspelt.keep: no filter is named 'publc': did you mean public or "
                                       "placed?"},
        {"check": "checks", "message": "checks.store-names.examples.flagged: the check finds nothing in it: make the "
                                       "code hold what the check is written to find, or correct the check"}])


def test_the_slots_profile_explain_says_the_meaning_of_are_the_slots_the_format_reads_in_its_order(tmp_path):
    explained = runner.invoke(app, ["profile", "explain", "checks", "--format", "json"])
    project(tmp_path, {"store-names": 5}, {})
    checked = runner.invoke(app, ["profile", "check", "--format", "json"])
    (problem,) = json.loads(checked.output)["problems"]
    read = problem["message"].split("checks.store-names: must be a map of slots: ")[1].split(", ")
    assert [slot["name"] for slot in json.loads(explained.output)["slots"]] == read

def test_a_check_whose_words_do_not_exist_stops_check_with_every_problem(tmp_path):
    project(tmp_path, {"store-names": {**CHECK, "keep": ["publc"], "mode": "fial"}}, {"store/a.py": "x = 1\n"})
    found = runner.invoke(app, ["check"])
    assert found.exit_code == 2
    assert "error: the checks the profile writes itself cannot run" in found.output
    assert "checks.store-names.mode: is 'fial'" in found.output and "'publc'" in found.output


def test_an_id_of_a_check_xarch_has_is_refused_and_a_hint_may_name_a_check_of_the_profile_s_own(tmp_path):
    project(tmp_path, {"names": CHECK}, {})
    refused = runner.invoke(app, ["profile", "check"])
    assert refused.exit_code == 1 and "checks.names: names is the id of a check xarch has" in refused.output
    project(tmp_path, {"store-names": CHECK}, {"store/a.py": "class Thing: ...\n"})
    document = yaml.safe_load((tmp_path / "mine.yaml").read_text())
    document["hints"] = {"store-names": "a store saves, so its name says so"}
    (tmp_path / "mine.yaml").write_text(yaml.safe_dump(document, sort_keys=False))
    found = json.loads(runner.invoke(app, ["check", "--format", "json"]).output)
    assert found["violations"][0]["hint"] == "a store saves, so its name says so"


def test_the_same_rule_written_by_a_key_and_by_hand_finds_the_same(tmp_path):
    files = {"store/a.py": "class Thing: ...\nclass DocStore: ...\n"}
    project(tmp_path, {}, files, holds={"classes": {"names": "*Store"}})
    by_key = json.loads(runner.invoke(app, ["check", "--format", "json"]).output)["violations"]
    written = yaml.safe_load(json.loads(runner.invoke(app, ["profile", "explain", "parts.names", "--rule",
                                                            "--format", "json"]).output)["checks"])["checks"]
    ((name, body),) = written.items()
    project(tmp_path, {name: {**body, "examples": CHECK["examples"]}}, files)
    by_hand = json.loads(runner.invoke(app, ["check", "--format", "json"]).output)["violations"]
    assert [v["rule"] for v in by_key] == ["names"] and [v["rule"] for v in by_hand] == ["names-store"]
    assert [{**v, "rule": "", "message": v["message"].replace("checks.names-store", "parts.store.names")}
            for v in by_hand] == [{**v, "rule": ""} for v in by_key]
