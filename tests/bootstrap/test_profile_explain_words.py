"""`xarch profile explain` through the real app for the words a check is written in: how a check reads, a category, a
word with an example from a bundled profile's own rules, the rules a key expands to as checks, a word that does not
exist refused with the nearest ones (a key that does not exist with the nearest words too), and all of it as JSON."""
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def explain(*args: str):
    return runner.invoke(app, ["profile", "explain", *args])


def test_checks_is_how_a_check_reads_on_one_screen_with_its_slots_its_words_and_an_example():
    result = explain("checks")
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert lines[0] == "how a check reads" and "slots" in lines and "words" in lines
    assert any(line.startswith("  filters ") for line in lines)
    assert "example: a check of your own, checks.no-todo" in result.output and "      examples:" in lines
    assert len(lines) < 80


def test_a_category_lists_its_words_and_a_word_is_explained_with_an_example_from_a_bundled_profile():
    category = explain("filters")
    assert category.exit_code == 0 and "  public " in category.output
    word = explain("filters.public")
    assert word.exit_code == 0, word.output
    assert word.output.splitlines()[:4] == [
        "filters.public", "  what: the name the fact carries is public in the language: it does not start as a private "
                          "name", "    does", "  about: the fact"]
    assert "example: the rule parts.services.names of cli expands to" in word.output


def test_a_key_with_rule_shows_the_rules_it_expands_to_in_the_profile_given_as_checks():
    result = explain("parts.names", "--rule", "--profile", "web")
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "parts.names expands to 2 rules in web, written as checks:"
    assert "  names-services:" in result.output and "may_only: {name: [\"*Service\"]}" in result.output
    none = explain("parts.path", "--rule", "--profile", "web")
    assert none.exit_code == 2 and "parts.path in web: it expands to no rule of the engine here" in none.output


def test_a_word_that_does_not_exist_is_refused_with_the_nearest_and_so_is_a_key_with_the_nearest_words():
    word = explain("filters.publik")
    assert word.exit_code == 2
    assert "error: no word `filters.publik` of a check: the nearest are filters.public" in word.output
    key = explain("public")
    assert key.exit_code == 2 and "of the words of a check, filters.public" in key.output


def test_json_gives_each_of_them_as_one_document():
    checks = json.loads(explain("checks", "--format", "json").output)
    assert checks["ok"] is True and checks["slots"][0]["name"] == "read" and checks["example"]["profile"] is None
    word = json.loads(explain("kinds.call", "--format", "json").output)
    assert (word["name"], word["verb"], word["needs"]) == ("call", "call", ["call"])
    assert {"name": "place", "meaning": "where what it leads to sits: a part, or a folder of the layout",
            "when": "target-placed"} in word["fields"]
    rule = json.loads(explain("parts.names", "--rule", "--profile", "cli", "--format", "json").output)
    assert rule["ok"] is True and rule["rules"] == 2 and rule["checks"].startswith("checks:")
    refused = explain("filters.publik", "--format", "json")
    assert refused.exit_code == 2 and json.loads(refused.output)["nearest"][0] == "filters.public"


@pytest.mark.parametrize("configured, said", [
    pytest.param('profile = "nope"', "error: unknown profile 'nope' in {pyproject}: use one of cli, web",
                 id="an unknown profile"),
    pytest.param('profile = "broken.yaml"', "error: {folder}/broken.yaml: missing `parts`",
                 id="a profile that does not load"),
])
def test_a_word_asked_in_a_project_whose_configured_profile_cannot_be_used_is_refused_with_why(tmp_path, configured,
                                                                                                said):
    (tmp_path / "pyproject.toml").write_text(f"[tool.xarch]\n{configured}\n", encoding="utf-8")
    (tmp_path / "broken.yaml").write_text("name: broken\n", encoding="utf-8")
    result = explain("filters.public")
    assert (result.exit_code, result.output) == (
        2, said.format(pyproject=tmp_path / "pyproject.toml", folder=tmp_path) + "\n")


def test_a_part_s_never_list_and_a_tier_s_switch_expand_to_the_rules_never_use():
    listed = explain("parts.uses.never", "--rule", "--profile", "web")
    assert listed.exit_code == 0, listed.output
    assert listed.output.splitlines()[0] == "parts.uses.never expands to 22 rules in web, written as checks:"
    assert "  never-use-domain:" in listed.output
    switch = explain("tiers.uses.apply_never", "--rule", "--profile", "web")
    assert switch.output.splitlines()[0] == "tiers.uses.apply_never expands to 11 rules in web, written as checks:"
