"""Tests for reading [tool.xarch] from pyproject.toml on a real filesystem."""
from pathlib import Path

import pytest

from xarch.modules.spec.adapters.pyproject_settings import PyprojectSettings
from xarch.modules.spec.domain.errors import UnreadableSettings
from xarch.modules.spec.domain.values import Configured
from xarch.platform.filesystem import FileSystem
from xarch.platform.toml import TomlReader


def settings() -> PyprojectSettings:
    return PyprojectSettings(FileSystem(), TomlReader())


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_the_profile_is_read_from_the_pyproject_next_to_the_app(tmp_path):
    pyproject = write(tmp_path / "pyproject.toml", '[tool.xarch]\nprofile = "web"\n')
    assert settings().configured_profile(tmp_path / "app") == Configured("web", pyproject)


def test_the_pyproject_is_looked_up_upward(tmp_path):
    pyproject = write(tmp_path / "pyproject.toml", '[tool.xarch]\nprofile = "web"\n')
    assert settings().configured_profile(tmp_path / "src" / "deep" / "app") == Configured("web", pyproject)


def test_the_nearest_pyproject_decides_even_without_the_key(tmp_path):
    write(tmp_path / "pyproject.toml", '[tool.xarch]\nprofile = "web"\n')
    write(tmp_path / "inner" / "pyproject.toml", '[project]\nname = "inner"\n')
    assert settings().configured_profile(tmp_path / "inner" / "app") is None


def test_a_relative_app_path_is_looked_up_from_the_working_directory(tmp_path, monkeypatch):
    pyproject = write(tmp_path / "pyproject.toml", '[tool.xarch]\nprofile = "web"\n')
    monkeypatch.chdir(tmp_path)
    assert settings().configured_profile(Path("app")) == Configured("web", pyproject)


def test_no_pyproject_means_nothing_configured(tmp_path):
    assert not any((p / "pyproject.toml").exists() for p in [tmp_path, *tmp_path.parents])
    assert settings().configured_profile(tmp_path / "app") is None


@pytest.mark.parametrize("text", ["[tool.xarch\n", '[tool.xarch]\nprofile = 3\n'])
def test_broken_settings_are_unreadable(tmp_path, text):
    write(tmp_path / "pyproject.toml", text)
    with pytest.raises(UnreadableSettings):
        settings().configured_profile(tmp_path / "app")


def test_the_tests_root_is_read_relative_to_the_pyproject(tmp_path):
    write(tmp_path / "pyproject.toml", '[tool.xarch]\ntests = "checks/unit"\n')
    assert settings().configured_tests(tmp_path / "app") == tmp_path / "checks" / "unit"


def test_without_a_tests_setting_none_is_configured(tmp_path):
    write(tmp_path / "pyproject.toml", '[tool.xarch]\nprofile = "web"\n')
    assert settings().configured_tests(tmp_path / "app") is None


def test_a_tests_setting_that_is_not_a_string_is_unreadable(tmp_path):
    pyproject = write(tmp_path / "pyproject.toml", "[tool.xarch]\ntests = 1\n")
    with pytest.raises(UnreadableSettings) as caught:
        settings().configured_tests(tmp_path / "app")
    assert caught.value.reason == f"cannot read {pyproject}: [tool.xarch] tests must be a string"
