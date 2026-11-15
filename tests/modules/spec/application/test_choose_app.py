"""Use case: choose the app folder to work on, from --app, then [tool.xarch] app in the project around the working
folder, then app/."""
from pathlib import Path

import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.settings import FakeSettings
from tests.modules.spec.application.helpers import controller
from xarch.modules.spec.contract import AppChosen, ChooseApp, ProfileRefused
from xarch.modules.spec.domain.errors import UnreadableSettings

PYPROJECT = Path("/src/pyproject.toml")


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(app=Path("/src/shop")), ChooseApp(Path("/src"), Path("given")), AppChosen(Path("given")),
                 id="the app folder given wins over the one configured"),
    pytest.param(dict(app=Path("/src/shop")), ChooseApp(Path("/src")), AppChosen(Path("/src/shop")),
                 id="the app folder configured for the project is used"),
    pytest.param(dict(), ChooseApp(Path("/src")), AppChosen(Path("app")), id="with none configured it is app/"),
    pytest.param(dict(app=Path("/src/shop"), from_folder=Path("/src")), ChooseApp(Path("/elsewhere")),
                 AppChosen(Path("app")), id="an app folder configured for another project is not this one's"),
    pytest.param(dict(error=UnreadableSettings(PYPROJECT, "bad")), ChooseApp(Path("/src")),
                 ProfileRefused(f"cannot read {PYPROJECT}: bad"), id="unreadable settings are refused with why"),
])
def test_choose_app(given, when, then):
    assert controller(FakeArchitectureFiles({}), FakeSettings(**given)).choose_app(when) == then
