"""Tests for choosing a profile: --profile, then [tool.xarch] profile, then the default."""
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
    return SpecController(SkeletonService(settings), build_architectures()).select(SelectProfile(APP, override))


def test_with_nothing_configured_the_profile_is_cli():
    assert select(FakeSettings()) == ProfileSelected("cli")


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
