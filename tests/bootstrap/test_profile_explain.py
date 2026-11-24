"""`xarch profile explain` through the real app: the whole format on one screen, one key in full, a key that does not
exist refused with the nearest ones, the same as JSON, and the folder tree and import table of a profile."""
import json

import pytest
from typer.testing import CliRunner

from tests.bootstrap.project import bundled_profiles, retiring
from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_controllers, load_architecture
from xarch.modules.spec.domain.profile_keys import PART
from xarch.profile_values.capabilities import FACTS
from xarch.profile_values.testing import ScenarioCoverage

runner = CliRunner()

RENAMED = "renamed in 0.3.0: write tier"


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_with_no_key_the_whole_format_is_one_screen_with_the_shape_the_symbols_and_the_smallest_profile():
    result = runner.invoke(app, ["profile", "explain"])
    assert result.exit_code == 0, result.output
    lines = result.output.splitlines()
    assert any(line.startswith("parts") and "required" in line and "enforced" in line for line in lines)
    assert any(line.strip().startswith("parts.imports") for line in lines)
    assert "symbols" in result.output and "<word>" in result.output and "@any" in result.output
    assert "smallest valid profile" in result.output and "\n  name: documents-app\n" in result.output
    assert "xarch profile explain parts.imports.may" in result.output
    assert len(lines) < 100 and max(map(len, lines)) <= 120


def test_a_key_is_explained_with_what_it_accepts_whether_check_enforces_it_through_which_rule_and_an_example():
    result = runner.invoke(app, ["profile", "explain", "parts.imports.may"])
    assert result.exit_code == 0, result.output
    assert result.output.splitlines()[0] == "parts.imports.may"
    for expected in ("in: parts.<part>.imports", "accepts:", "required: no", "enforced: yes, by the rule `may-import`", "example:",
                     "may: [core]", "parts.imports.may.types_only"):
        assert expected in result.output


def test_the_example_of_hints_gives_advice_for_the_rule_may_import():
    result = runner.invoke(app, ["profile", "explain", "hints"])
    assert result.exit_code == 0, result.output
    assert "      may-import: Ask the maintainer before adding an import." in result.output.splitlines()


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
    assert "error: no key `parts.may_imports` in the format: the nearest are parts.imports" in result.output


