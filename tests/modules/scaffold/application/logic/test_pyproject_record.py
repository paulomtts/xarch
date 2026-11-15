"""Recording the profile and the app folder in a pyproject.toml's [tool.xarch] table, as text, never rewriting a value."""
from pathlib import Path

import pytest

from xarch.modules.scaffold.application.logic.pyproject_record import (
    pyproject_target,
    recorded_app,
    recorded_location,
    recorded_text,
    with_profile,
    with_setting,
)

CWD = Path("/work")


@pytest.mark.parametrize("location, folder, recorded", [
    pytest.param("web", Path("/src"), "web", id="a bundled name is recorded as it is"),
    pytest.param("/src/profiles/arch.yaml", Path("/src"), "profiles/arch.yaml",
                 id="a path is recorded relative to the folder holding the pyproject"),
    pytest.param("arch.yaml", Path("/work/sub"), "../arch.yaml", id="a relative path is read from the current folder"),
])
def test_recorded_location(location, folder, recorded):
    assert recorded_location(location, folder, CWD) == recorded


@pytest.mark.parametrize("app, folder, recorded", [
    pytest.param(Path("/src/app"), Path("/src"), None, id="the default app folder needs no record"),
    pytest.param(Path("/src/services/shop"), Path("/src"), "services/shop", id="another folder is recorded as posix"),
    pytest.param(Path("shop"), Path("/work"), "shop", id="a relative app folder is read from the current folder"),
])
def test_recorded_app(app, folder, recorded):
    assert recorded_app(app, folder, CWD) == recorded


@pytest.mark.parametrize("text, written", [
    pytest.param(None, '[tool.xarch]\nprofile = "web"\n', id="no file gets the table"),
    pytest.param('[project]\nname = "x"\n', '[project]\nname = "x"\n\n[tool.xarch]\nprofile = "web"\n',
                 id="a file with no table gets it at the end"),
    pytest.param('[tool.xarch]\ntests = "t"\n\n[tool.other]\n', '[tool.xarch]\nprofile = "web"\ntests = "t"\n\n'
                 '[tool.other]\n', id="an existing table gets the key at its top"),
    pytest.param('[tool.xarch]\nprofile = "cli"\n', None, id="a recorded profile is never rewritten"),
    pytest.param('tool.xarch.profile = "cli"\n', None, id="a table written another way is not extended"),
])
def test_with_profile(text, written):
    assert with_profile(text, "web") == written


def test_with_setting_writes_the_key_after_the_one_it_follows_and_quotes_the_value():
    text = '[tool.xarch]\nprofile = "web"\ntests = "t"\n'
    assert with_setting(text, "app", 'a"b', after="profile") == '[tool.xarch]\nprofile = "web"\napp = "a\\"b"\ntests = "t"\n'


@pytest.mark.parametrize("text, app, written", [
    pytest.param(None, "shop", '[tool.xarch]\nprofile = "web"\napp = "shop"\n',
                 id="a new pyproject records an app folder that is not the default, after the profile"),
    pytest.param('[project]\nname = "x"\n', "shop", '[project]\nname = "x"\n\n[tool.xarch]\nprofile = "web"\n'
                 'app = "shop"\n', id="a pyproject with no table gets it with both"),
    pytest.param('[tool.xarch]\ntests = "t"\n\n[tool.other]\n', "shop",
                 '[tool.xarch]\nprofile = "web"\napp = "shop"\ntests = "t"\n\n[tool.other]\n',
                 id="an existing table gets both at its top"),
    pytest.param('[tool.xarch]\nprofile = "web"\n', "shop", '[tool.xarch]\nprofile = "web"\napp = "shop"\n',
                 id="a recorded profile is left, and the app folder is still recorded"),
    pytest.param('[tool.xarch]\napp = "other"\n', "shop", '[tool.xarch]\nprofile = "web"\napp = "other"\n',
                 id="a recorded app folder is left, and the profile is still recorded"),
    pytest.param('[tool.xarch]\nprofile = "cli"\napp = "other"\n', "shop", None,
                 id="a profile and an app folder already recorded are never rewritten"),
    pytest.param(None, None, '[tool.xarch]\nprofile = "web"\n', id="the default app folder is not recorded"),
    pytest.param('[tool.xarch]\nprofile = "web"\n', None, None,
                 id="the default app folder with a recorded profile has nothing to record"),
])
def test_recorded_text(text, app, written):
    assert recorded_text(text, "web", app) == written


@pytest.mark.parametrize("found, target", [
    pytest.param(None, Path("src/pyproject.toml"), id="no pyproject: a new one in the folder holding the app"),
    pytest.param(Path("/work/src/pyproject.toml"), Path("src/pyproject.toml"),
                 id="the one in the folder holding the app is named below it"),
    pytest.param(Path("/work/pyproject.toml"), Path("/work/pyproject.toml"), id="one found above it is used"),
])
def test_pyproject_target(found, target):
    assert pyproject_target(found, Path("src"), Path("/work/src")) == target
