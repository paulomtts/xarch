"""Recording the profile and the app folder in a pyproject.toml's [tool.xarch] table, as text, never rewriting a value."""
from pathlib import Path

import pytest

from xarch.modules.scaffold.application.logic.pyproject_record import (
    recorded_app,
    recorded_location,
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
