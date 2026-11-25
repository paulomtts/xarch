"""The words a check of a profile's own is written with that no bundled profile uses, through the real app: `profile
check` holds a check written with each to its examples, and `check` finds with it what it is written to find in a
project, however far what it follows goes."""
import json

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()


def project(tmp_path, checks: dict, files: dict[str, str]) -> None:
    profile = {"name": "mine", "parts": {"store/": {"role": "saves documents"}, "ui/": {"role": "shows them"}},
               "checks": checks}
    (tmp_path / "mine.yaml").write_text(yaml.safe_dump(profile, sort_keys=False))
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "mine.yaml"\n')
    for path, text in files.items():
        (tmp_path / "app" / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "app" / path).write_text(text)


def found(tmp_path, checks: dict, files: dict[str, str]) -> list[tuple[str, int, str]]:
    """What the checks find in the files, once profile check has held every check to its examples."""
    project(tmp_path, checks, files)
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 0, checked.output
    document = json.loads(runner.invoke(app, ["check", "--format", "json"]).output)
    return [(v["file"], v["line"], v["message"]) for v in document["violations"] if v["rule"] in checks]


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


SCREENS = "class Reactive: ...\nclass Screen(Reactive): ...\n"
PAGES = "from app.ui.screens import Screen as Base\n\nclass HomePage(Base): ...\nclass AboutPage: ...\n"
NEVER_REACTIVE = {
    "read": "class", "in": {"part": "ui"}, "keep": [{"named": "*Page"}, {"extends": "Reactive"}], "may_not": "exist",
    "message": "{name} in {file} derives from Reactive at line {line}", "fix": "build {name} from plain parts",
    "examples": {"flagged": {"ui/screens.py": SCREENS, "ui/pages.py": PAGES},
                 "clean": {"ui/screens.py": SCREENS, "ui/pages.py": "class HomePage: ...\n"}}}


def test_extends_follows_the_bases_of_a_class_however_far_through_the_classes_the_app_defines(tmp_path):
    """HomePage derives from Screen through an import that renames it, and Screen from Reactive in its own file."""
    assert found(tmp_path, {"pages-never-reactive": NEVER_REACTIVE},
                 {"ui/screens.py": SCREENS, "ui/pages.py": PAGES}) == [
        ("app/ui/pages.py", 3, "HomePage in app/ui/pages.py derives from Reactive at line 3")]


PORT = "from typing import Protocol\n\nclass StorePort(Protocol): ...\n"
FAKES_EXTEND_PORTS = {
    "read": "class", "in": {"part": "store"}, "keep": [{"named": "Fake*"}], "may_not": "exist",
    "except": [{"extends": "*Port"}], "message": "{name} stands in for no port at line {line}",
    "fix": "derive {name} from the port it stands in for",
    "examples": {"flagged": {"store/fakes.py": "class FakeStore: ...\n"},
                 "clean": {"store/port.py": PORT,
                           "store/fakes.py": "from app.store.port import StorePort\n\nclass FakeStore(StorePort): ...\n"}}}


def test_extends_excuses_a_class_one_of_whose_bases_matches_the_pattern(tmp_path):
    files = {"store/port.py": PORT,
             "store/fakes.py": "from app.store.port import StorePort\n\nclass FakeStore(StorePort): ...\n"
                               "class FakeCache: ...\nclass FakeDeep(FakeStore): ...\n"}
    assert found(tmp_path, {"fakes-extend-ports": FAKES_EXTEND_PORTS}, files) == [
        ("app/store/fakes.py", 4, "FakeCache stands in for no port at line 4")]


def test_extends_is_refused_on_a_kind_that_carries_no_bases(tmp_path):
    project(tmp_path, {"x": {**FAKES_EXTEND_PORTS, "read": "function"}}, {})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 1
    assert ("checks.x.except: extends does not apply to function: it reads bases, which it does not carry; it applies "
            "to class") in checked.output
