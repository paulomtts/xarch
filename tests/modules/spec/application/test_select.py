"""Use case: choose the profile, from --profile, then [tool.xarch] profile, then nothing: no profile is assumed."""
from pathlib import Path

import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.folders import FakeFolders
from tests.fakes.settings import FakeSettings
from tests.modules.spec.application.helpers import controller as spec_controller
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import NoProfileChosen, ProfileRefused, ProfileSelected, SelectProfile
from xarch.modules.spec.domain.errors import UnreadableSettings
from xarch.modules.spec.domain.values import Configured

APP = Path("/src/app")
PYPROJECT = Path("/src/pyproject.toml")
LAYERED = {"xarch": 2, "name": "layered", "parts": {"api": {"path": "src/<module>/api", "role": "handlers"}}}


def controller(configured: Configured | None = None, error: Exception | None = None, tests: Path | None = None,
               files: dict | None = None, at: Path | None = None, app: Path | None = None,
               from_folder: Path | None = None) -> SpecController:
    port = FakeArchitectureFiles({"cli": LAYERED, "web": LAYERED}, files)
    settings = FakeSettings(configured, error, tests, at, app, from_folder)
    return spec_controller(port, settings)


FILE = "/src/layered.yaml"
BROKEN = {**LAYERED, "parts": {"api": {**LAYERED["parts"]["api"], "may_import": ["api@mine", "nowhere"]}}}


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(), SelectProfile(APP, None),
                 NoProfileChosen(("cli", "web",)),
                 id="with nothing configured no profile is chosen and the known ones are listed"),
    pytest.param(dict(configured=Configured("web", PYPROJECT)), SelectProfile(APP, None), ProfileSelected("web"),
                 id="the configured profile is used"),
    pytest.param(dict(configured=Configured("web", PYPROJECT), at=APP), SelectProfile(APP, None), ProfileSelected("web"),
                 id="the profile is the one configured for the project holding the app folder"),
    pytest.param(dict(configured=Configured("web", PYPROJECT), at=Path("/elsewhere/app")), SelectProfile(APP, None),
                 NoProfileChosen(("cli", "web",)),
                 id="a profile configured for another folder is not the app folder's"),
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
    pytest.param(dict(files={FILE: BROKEN}), SelectProfile(APP, FILE),
                 ProfileRefused(
                     f"{FILE}: parts.api.may_import: 'api@mine' has an unknown scope '@mine': the only scope is "
                     f"@any, any instance of the repeating folder\n{FILE}: parts.api.may_import: 'nowhere' names "
                     "no part 'nowhere'"),
                 id="an invalid architecture file is refused with every problem"),
    pytest.param(dict(), SelectProfile(APP, "/src/none.yaml"),
                 ProfileRefused("/src/none.yaml: cannot read the file: no such file"),
                 id="a missing architecture file is refused with the reason it cannot be read"),
])
def test_profile(given, when, then):
    assert controller(**given).select(when) == then


@pytest.mark.parametrize("configured_tests, override, tests", [
    pytest.param(None, None, None, id="with neither the tests root is none"),
    pytest.param(Path("/src/checks"), None, Path("/src/checks"), id="the configured tests root is used"),
    pytest.param(Path("/src/checks"), Path("t"), Path("t"), id="an override wins over the configured tests root"),
])
def test_the_tests_root(configured_tests, override, tests):
    result = controller(Configured("cli", PYPROJECT), tests=configured_tests).select(SelectProfile(APP, None, override))
    assert isinstance(result, ProfileSelected) and result.tests == tests


@pytest.mark.parametrize("folders, tests", [
    pytest.param({Path("/src/tests")}, Path("/src/tests"), id="tests/ beside the app folder is the default tests root"),
    pytest.param(set(), None, id="with no tests/ beside the app folder there is no tests root"),
])
def test_the_tests_root_by_default(folders, tests):
    port = FakeArchitectureFiles({"cli": LAYERED, "web": LAYERED})
    spec = spec_controller(port, FakeSettings(Configured("cli", PYPROJECT)), folders=FakeFolders(folders))
    result = spec.select(SelectProfile(APP, None))
    assert isinstance(result, ProfileSelected) and result.tests == tests
