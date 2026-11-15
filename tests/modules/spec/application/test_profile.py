"""Use case: choose the profile, from --profile, then [tool.xarch] profile, then nothing: no profile is assumed."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.architecture import ArchitectureService
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import ProfileRefused, ProfileSelected, SelectProfile
from xarch.modules.spec.domain.errors import UnreadableSettings
from xarch.modules.spec.domain.values import Configured
from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.settings import FakeSettings

APP = Path("/src/app")
PYPROJECT = Path("/src/pyproject.toml")
LAYERED = {"xarch": 1, "name": "layered", "layout": {"src": {"singular": "module", "each": {"api": {}}}},
           "parts": {"api": {"path": "src/*/api", "role": "handlers"}}, "rules": {"api": ["api@own"]}}


def controller(configured: Configured | None = None, error: Exception | None = None, tests: Path | None = None,
               files: dict | None = None, settings: FakeSettings | None = None) -> SpecController:
    architectures = ArchitectureService(FakeArchitectureFiles({"cli": LAYERED, "web": LAYERED}, files))
    return SpecController(SkeletonService(settings or FakeSettings(configured, error, tests), architectures),
                          architectures)


FILE = "/src/layered.yaml"


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(), SelectProfile(APP, None),
                 ProfileRefused("no profile: pass --profile, or set `profile` under [tool.xarch] in pyproject.toml; "
                                "the profiles found are cli, web"),
                 id="with nothing configured no profile is chosen and the known ones are listed"),
    pytest.param(dict(configured=Configured("web", PYPROJECT)), SelectProfile(APP, None), ProfileSelected("web"),
                 id="the configured profile is used"),
    pytest.param(dict(configured=Configured("web", PYPROJECT)), SelectProfile(APP, "cli"), ProfileSelected("cli"),
                 id="an override wins over the configured profile"),
    pytest.param(dict(), SelectProfile(APP, "mobile"),
                 ProfileRefused("unknown profile 'mobile': use one of cli, web"),
                 id="an unknown override is refused"),
    pytest.param(dict(configured=Configured("mobile", PYPROJECT)), SelectProfile(APP, None),
                 ProfileRefused(f"unknown profile 'mobile' in {PYPROJECT}: use one of cli, web"),
                 id="an unknown configured profile is refused naming where it came from"),
    pytest.param(dict(error=UnreadableSettings(PYPROJECT, "Expected '=' (at line 1, column 5)")),
                 SelectProfile(APP, None),
                 ProfileRefused(f"cannot read {PYPROJECT}: Expected '=' (at line 1, column 5)"),
                 id="unreadable settings are refused"),
    pytest.param(dict(files={FILE: LAYERED}), SelectProfile(APP, FILE), ProfileSelected(FILE),
                 id="an override may be a path to an architecture file"),
    pytest.param(dict(configured=Configured("arch/layered.yaml", PYPROJECT), files={"/src/arch/layered.yaml": LAYERED}),
                 SelectProfile(APP, None), ProfileSelected("/src/arch/layered.yaml"),
                 id="a configured path is relative to the pyproject holding it"),
    pytest.param(dict(files={FILE: LAYERED | {"rules": {"api": ["api@mine", "nowhere"]}}}), SelectProfile(APP, FILE),
                 ProfileRefused(
                     f"{FILE}: rules.api: 'api@mine' has an unknown scope '@mine': use @own (the importer's own "
                     f"`each` folder) or @any (any `each` folder)\n{FILE}: rules.api: 'nowhere' names no part "
                     "'nowhere'"),
                 id="an invalid architecture file is refused with every problem"),
    pytest.param(dict(), SelectProfile(APP, "/src/none.yaml"),
                 ProfileRefused("/src/none.yaml: cannot read the file: no such file"),
                 id="a missing architecture file is refused with the reason it cannot be read"),
])
def test_profile(given, when, then):
    assert controller(**given).select(when) == then


def select(settings: FakeSettings, override: str | None = None):
    return controller(settings=settings).select(SelectProfile(APP, override))


def test_the_settings_are_looked_up_for_the_app_folder():
    settings = FakeSettings()
    select(settings)
    assert settings.asked == [APP]


def test_the_tests_root_is_the_override_else_the_configured_one_else_none():
    configured = Configured("cli", PYPROJECT)
    assert controller(configured).select(SelectProfile(APP, None)).tests is None
    assert controller(configured, tests=Path("/src/checks")).select(SelectProfile(APP, None)).tests == Path("/src/checks")
    assert controller(configured, tests=Path("/src/checks")).select(SelectProfile(APP, None, Path("t"))).tests == Path("t")
