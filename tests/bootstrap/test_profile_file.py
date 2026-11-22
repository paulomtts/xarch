"""A profile file through the real app: read from a file, its test framework taken from the preset shipped as
data, and its rules, outside packages and names enforced by the wired check; and the preset itself, which holds what
the bundled profiles spell out."""
from pathlib import Path

import pytest

from tests.bootstrap.project import app_check, bundled_profiles
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.profile_values.testing import ScenarioCoverage, StandIns

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
    may_import: [core]
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
  scenario-coverage: {results: results, tier: unit, suffix: Result, columns: [given, when, then], file: "test_{name}.py"}
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
        "app/cli/app.py:1: cli/ may not import the outside package yaml (parts.cli.libraries)",
        "app/core/rules.py:1: core/ may not import the outside package typer (parts.core.libraries)"]


def test_the_names_a_part_forbids_are_enforced(tmp_path):
    assert check(tmp_path, {"core/rules.py": "print(1)\n"}) == [
        "app/core/rules.py:1: core/ may not use builtins.print (parts.core.forbidden)"]


def test_the_preset_is_read_from_the_data_file_beside_the_bundled_profiles(tmp_path):
    architecture = load_architecture(profile_in(tmp_path))
    assert architecture.framework is not None
    assert architecture.framework.files == ("test_*.py", "*_test.py")
    assert architecture.framework.functions == "test_*"


def test_a_preset_that_does_not_exist_is_refused_listing_the_ones_that_do(tmp_path):
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(profile_in(tmp_path, PROFILE.replace("testing: pytest", "testing: rspec")))
    assert caught.value.problems == (
        f"{tmp_path / 'small.yaml'}: testing: no preset 'rspec': use pytest, or write the map {{files, functions}}",)


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
    """tests, and the table and the mocks of the guards scenario-coverage and stand-ins."""
    spelled = load_architecture(name)
    preset = load_architecture(profile_in(tmp_path, PRESET_PROFILE))
    assert preset.framework == spelled.framework
    assert [g for g in preset.guards if isinstance(g, StandIns)] == [g for g in spelled.guards if isinstance(g, StandIns)]
    assert [g.table for g in preset.guards if isinstance(g, ScenarioCoverage)] == [
        g.table for g in spelled.guards if isinstance(g, ScenarioCoverage)]


def test_xarch_s_own_profile_spells_out_the_same_as_the_preset(tmp_path):
    spelled = load_architecture(Path(__file__).parent.parent.parent / "architecture.yaml")
    preset = load_architecture(profile_in(tmp_path, PRESET_PROFILE))
    assert preset.framework == spelled.framework
    assert [g for g in preset.guards if isinstance(g, StandIns)] == [g for g in spelled.guards if isinstance(g, StandIns)]
    assert [g.table for g in preset.guards if isinstance(g, ScenarioCoverage)] == [
        g.table for g in spelled.guards if isinstance(g, ScenarioCoverage)]
