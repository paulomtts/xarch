"""Use case: the profiles a project knows, the one in force and the bundled ones; none configured comes back with the
bundled ones, and one that cannot be chosen or loaded is refused with why."""
from pathlib import Path

import pytest

from tests.fakes.architecture_files import FakeArchitectureFiles
from tests.fakes.settings import FakeSettings
from tests.modules.spec.application.helpers import controller
from xarch.modules.spec.contract import KnownProfiles, NoProfileChosen, ProfileRefused
from xarch.modules.spec.domain.errors import UnreadableSettings
from xarch.modules.spec.domain.values import Configured

APP = Path("/src/app")
PYPROJECT = Path("/src/pyproject.toml")
LAYERED = {"name": "layered", "parts": {"api": {"path": "api", "role": "handlers"}}}
BROKEN = {"name": "broken"}
FILES = FakeArchitectureFiles({"cli": LAYERED, "web": LAYERED}, {"/src/broken.yaml": BROKEN})


@pytest.mark.parametrize("given, when, then", [
    pytest.param(FakeSettings(configured=Configured("web", PYPROJECT)), APP, KnownProfiles("web", ("cli", "web")),
                 id="the profile in force, then the bundled ones"),
    pytest.param(FakeSettings(), APP, NoProfileChosen(("cli", "web")),
                 id="with none configured, the bundled ones come back as no profile chosen"),
    pytest.param(FakeSettings(configured=Configured("mobile", PYPROJECT)), APP,
                 ProfileRefused(f"unknown profile 'mobile' in {PYPROJECT}: use one of cli, web"),
                 id="an unknown configured profile is refused with why"),
    pytest.param(FakeSettings(configured=Configured("broken.yaml", PYPROJECT)), APP,
                 ProfileRefused("/src/broken.yaml: missing `parts`"),
                 id="a configured profile that does not load is refused with why"),
    pytest.param(FakeSettings(error=UnreadableSettings(PYPROJECT, "bad")), APP,
                 ProfileRefused(f"cannot read {PYPROJECT}: bad"), id="unreadable settings are refused with why"),
])
def test_known(given, when, then):
    assert controller(FILES, given).known(when) == then
