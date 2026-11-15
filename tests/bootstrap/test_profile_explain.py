"""`xarch profile explain` through the real app: the whole format on one screen, one key in full, a key that does not
exist refused with the nearest ones, the same as JSON, and the folder tree and import table of a profile."""
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_spec

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


def test_json_gives_the_shape_the_symbols_and_the_smallest_profile_and_for_a_key_the_fields_of_its_explanation():
    whole = json.loads(runner.invoke(app, ["profile", "explain", "--format", "json"]).output)
    assert whole["ok"] is True and whole["format"] == 2
    assert {"key": "parts.may_import", "depth": 1, "meaning": "what the part may import besides itself",
            "required": False, "enforced": True} in whole["shape"]
    assert whole["symbols"][0]["symbol"] == "<word>" and whole["smallest"].startswith("xarch: 2")
    key = json.loads(runner.invoke(app, ["profile", "explain", "parts.may_import", "--format", "json"]).output)
    assert key["ok"] is True and key["key"] == "parts.may_import" and key["rules"] == ["rules"]
    assert set(key) == {"ok", "key", "where", "meaning", "accepts", "required", "enforced", "rules", "example",
                        "choices", "keys"}
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
        assert found["ok"] is True and found["key"] == key and found["example"], key
        asked.append(key)
        pending += [held["key"] for held in found["keys"]]
    assert len(asked) == len(set(asked)) > 80


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
    shipped = build_spec().profiles()
    based = json.loads(runner.invoke(app, ["profile", "explain", "based_on", "--format", "json"]).output)
    assert tuple(based["choices"]) == shipped and f"based_on: {shipped[0]}" in based["example"]


@pytest.mark.parametrize("bundled", build_spec().profiles())
def test_the_agent_instructions_every_bundled_profile_ships_say_that_xarch_profile_explain_exists(bundled):
    text = next(f.content for f in build_spec().files(bundled, "app") if f.path == ("AGENTS.md",))
    assert "xarch profile explain" in text and "xarch profile check" in text
