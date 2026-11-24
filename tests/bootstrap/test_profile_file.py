"""A profile file through the real app: read from a file, its test framework taken from the preset shipped as
data, and its rules, outside packages and names enforced by the wired check; and the preset itself, which holds what
the bundled profiles spell out."""
from pathlib import Path

import pytest
from typer.testing import CliRunner

from tests.bootstrap.project import app_check, bundled_profiles
from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.profile_values.testing import ScenarioCoverage, StandIns
from xarch.profile_values.testing import TestForm as DeclaredForm

PROFILE = """\
name: small
language: python
testing: pytest
never:
  pure: [builtins.print]
parts:
  core:
    path: core
    role: the rules
    uses: {never: pure}
    tests: unit
  cli:
    path: cli
    role: commands and output
    imports:
      may: [core]
      libraries: [typer]
    tests: unit
tiers:
  unit: {}
"""
PRESET_PROFILE = """\
name: preset
testing: pytest
parts:
  results: {path: modules/<module>/results, role: the results, tests: unit}
  ports: {path: modules/<module>/ports, role: the ports, tests: unit}
tiers:
  unit: {}
fakes: {folder: fakes, for: [ports], prefix: Fake}
guards:
  stand-ins: {}
  scenario-coverage: {results: results, tier: unit, suffix: Result, columns: [given, when, then], file: "test_{name:snake}.py"}
"""
APP = {"__init__.py": "", "core/__init__.py": "", "cli/__init__.py": "", "core/rules.py": "X = 1\n",
       "cli/app.py": "import typer\nfrom app.core import rules\n"}


def profile_in(tmp_path: Path, text: str = PROFILE) -> Path:
    path = tmp_path / "small.yaml"
    path.write_text(text)
    return path


def check(tmp_path: Path, files: dict[str, str], text: str = PROFILE) -> list[str]:
    app = tmp_path / "app"
    for rel, body in {**APP, **files}.items():
        (app / rel).parent.mkdir(parents=True, exist_ok=True)
        (app / rel).write_text(body)
    return [str(v) for v in app_check(app, str(profile_in(tmp_path, text))).violations]


def test_a_conforming_app_passes_a_profile_file(tmp_path):
    assert check(tmp_path, {}) == []


def test_the_rules_of_a_profile_file_are_enforced(tmp_path):
    assert check(tmp_path, {"core/rules.py": "from app.cli import app\n"}) == [
        "app/core/rules.py:1: core/ may not import cli/ (app.cli.app)"]


def test_libraries_are_strict_by_default(tmp_path):
    assert check(tmp_path, {"core/rules.py": "import typer\n", "cli/app.py": "import yaml\n"}) == [
        "app/cli/app.py:1: cli/ may not import the outside package yaml (parts.cli.imports.libraries)",
        "app/core/rules.py:1: core/ may not import the outside package typer (parts.core.imports.libraries)"]


def test_the_names_a_part_forbids_are_enforced(tmp_path):
    assert check(tmp_path, {"core/rules.py": "print(1)\n"}) == [
        "app/core/rules.py:1: core/ may not use builtins.print (parts.core.uses.never)"]


def test_the_preset_is_read_from_the_data_file_beside_the_bundled_profiles(tmp_path):
    architecture = load_architecture(profile_in(tmp_path))
    assert architecture.framework is not None
    assert architecture.framework.files == ("test_*.py", "*_test.py")
    assert architecture.framework.declared == (DeclaredForm(function="test_*"),)


def test_a_preset_that_does_not_exist_is_refused_listing_the_ones_that_do(tmp_path):
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: rspec")))
    assert caught.value.problems == (
        f"{tmp_path / 'small.yaml'}: testing: no preset 'rspec': use pytest, or write the map {{files, declared}}",)


MAPPED = PROFILE.replace("testing: pytest", "testing: {preset: pytest}")


def test_a_map_naming_the_preset_loads_and_checks_as_the_preset_by_name(tmp_path):
    assert load_architecture(profile_in(tmp_path, MAPPED)) == load_architecture(profile_in(tmp_path))
    assert check(tmp_path, {"core/rules.py": "from app.cli import app\n"}, MAPPED) == [
        "app/core/rules.py:1: core/ may not import cli/ (app.cli.app)"]


def test_the_guards_that_read_tests_read_the_same_under_a_map_naming_the_preset(tmp_path):
    named = load_architecture(profile_in(tmp_path, PRESET_PROFILE))
    mapped = PRESET_PROFILE.replace("testing: pytest\n", "testing: {preset: pytest}\n")
    assert load_architecture(profile_in(tmp_path, mapped)) == named


def test_a_key_beside_the_shipped_preset_is_refused_naming_what_the_preset_gives(tmp_path):
    path = profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: pytest, files: [check_*.py]}"))
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: testing.files: the preset pytest gives files: drop it, or drop preset and write the whole map",)


def test_a_map_naming_a_preset_that_does_not_exist_is_refused_at_its_preset(tmp_path):
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: rspec}")))
    assert caught.value.problems == (
        f"{tmp_path / 'small.yaml'}: testing.preset: no preset 'rspec': use pytest, or write the map {{files, declared}}",)


