"""The version `xarch --version` prints is the one pyproject.toml gives: the installed package is this source's."""
import tomllib
from importlib import metadata
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def test_the_installed_version_is_the_one_pyproject_gives():
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    assert metadata.version("xarch") == project["version"]
