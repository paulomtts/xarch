"""Where the wired check keeps what its reader read: the folder XARCH_CACHE_DIR names, none when it is empty, else
xarch/ in the user's cache folder; a check with the cache finds what one without it finds."""
from pathlib import Path

import pytest

from tests.bootstrap.project import APP, write
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import AppChecked, CheckApp


def checked(tmp_path: Path, environment: dict[str, str]) -> AppChecked:
    found = build_controllers(environment).rules.check_app(CheckApp(tmp_path / "app", "web", tmp_path))
    assert isinstance(found, AppChecked), found
    return found


def kept(folder: Path) -> list[str]:
    return sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []


@pytest.mark.parametrize("environment, folder", [
    pytest.param({"XARCH_CACHE_DIR": "{tmp}/chosen", "HOME": "{tmp}/home"}, "chosen", id="the folder named"),
    pytest.param({"XDG_CACHE_HOME": "{tmp}/xdg", "HOME": "{tmp}/home"}, "xdg/xarch", id="the user's cache folder"),
    pytest.param({"XDG_CACHE_HOME": "relative", "HOME": "{tmp}/home"}, "home/.cache/xarch",
                 id="the home's, when the cache folder named is not given in full"),
    pytest.param({"HOME": "{tmp}/home"}, "home/.cache/xarch", id="the home's, when no cache folder is named"),
])
def test_the_reader_keeps_what_it_read_in_the_folder_the_environment_says(tmp_path, environment, folder):
    write(tmp_path / "app", APP)
    environment = {name: value.format(tmp=tmp_path) for name, value in environment.items()}
    assert checked(tmp_path, environment) == checked(tmp_path, {"XARCH_CACHE_DIR": ""})
    assert kept(tmp_path / folder) != []


@pytest.mark.parametrize("environment", [
    pytest.param({"XARCH_CACHE_DIR": "", "HOME": "{tmp}/home"}, id="the folder named empty"),
    pytest.param({}, id="no home"),
])
def test_the_reader_keeps_nothing_when_the_environment_says_no_folder(tmp_path, environment):
    write(tmp_path / "app", APP)
    checked(tmp_path, {name: value.format(tmp=tmp_path) for name, value in environment.items()})
    assert kept(tmp_path / "home") == []
