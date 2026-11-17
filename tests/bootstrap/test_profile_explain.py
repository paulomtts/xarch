"""`xarch profile explain` through the real app: the whole format on one screen, one key in full, a key that does not
exist refused with the nearest ones, the same as JSON, and the folder tree and import table of a profile."""
import json

import pytest
from typer.testing import CliRunner

from tests.bootstrap.project import bundled_profiles
from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers

runner = CliRunner()


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_with_no_key_the_whole_format_is_one_screen_with_the_shape_the_symbols_and_the_smallest_profile():
    result = runner.invoke(app, ["profile", "explain"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert any(line.startswith("parts") and "required" in line and "enforced" in line for line in lines)
    assert any(line.strip().startswith("parts.may_import") for line in lines)
    assert "symbols" in result.output and "<word>" in result.output and "@any" in result.output
    assert "smallest valid profile" in result.output and "\n  xarch: 2\n" in result.output
    assert "xarch profile explain parts.may_import" in result.output
    assert len(lines) < 100 and max(map(len, lines)) <= 120


def test_a_key_is_explained_with_what_it_accepts_whether_check_enforces_it_through_which_rule_and_an_example():
    result = runner.invoke(app, ["profile", "explain", "parts.may_import"])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "parts.may_import"
    for expected in ("in: parts.<part>", "accepts:", "required: no", "enforced: yes, by the rule `rules`", "example:",
                     "may_import: [core]", "keys: none"):
        assert expected in result.output


def test_a_key_that_holds_keys_lists_them_and_a_guard_is_explained_by_its_name():
    held = runner.invoke(app, ["profile", "explain", "fakes"])
    assert "fakes.folder" in held.output and "required" in held.output
    guard = runner.invoke(app, ["profile", "explain", "guards.no-duplicates"])
    assert guard.exit_code == 0 and "enforced: yes, by the rule `no-duplicates`" in guard.output
    assert "guards.no-duplicates.min_statements" in guard.output


def test_a_key_that_names_something_xarch_ships_says_which():
    result = runner.invoke(app, ["profile", "explain", "testing"])
    assert "one of: " in result.output and any(name in result.output for name in ("pytest",))


def test_a_key_the_format_does_not_have_is_refused_with_the_nearest_keys():
    result = runner.invoke(app, ["profile", "explain", "parts.may_imports"])
    assert result.exit_code == 2
    assert "error: no key `parts.may_imports` in the format: the nearest are parts.may_import" in result.output


def test_a_key_of_the_format_is_explained_in_a_project_whose_pyproject_cannot_be_read(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.xarch\n")
    explained = runner.invoke(app, ["profile", "explain", "parts"])
    assert (explained.exit_code, explained.output.splitlines()[0]) == (0, "parts")
    unknown = runner.invoke(app, ["profile", "explain", "parts.may_imports"])
    assert unknown.exit_code == 2 and "cannot read" in unknown.output and "pyproject.toml" in unknown.output


def test_json_gives_the_shape_the_symbols_and_the_smallest_profile_and_for_a_key_the_fields_of_its_explanation():
    whole = json.loads(runner.invoke(app, ["profile", "explain", "--format", "json"]).output)
    assert whole["ok"] is True and whole["format"] == 2
    assert {"key": "parts.may_import", "depth": 1, "meaning": "what the part may import besides itself",
            "required": False, "enforced": True, "read_by": None} in whole["shape"]
    assert {"key": "review", "depth": 0, "meaning": "what `xarch review` may send: never, mask", "required": False,
            "enforced": False, "read_by": "review"} in whole["shape"]
    assert whole["symbols"][0]["symbol"] == "<word>" and whole["smallest"].startswith("xarch: 2")
    assert "xarch profile explain parts.may_import" in whole["deeper"]
    key = json.loads(runner.invoke(app, ["profile", "explain", "parts.may_import", "--format", "json"]).output)
    assert key["ok"] is True and key["key"] == "parts.may_import" and key["rules"] == ["rules"]
    assert set(key) == {"ok", "key", "where", "meaning", "accepts", "required", "enforced", "read_by", "rules",
                        "example", "choices", "keys", "needs", "language"}
    assert key["read_by"] is None
    refused = runner.invoke(app, ["profile", "explain", "parts.colour", "--format", "json"])
    assert refused.exit_code == 2
    assert json.loads(refused.output)["ok"] is False and json.loads(refused.output)["nearest"]


def test_every_key_the_overview_names_and_every_key_those_hold_can_be_asked_for_by_its_address():
    def ask(key):
        return json.loads(runner.invoke(app, ["profile", "explain", key, "--format", "json"]).output)

    pending = [shown["key"] for shown in json.loads(runner.invoke(app, ["profile", "explain", "--format", "json"]).output)["shape"]
               if shown["depth"] == 0]
    asked = []
    while pending:
        key = pending.pop()
        found = ask(key)
        asked.append(key)
        if key == "checks":
            assert found["ok"] is True and found["slots"] and found["example"]["check"].startswith("checks:")
            continue
        assert found["ok"] is True and found["key"] == key and found["example"], key
        pending += [held["key"] for held in found["keys"]]
    assert len(asked) == len(set(asked)) > 80


def test_what_review_may_send_is_read_by_review_alone_and_its_keys_are_listed_in_its_own_explanation():
    overview = runner.invoke(app, ["profile", "explain"]).output.splitlines()
    assert [line.split()[:3] for line in overview if line.split()[:1] in (["review"], ["review.never"])] == [
        ["review", "optional", "review"]]
    found = runner.invoke(app, ["profile", "explain", "review"]).output.splitlines()
    assert ("  enforced: no: check never acts on it (written wrong, the profile is invalid for every command); only xarch "
            "review reads what it says") in found
    assert [line.split()[0] for line in found[found.index("  keys:") + 1:]] == ["review.never", "review.mask"]
    never = json.loads(runner.invoke(app, ["profile", "explain", "review.never", "--format", "json"]).output)
    assert (never["where"], never["enforced"], never["read_by"], never["rules"]) == ("review", False, "review", [])


def test_review_never_says_it_holds_back_the_profile_s_own_examples_from_a_calibration_too():
    never = json.loads(runner.invoke(app, ["profile", "explain", "review.never", "--format", "json"]).output)
    assert ("The profile's own examples are covered too (a file of `docs.examples` or `evals.placement.examples`, an "
            "example of an eval of its own, by its path below the app): `review calibrate`, `--dry-run` included, "
            "never sends one it matches") in " ".join(never["accepts"].split())


def test_how_review_reads_what_it_asks_is_read_by_review_alone_down_to_the_line_of_each_part():
    overview = runner.invoke(app, ["profile", "explain"]).output.splitlines()
    assert [line.split()[:3] for line in overview if line.split()[:1] in (["evals"], ["evals.placement"])] == [
        ["evals", "optional", "review"]]
    evals = runner.invoke(app, ["profile", "explain", "evals"]).output.splitlines()
    assert [line.split()[0] for line in evals[evals.index("  keys:") + 1:]] == ["evals.placement", *(
        f"evals.<id>.{slot}" for slot in ("ask", "answer", "yes", "no", "reads", "in", "keep", "line", "message", "fix",
                                          "examples"))]
    ask = json.loads(runner.invoke(app, ["profile", "explain", "evals.title-rule.ask", "--format", "json"]).output)
    assert (ask["key"], ask["where"], ask["required"], ask["enforced"], ask["read_by"]) == (
        "evals.<id>.ask", "evals.<id>", True, False, "review")
    assert runner.invoke(app, ["profile", "explain", "evals.<id>.ask"]).output.splitlines()[0] == "evals.<id>.ask"
    assert runner.invoke(app, ["profile", "explain", "evals.ask"]).exit_code == 2
    lines = json.loads(runner.invoke(app, ["profile", "explain", "evals.placement.lines", "--format", "json"]).output)
    assert (lines["where"], lines["enforced"], lines["read_by"]) == ("evals.placement", False, "review")


def test_a_profile_is_shown_as_its_folder_tree_and_its_import_table_for_a_human_to_approve():
    result = runner.invoke(app, ["profile", "explain", "--profile", "web"])
    assert result.exit_code == 0, result.output
    assert "web (bundled)" in result.output.splitlines()[0]
    assert "folders" in result.output and "<module>/" in result.output and "| Part | May import |" in result.output
    as_json = json.loads(runner.invoke(app, ["profile", "explain", "--profile", "web", "--format", "json"]).output)
    assert as_json["profile"] == "web" and "<module>/" in as_json["tree"] and "| Part |" in as_json["imports"]


def test_the_profile_the_project_configures_is_shown_with_configured(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\n')
    result = runner.invoke(app, ["profile", "explain", "--configured"])
    assert result.exit_code == 0 and "cli (bundled)" in result.output.splitlines()[0]


def test_a_key_and_a_profile_together_or_no_configured_profile_is_refused(tmp_path):
    both = runner.invoke(app, ["profile", "explain", "parts", "--profile", "web"])
    assert both.exit_code == 2 and "either a key or a profile" in both.output
    none = runner.invoke(app, ["profile", "explain", "--configured"])
    assert none.exit_code == 2 and "no profile" in none.output


def test_the_bundled_profiles_the_choices_name_are_the_ones_xarch_ships():
    shipped = bundled_profiles()
    based = json.loads(runner.invoke(app, ["profile", "explain", "based_on", "--format", "json"]).output)
    assert tuple(based["choices"]) == shipped and f"based_on: {shipped[0]}" in based["example"]


@pytest.mark.parametrize("bundled", bundled_profiles())
def test_the_agent_instructions_every_bundled_profile_ships_say_that_xarch_profile_explain_exists(bundled):
    text = next(f.content for f in build_controllers().spec.files(bundled, "app").files if f.path == ("AGENTS.md",))
    assert "xarch profile explain" in text and "xarch profile check" in text


def test_the_rule_of_a_key_review_alone_reads_is_refused_saying_review_reads_it():
    result = runner.invoke(app, ["profile", "explain", "evals.placement.lines", "--rule", "--profile", "cli"])
    assert result.exit_code == 2
    assert "check makes no rule of it: only xarch review reads what it says" in result.output
