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


PORTS = ("from typing import Protocol\n\nclass StorePort(Protocol): ...\nclass CachePort(Protocol): ...\n"
         "class LockPort(Protocol): ...\n")
ONE_PORT = {
    "read": "class", "in": {"part": "store"}, "keep": [{"named": "*Port"}], "at_most": 1,
    "message": "{file} declares {count} interfaces, and {name} at line {line} is one too many",
    "fix": "move {name} to a file of its own",
    "examples": {"flagged": {"store/ports.py": PORTS}, "clean": {"store/ports.py": "class Store: ...\n"}}}


def test_at_most_finds_each_kept_fact_of_a_file_beyond_the_number_at_its_own_line(tmp_path):
    files = {"store/ports.py": PORTS, "store/one.py": "from typing import Protocol\n\nclass OnePort(Protocol): ...\n"}
    assert found(tmp_path, {"one-port-per-file": ONE_PORT}, files) == [
        ("app/store/ports.py", 4, "app/store/ports.py declares 3 interfaces, and CachePort at line 4 is one too many"),
        ("app/store/ports.py", 5, "app/store/ports.py declares 3 interfaces, and LockPort at line 5 is one too many")]


SOME_PORT = {
    "read": "class", "in": {"part": "store"}, "keep": [{"named": "*Port"}], "at_least": 1,
    "message": "{file} declares {count} interfaces, and needs one", "fix": "declare its port, or move the file",
    "examples": {"flagged": {"store/ports.py": "class Store: ...\n"}, "clean": {"store/ports.py": PORTS}}}


def test_at_least_finds_each_file_of_the_scope_that_keeps_fewer_facts_than_the_number(tmp_path):
    assert found(tmp_path, {"a-port-per-file": SOME_PORT}, {"store/ports.py": PORTS, "store/none.py": "x = 1\n"}) == [
        ("app/store/none.py", None, "app/store/none.py declares 0 interfaces, and needs one")]


LONG = {
    "read": "file", "in": {"part": "store"}, "keep": [{"longer-than": 3}], "may_not": "exist",
    "message": "{file} holds {lines} lines", "fix": "split it",
    "examples": {"flagged": {"store/long.py": "a = 1\nb = 2\nc = 3\nd = 4\n"}, "clean": {"store/short.py": "a = 1\n"}}}


def test_longer_than_holds_of_a_file_of_more_lines_than_the_number(tmp_path):
    files = {"store/long.py": "a = 1\nb = 2\nc = 3\nd = 4\n", "store/three.py": "a = 1\nb = 2\nc = 3\n"}
    assert found(tmp_path, {"short-files": LONG}, files) == [("app/store/long.py", None, "app/store/long.py holds 4 lines")]


@pytest.mark.parametrize("changes, said", [
    pytest.param({"at_most": -1}, "checks.x.at_most: must be a whole number, 0 or more", id="a negative number"),
    pytest.param({"at_most": "one"}, "checks.x.at_most: must be a whole number, 0 or more", id="a word"),
    pytest.param({"keep": [{"longer-than": "many"}]},
                 "checks.x.keep: longer-than 'many': write a whole number, such as 700", id="a length that is no number"),
])
def test_a_count_or_a_length_that_is_no_whole_number_is_refused(tmp_path, changes, said):
    body = {**ONE_PORT, **changes} if "at_most" in changes else {**LONG, **changes}
    project(tmp_path, {"x": body}, {})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 1 and said in checked.output, checked.output


def test_count_is_said_only_by_a_check_that_counts(tmp_path):
    project(tmp_path, {"x": {**LONG, "message": "{file} holds {count}"}}, {})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 1
    assert ("checks.x.message: {count} is how many facts a file keeps, which only a check under at_most or at_least "
            "counts") in checked.output