def test_a_version_line_is_refused_as_an_unknown_key(tmp_path):
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(profile_in(tmp_path, "xarch: 2\n" + PROFILE))
    assert caught.value.problems == (
        f"{tmp_path / 'small.yaml'}: unknown key 'xarch': use based_on, checks, docs, evals, excluded, fakes, files, "
        "guards, hints, language, layers, name, never, parts, reserved, review, testing, tiers",)


def test_a_bundled_profile_may_not_be_a_preset():
    assert bundled_profiles() == ("cli", "web")


@pytest.mark.parametrize("name", ["cli", "web"])
def test_the_preset_holds_exactly_what_the_bundled_profiles_spell_out(name, tmp_path):
    """tests, the forms of a table, and the guards scenario-coverage and stand-ins."""
    spelled = load_architecture(name)
    preset = load_architecture(profile_in(tmp_path, PRESET_PROFILE))
    assert preset.framework == spelled.framework
    assert [g for g in preset.guards if isinstance(g, StandIns)] == [g for g in spelled.guards if isinstance(g, StandIns)]
    assert [g.file for g in preset.guards if isinstance(g, ScenarioCoverage)] == [
        g.file for g in spelled.guards if isinstance(g, ScenarioCoverage)]


def test_xarch_s_own_profile_spells_out_the_same_as_the_preset(tmp_path):
    spelled = load_architecture(Path(__file__).parent.parent.parent / "architecture.yaml")
    preset = load_architecture(profile_in(tmp_path, PRESET_PROFILE))
    assert preset.framework == spelled.framework
    assert [g for g in preset.guards if isinstance(g, StandIns)] == [g for g in spelled.guards if isinstance(g, StandIns)]
    assert [g.file for g in preset.guards if isinstance(g, ScenarioCoverage)] == [
        g.file for g in spelled.guards if isinstance(g, ScenarioCoverage)]


BARE = ("guards.scenario-coverage.file: 'test_{name}.py': {name} with no case was removed in 0.3.0: write "
        "{name:snake} for what {name} meant")


def test_a_bare_name_in_the_file_of_the_scenario_guard_is_refused_with_its_hint(tmp_path):
    path = profile_in(tmp_path, PRESET_PROFILE.replace("test_{name:snake}.py", "test_{name}.py"))
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    checked = CliRunner().invoke(app, ["profile", "check", str(path)])
    assert (caught.value.problems, checked.exit_code) == ((f"{path}: {BARE}",), 1)
    assert f"    {path}: {BARE}" in checked.output.splitlines()


OLD_TABLE_PROFILE = PRESET_PROFILE.replace("testing: pytest\n", 'testing:\n  files: ["test_*.py"]\n  declared: [{function: "test_*"}]\n'
                                           "  table: {decorator: pytest.mark.parametrize, row: pytest.param, id: id}\n")
RETIRED_TABLE = ("testing: unknown key 'table': moved in 0.3.0: write tables, a list of forms (xarch profile explain "
                 "testing.tables); use beside, declared, files, globals, mocks, preset, skips, tables")


def test_a_profile_writing_the_table_of_testing_is_refused_with_its_hint(tmp_path):
    path = profile_in(tmp_path, OLD_TABLE_PROFILE)
    checked = CliRunner().invoke(app, ["profile", "check", str(path)])
    assert checked.exit_code == 1
    assert f"    {path}: {RETIRED_TABLE}" in checked.output.splitlines()


FUNCTIONS_PROFILE = PRESET_PROFILE.replace("testing: pytest\n", 'testing:\n  files: ["test_*.py"]\n  functions: "test_*"\n')


def test_a_profile_writing_the_functions_of_testing_is_refused_with_its_hint(tmp_path):
    path = profile_in(tmp_path, FUNCTIONS_PROFILE)
    checked = CliRunner().invoke(app, ["profile", "check", str(path)])
    assert checked.exit_code == 1
    assert (f"    {path}: testing: unknown key 'functions': moved in 0.3.0: write declared: [{{function: \"<pattern>\"}}]; "
            "use beside, declared, files, globals, mocks, preset, skips, tables") in checked.output.splitlines()


def test_beside_that_is_no_bool_is_refused_naming_the_file(tmp_path):
    path = profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: pytest, beside: sometimes}"))
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: testing.beside: must be true or false: whether every test of a part sits beside the code it tests",)


def test_a_part_naming_a_tier_with_a_folder_is_refused_under_beside_naming_the_file(tmp_path):
    text = (PROFILE.replace("testing: pytest", "testing: {preset: pytest, beside: true}")
            .replace("    tests: unit\n  cli:", "    tests: guard\n  cli:")
            .replace("tiers:\n  unit: {}\n", "tiers:\n  unit: {}\n  guard: {folder: architecture}\n"))
    path = profile_in(tmp_path, text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: tiers.guard: parts.core says tests: guard, and guard keeps its tests in tests/architecture: under "
        "testing.beside a part's tests sit beside its code; give the part a tier with no folder",)


def test_beside_true_loads_with_the_preset_s_framework(tmp_path):
    path = profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: {preset: pytest, beside: true}"))
    loaded = load_architecture(path)
    assert loaded.framework.beside is True
    assert loaded.framework.files == load_architecture(profile_in(tmp_path, PROFILE)).framework.files