def test_a_key_of_the_format_is_explained_in_a_project_whose_pyproject_cannot_be_read(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.xarch\n")
    explained = runner.invoke(app, ["profile", "explain", "parts"])
    assert (explained.exit_code, explained.output.splitlines()[0]) == (0, "parts")
    unknown = runner.invoke(app, ["profile", "explain", "parts.may_imports"])
    assert unknown.exit_code == 2 and "cannot read" in unknown.output and "pyproject.toml" in unknown.output


def test_json_gives_the_shape_the_symbols_and_the_smallest_profile_and_for_a_key_the_fields_of_its_explanation():
    whole = json.loads(runner.invoke(app, ["profile", "explain", "--format", "json"]).output)
    assert whole["ok"] is True and "format" not in whole
    assert {"key": "parts.imports", "depth": 1, "meaning": "what the part may and must import, and its outside packages",
            "required": False, "enforced": True, "read_by": None} in whole["shape"]
    assert {"key": "review", "depth": 0, "meaning": "what `xarch review` may send: never, mask", "required": False,
            "enforced": False, "read_by": "review"} in whole["shape"]
    assert whole["symbols"][0]["symbol"] == "<word>" and whole["smallest"].startswith("name: documents-app")
    assert "xarch profile explain parts.imports.may" in whole["deeper"]
    key = json.loads(runner.invoke(app, ["profile", "explain", "parts.imports.may", "--format", "json"]).output)
    assert key["ok"] is True and key["key"] == "parts.imports.may" and key["rules"] == ["may-import"]
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


def test_an_address_xarch_retired_is_refused_with_its_fixed_text_in_text_and_in_json(monkeypatch):
    retiring(monkeypatch, PART, "tested_by", RENAMED)
    text = runner.invoke(app, ["profile", "explain", "parts.<part>.tested_by"])
    assert text.exit_code == 2
    assert f"error: no key `parts.tested_by` in the format: {RENAMED}; the nearest are " in text.output
    found = runner.invoke(app, ["profile", "explain", "parts.tested_by", "--format", "json"])
    assert found.exit_code == 2
    document = json.loads(found.output)
    assert (document["ok"], document["key"], document["retired"]) == (False, "parts.tested_by", RENAMED)
    assert document["error"].startswith(f"no key `parts.tested_by` in the format: {RENAMED}; the nearest are ")


def test_a_key_of_the_format_is_explained_even_with_an_entry_at_its_address(monkeypatch):
    retiring(monkeypatch, PART, "imports", RENAMED)
    result = runner.invoke(app, ["profile", "explain", "parts.imports"])
    assert (result.exit_code, result.output.splitlines()[0]) == (0, "parts.imports")
    assert RENAMED not in result.output


def test_an_address_with_no_entry_is_refused_as_today_with_retired_null_in_json():
    text = runner.invoke(app, ["profile", "explain", "parts.colour"])
    assert text.exit_code == 2 and "error: no key `parts.colour` in the format: the nearest are " in text.output
    found = runner.invoke(app, ["profile", "explain", "parts.colour", "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] is None


@pytest.mark.parametrize("address", [pytest.param("rules", id="the bare rule id"),
                                     pytest.param("hints.rules", id="the rule id under hints")])
def test_the_rule_id_rules_has_no_address_and_is_refused_as_any_unknown_key(address):
    text = runner.invoke(app, ["profile", "explain", address])
    assert text.exit_code == 2 and f"error: no key `{address}` in the format: the nearest are " in text.output
    assert "may-import" not in text.output
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] is None


def test_an_address_xarch_retired_in_a_project_whose_profile_does_not_load_is_refused_with_why(tmp_path, monkeypatch):
    retiring(monkeypatch, PART, "tested_by", RENAMED)
    (tmp_path / "pyproject.toml").write_text("[tool.xarch\n")
    refused = runner.invoke(app, ["profile", "explain", "parts.tested_by"])
    assert refused.exit_code == 2 and "cannot read" in refused.output and "pyproject.toml" in refused.output
    assert RENAMED not in refused.output


SHIPPED = "renamed in 0.3.0: write tests"


def test_the_part_key_tier_is_refused_with_the_rename_in_text_and_in_json():
    text = runner.invoke(app, ["profile", "explain", "parts.tier"])
    assert text.exit_code == 2
    assert f"error: no key `parts.tier` in the format: {SHIPPED}; the nearest are " in text.output
    found = runner.invoke(app, ["profile", "explain", "parts.<part>.tier", "--format", "json"])
    assert found.exit_code == 2
    document = json.loads(found.output)
    assert (document["ok"], document["key"], document["retired"]) == (False, "parts.tier", SHIPPED)


def test_the_part_key_tests_and_the_tier_of_scenario_coverage_are_explained():
    tests = runner.invoke(app, ["profile", "explain", "parts.tests"])
    assert (tests.exit_code, tests.output.splitlines()[0]) == (0, "parts.tests")
    guard = runner.invoke(app, ["profile", "explain", "guards.scenario-coverage.tier"])
    assert (guard.exit_code, guard.output.splitlines()[0]) == (0, "guards.scenario-coverage.tier")
    assert SHIPPED not in tests.output + guard.output


@pytest.mark.parametrize("address", ["never", "parts.uses", "parts.uses.never", "tiers.uses", "tiers.uses.apply_never",
                                     "review.never"])
def test_never_its_groups_and_review_never_are_explained(address):
    found = runner.invoke(app, ["profile", "explain", address])
    assert (found.exit_code, found.output.splitlines()[0]) == (0, address)


@pytest.mark.parametrize("address, text", [
    pytest.param("forbidden", "renamed in 0.3.0: write never", id="the old block"),
    pytest.param("parts.forbidden", "moved in 0.3.0: write uses: {never: <list>}", id="the old part key"),
    pytest.param("tiers.apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}", id="the old tier key"),
    pytest.param("parts.never", "a key of uses: write uses: {never: <list>}", id="never on a part"),
    pytest.param("tiers.apply_never", "a key of uses: write uses: {apply_never: true}", id="apply_never on a tier"),
])
def test_an_old_name_of_never_is_refused_with_its_text_exit_2_and_retired_in_json(address, text):
    said = runner.invoke(app, ["profile", "explain", address])
    assert said.exit_code == 2
    assert f"error: no key `{address}` in the format: {text}; the nearest are " in said.output
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] == text


def test_never_says_an_entry_naming_a_list_includes_it_and_a_list_may_not_take_a_name_an_entry_reads_as():
    found = json.loads(runner.invoke(app, ["profile", "explain", "never", "--format", "json"]).output)
    accepts = " ".join(found["accepts"].split())
    for said in ("a map {<list>: [<dotted name> | <list>, ...]}",
                 "An entry that is exactly the name of another list of `never` includes that list's names in its "
                 "place, in order, however deep, and the list may be written below",
                 "a list may not include itself, nor reach a name or a list twice",
                 "A list may not take the name of a package of the Python standard library, nor of a package the "
                 "profile names in a part's `imports.libraries` or in `reserved`, since an entry of that name would name the "
                 "list"):
        assert said in accepts
    assert "  published: [pure, json.dumps]\n" in found["example"]
    assert "uses: {never: published}" in found["example"]
    shown = runner.invoke(app, ["profile", "explain", "never"])
    assert shown.exit_code == 0 and "published: [pure, json.dumps]" in shown.output


def test_the_mark_is_a_key_with_its_text_and_its_rule():
    found = runner.invoke(app, ["profile", "explain", "parts.imports.may.types_only", "--format", "json"])
    shown = json.loads(found.output)
    assert found.exit_code == 0 and shown["key"] == "parts.imports.may.types_only"
    assert shown["meaning"] == "a target of imports.may the part may use only as a type"
    assert shown["rules"] == ["types-only"]


def test_an_old_part_key_answers_with_the_form_that_replaces_it():
    found = runner.invoke(app, ["profile", "explain", "parts.may_import"])
    assert found.exit_code == 2
    assert "moved in 0.3.0: write imports: {may: [...]}" in found.output


@pytest.mark.parametrize("address, key", [
    pytest.param("tiers.imports.also", "tiers.imports.also", id="the plain address"),
    pytest.param("tiers.<tier>.imports.must", "tiers.imports.must", id="with the placeholder"),
    pytest.param("tiers.unit.imports.must", "tiers.imports.must", id="with a tier's name"),
])
def test_a_key_of_a_tier_s_group_is_explained_with_or_without_a_tier_name(address, key):
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 0 and json.loads(found.output)["key"] == key


def test_the_group_of_a_tier_lists_its_keys_and_the_rules_they_feed():
    shown = json.loads(runner.invoke(app, ["profile", "explain", "tiers.imports", "--format", "json"]).output)
    assert shown["rules"] == ["tiers", "must-import", "types-only"]
    assert json.loads(runner.invoke(app, ["profile", "explain", "tiers.imports.types_only", "--format",
                                          "json"]).output)["rules"] == ["types-only"]


@pytest.mark.parametrize("address, text", [
    pytest.param("tiers.may_import", "moved in 0.3.0: write imports: {may: [...]}", id="may_import"),
    pytest.param("tiers.may_also_import", "moved in 0.3.0: write imports: {also: [...]}", id="may_also_import"),
    pytest.param("tiers.must_import", "moved in 0.3.0: write imports: {must: [...]}", id="must_import"),
    pytest.param("tiers.types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}", id="types_only"),
])
def test_an_old_tier_key_answers_with_the_form_that_replaces_it(address, text):
    said = runner.invoke(app, ["profile", "explain", address])
    assert said.exit_code == 2 and f"error: no key `{address}` in the format: {text}; the nearest are " in said.output
    found = runner.invoke(app, ["profile", "explain", address, "--format", "json"])
    assert found.exit_code == 2 and json.loads(found.output)["retired"] == text


ACCEPTS = ("the name of a bundled profile, or the path of a profile file from this file's folder: `profile check` and "
           "`check` compare this one with it, unless `--against` names another for the run; `--strict` rests on a "
           "bundled profile: the chain's bundled root, else the bundled profile closest to its last file")
"""What based_on accepts, as `profile explain based_on` says it."""


def test_based_on_is_explained_as_a_bundled_name_or_a_profile_file_and_its_choices_stay_the_bundled_names():
    explained = json.loads(runner.invoke(app, ["profile", "explain", "based_on", "--format", "json"]).output)
    assert explained["accepts"] == ACCEPTS
    assert explained["meaning"] == "the profile this one is based on: a bundled one, or a profile file"
    assert tuple(explained["choices"]) == bundled_profiles()
    text = runner.invoke(app, ["profile", "explain", "based_on"])
    assert text.exit_code == 0 and "the path of a profile file from this file's folder" in " ".join(text.output.split())


def test_the_file_of_the_scenario_guard_is_explained_with_its_cases_and_its_example_loads(tmp_path):
    key = json.loads(runner.invoke(app, ["profile", "explain", "guards.scenario-coverage.file", "--format", "json"]).output)
    guard = json.loads(runner.invoke(app, ["profile", "explain", "guards.scenario-coverage", "--format", "json"]).output)
    (tmp_path / "example.yaml").write_text("name: documents-app\n" + key["example"])
    loaded = load_architecture(tmp_path / "example.yaml")
    assert key["accepts"] == ("a name holding {name:<case>} once, <case> one of snake, kebab, camel, pascal, for the "
                              "use case")
    assert "(`{name:<case>}` is <Name> in that case: snake, kebab, camel or pascal)" in guard["accepts"]
    assert [g.file for g in loaded.guards if isinstance(g, ScenarioCoverage)] == ["check_{name:snake}.py"]


def test_the_table_of_testing_is_answered_from_the_table_of_retired_names():
    found = runner.invoke(app, ["profile", "explain", "testing.table", "--format", "json"])
    assert (found.exit_code, json.loads(found.output)["retired"]) == (
        2, "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)")


def test_a_holder_of_a_table_form_says_the_fact_of_its_form_and_whether_python_supplies_it():
    call = json.loads(runner.invoke(app, ["profile", "explain", "testing.tables.call", "--format", "json"]).output)
    assert call["needs"] == [{"fact": "function.tables.call", "meaning": FACTS["function.tables.call"], "grade": "absent",
                              "note": None}]
    text = " ".join(runner.invoke(app, ["profile", "explain", "testing.tables.call"]).output.split())
    assert ("needs: function.tables.call: the facts of the source its check reads; Python supplies not "
            "function.tables.call") in text
    decorator = " ".join(runner.invoke(app, ["profile", "explain", "testing.tables.decorator"]).output.split())
    assert ("needs: function.tables.decorator: the facts of the source its check reads, which Python supplies "
            "exactly") in decorator


def test_the_list_of_table_forms_needs_no_fact_of_its_own():
    found = runner.invoke(app, ["profile", "explain", "testing.tables", "--format", "json"])
    assert json.loads(found.output)["needs"] == []
    text = runner.invoke(app, ["profile", "explain", "testing.tables"]).output
    assert not any(line.startswith("  needs:") for line in text.splitlines())


def test_the_loop_holder_of_a_table_form_says_python_supplies_its_fact_exactly():
    loop = json.loads(runner.invoke(app, ["profile", "explain", "testing.tables.loop", "--format", "json"]).output)
    assert loop["needs"] == [{"fact": "function.tables.loop", "meaning": FACTS["function.tables.loop"], "grade": "exact",
                              "note": None}]
    text = " ".join(runner.invoke(app, ["profile", "explain", "testing.tables.loop"]).output.split())
    assert ("needs: function.tables.loop: the facts of the source its check reads, which Python supplies "
            "exactly") in text
