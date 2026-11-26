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


ACTOR = {
    "read": "function", "in": {"part": "store"}, "keep": [{"parameter-has-default": "actor"}], "may_not": "exist",
    "message": "{name} gives actor a default at line {line}, of {parameters}", "fix": "make every caller pass actor",
    "examples": {"flagged": {"store/x.py": "def load(actor=None): ...\n"},
                 "clean": {"store/x.py": "def load(actor): ...\n"}}}
NO_ROWS = {
    "read": "function", "in": {"part": "store"}, "keep": ["public", {"returns-annotated": "*Row*"}],
    "may_not": "exist", "message": "{name} returns {returns} at line {line}", "fix": "return a value of the domain",
    "examples": {"flagged": {"store/x.py": "def load() -> UserRow: ...\n"},
                 "clean": {"store/x.py": "def load() -> User: ...\n"}}}
NO_RUNTIME = {
    "read": "function", "in": {"part": "store"}, "keep": [{"has-parameter": "runtime"}, {"named": "__init__"}],
    "except": [{"not parameter-annotated": "*RuntimePort"}], "may_not": "exist",
    "message": "{name} takes the runtime at line {line}", "fix": "take a narrower port",
    "examples": {"flagged": {"store/x.py": "class A:\n    def __init__(self, runtime: RuntimePort): ...\n"},
                 "clean": {"store/x.py": "class A:\n    def __init__(self, runtime: Clock): ...\n"}}}


def test_signature_filters_read_a_function_s_parameters_defaults_annotations_and_return_annotation(tmp_path):
    files = {"store/x.py": ("def load(title: str, actor: 'Actor | None' = None): ...\n"
                            "def save(actor, *, row=1) -> list[UserRow]: ...\n"
                            "def _raw() -> UserRow: ...\n"
                            "class A:\n    def __init__(self, runtime: 'FlowRuntimePort'): ...\n"
                            "class B:\n    def __init__(self, runtime): ...\n")}
    assert found(tmp_path, {"actor-has-no-default": ACTOR, "no-rows": NO_ROWS, "no-runtime": NO_RUNTIME}, files) == [
        ("app/store/x.py", 1, "load gives actor a default at line 1, of title, actor"),
        ("app/store/x.py", 2, "save returns list[UserRow] at line 2"),
        ("app/store/x.py", 5, "__init__ takes the runtime at line 5")]


SKIP_LOCKED = {
    "read": ["method-call"], "in": {"part": "store"}, "keep": [{"passes-literal": "skip_locked=True"}],
    "may_not": "exist", "message": "{file} claims rows at line {line}", "fix": "claim them through the shared claim",
    "examples": {"flagged": {"store/x.py": "q.with_for_update(skip_locked=True)\n"},
                 "clean": {"store/x.py": "q.with_for_update()\n"}}}
GUARDED = {
    "read": "call", "in": {"part": "ui"}, "may_not": {"path": ["app.ui.drawer.EditDrawer"]},
    "except": [{"passes": "unsaved_guard_form"}], "message": "{path} at line {line} guards no form",
    "fix": "pass unsaved_guard_form",
    "examples": {"flagged": {"ui/x.py": "from app.ui.drawer import EditDrawer\n\nEditDrawer()\n"},
                 "clean": {"ui/x.py": "from app.ui.drawer import EditDrawer\n\nEditDrawer(unsaved_guard_form=f)\n"}}}


def test_call_argument_filters_read_the_keywords_a_call_passes_and_whether_a_value_is_a_literal(tmp_path):
    files = {"store/x.py": "q.with_for_update(skip_locked=True)\nq.with_for_update(skip_locked=flag)\n",
             "ui/x.py": ("from app.ui.drawer import EditDrawer\nfrom app.ui import drawer\n\n"
                         "EditDrawer(unsaved_guard_form=f)\ndrawer.EditDrawer(title='x')\n")}
    assert found(tmp_path, {"one-claim": SKIP_LOCKED, "drawers-guard": GUARDED}, files) == [
        ("app/store/x.py", 1, "app/store/x.py claims rows at line 1"),
        ("app/ui/x.py", 5, "app.ui.drawer.EditDrawer at line 5 guards no form")]


GETTERS = {
    "read": "call", "in": {"part": "ui"}, "keep": [{"named": "get_*"}], "may_only": {"name": ["get_*_controller"]},
    "message": "{path} at line {line} is no controller's getter", "fix": "depend on a controller's getter",
    "examples": {"flagged": {"ui/x.py": "from app.store import get_load\n\nget_load()\n"},
                 "clean": {"ui/x.py": "from app.store import get_doc_controller\n\nget_doc_controller()\n"}}}


def test_a_name_pattern_applies_to_a_call_by_the_last_name_of_its_callee(tmp_path):
    files = {"ui/x.py": "from app import store\nfrom app.store import get_doc_controller\n\n"
                        "get_doc_controller()\nstore.get_registry()\nstore.load()\n"}
    assert found(tmp_path, {"controller-getters": GETTERS}, files) == [
        ("app/ui/x.py", 5, "app.store.get_registry at line 5 is no controller's getter")]


NEVER_SQL = {
    "read": "import", "in": {"part": "ui"}, "must_not_reach": {
        "targets": [{"package": ["sqlalchemy"]}], "through": "import-into-app"},
    "message": "{file} reaches sqlalchemy at line {line}: {chain}", "fix": "take what it needs through a port",
    "examples": {"flagged": {"ui/page.py": "import sqlalchemy\n"}, "clean": {"ui/page.py": "import json\n"}}}


def test_must_not_reach_finds_a_file_that_reaches_a_target_however_far_and_shows_the_chain(tmp_path):
    """The page takes Repo from the store's package file, which only re-exports it from sql.py: the chain goes
    through the package file, and on through every file it imports."""
    files = {"ui/page.py": "import json\nfrom app.store import Repo\n", "ui/plain.py": "import json\n",
             "store/__init__.py": "from app.store.sql import Repo\n",
             "store/sql.py": "import sqlalchemy\n\nclass Repo: ...\n"}
    assert found(tmp_path, {"ui-never-sql": NEVER_SQL}, files) == [
        ("app/ui/page.py", 2, "app/ui/page.py reaches sqlalchemy at line 2: app.store -> app.store.sql -> sqlalchemy")]


def test_must_not_reach_says_a_target_of_the_file_s_own_at_its_line(tmp_path):
    assert found(tmp_path, {"ui-never-sql": NEVER_SQL}, {"ui/page.py": "import json\nimport sqlalchemy\n"}) == [
        ("app/ui/page.py", 2, "app/ui/page.py reaches sqlalchemy at line 2: sqlalchemy")]


def test_chain_is_said_only_by_a_check_under_must_not_reach(tmp_path):
    project(tmp_path, {"x": {**LONG, "message": "{file} reaches {chain}"}}, {})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 1
    assert ("checks.x.message: {chain} is the chain of links a file reaches a target by, which only a check under "
            "must_not_reach follows") in checked.output
