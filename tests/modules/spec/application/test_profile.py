"""Use case: choose the profile, from --profile, then [tool.xarch] profile, then nothing: no profile is assumed.

Scenario: the configured profile is used
  Given a pyproject naming web    When the profile is chosen   Then the Result is ProfileSelected
Scenario: an unknown override is refused
  Given --profile mobile          When the profile is chosen   Then the Result is ProfileRefused
"""
from pathlib import Path

from xarch.bootstrap.wiring import build_architectures
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import ProfileRefused, ProfileSelected, SelectProfile
from xarch.modules.spec.domain.errors import UnreadableSettings
from xarch.modules.spec.domain.values import Configured
from tests.fakes.settings import FakeSettings

APP = Path("/src/app")
PYPROJECT = Path("/src/pyproject.toml")


def select(settings: FakeSettings, override: str | None = None):
    return SpecController(SkeletonService(settings, build_architectures()), build_architectures()).select(SelectProfile(APP, override))


def test_with_nothing_configured_no_profile_is_chosen_and_the_known_ones_are_listed():
    assert select(FakeSettings()) == ProfileRefused(
        "no profile: pass --profile, or set `profile` under [tool.xarch] in pyproject.toml; "
        "the profiles found are cli, web")


def test_the_configured_profile_is_used():
    assert select(FakeSettings(Configured("web", PYPROJECT))) == ProfileSelected("web")


def test_the_settings_are_looked_up_for_the_app_folder():
    settings = FakeSettings()
    select(settings)
    assert settings.asked == [APP]


def test_an_override_wins_over_the_configured_profile():
    assert select(FakeSettings(Configured("web", PYPROJECT)), "cli") == ProfileSelected("cli")


def test_an_unknown_override_is_refused():
    assert select(FakeSettings(), "mobile") == ProfileRefused("unknown profile 'mobile': use one of cli, web")


def test_an_unknown_configured_profile_is_refused_naming_where_it_came_from():
    assert select(FakeSettings(Configured("mobile", PYPROJECT))) == ProfileRefused(
        f"unknown profile 'mobile' in {PYPROJECT}: use one of cli, web")


def test_unreadable_settings_are_refused():
    error = UnreadableSettings(PYPROJECT, "Expected '=' (at line 1, column 5)")
    assert select(FakeSettings(error=error)) == ProfileRefused(
        f"cannot read {PYPROJECT}: Expected '=' (at line 1, column 5)")


LAYERED = """\
xarch: 1
name: layered
layout: {src: {singular: module, each: {api: {}}}}
parts: {api: {path: "src/*/api", role: handlers}}
rules: {api: [api@own]}
"""


def real_select(tmp_path: Path, settings: FakeSettings, override: str | None = None):
    app = tmp_path / "app"
    return SpecController(SkeletonService(settings, build_architectures()), build_architectures()).select(
        SelectProfile(app, override))


def test_an_override_may_be_a_path_to_an_architecture_file(tmp_path):
    (tmp_path / "layered.yaml").write_text(LAYERED)
    assert real_select(tmp_path, FakeSettings(), str(tmp_path / "layered.yaml")) == ProfileSelected(
        str(tmp_path / "layered.yaml"))


def test_a_configured_path_is_relative_to_the_pyproject_holding_it(tmp_path):
    (tmp_path / "arch").mkdir()
    (tmp_path / "arch" / "layered.yaml").write_text(LAYERED)
    configured = Configured("arch/layered.yaml", tmp_path / "pyproject.toml")
    assert real_select(tmp_path, FakeSettings(configured)) == ProfileSelected(str(tmp_path / "arch" / "layered.yaml"))


def test_an_invalid_architecture_file_is_refused_with_every_problem(tmp_path):
    (tmp_path / "layered.yaml").write_text(LAYERED.replace("[api@own]", "[api@mine, nowhere]"))
    file = tmp_path / "layered.yaml"
    result = real_select(tmp_path, FakeSettings(), str(file))
    assert result == ProfileRefused(
        f"{file}: rules.api: 'api@mine' has an unknown scope '@mine': use @own (the importer's own `each` folder) "
        f"or @any (any `each` folder)\n{file}: rules.api: 'nowhere' names no part 'nowhere'")


def test_a_missing_architecture_file_is_refused(tmp_path):
    result = real_select(tmp_path, FakeSettings(), str(tmp_path / "none.yaml"))
    assert isinstance(result, ProfileRefused) and "none.yaml: cannot read the file" in result.reason


def test_the_tests_root_is_the_override_else_the_configured_one_else_none():
    configured = FakeSettings(Configured("cli", PYPROJECT), tests=Path("/src/checks"))
    assert select(FakeSettings(Configured("cli", PYPROJECT))).tests is None
    assert select(configured).tests == Path("/src/checks")
    controller = SpecController(SkeletonService(configured, build_architectures()), build_architectures())
    assert controller.select(SelectProfile(APP, None, Path("t"))).tests == Path("t")
