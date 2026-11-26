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


def test_at_most_names_the_fact_after_the_limit_and_an_accepted_entry_names_that_fact(tmp_path):
    """StorePort is within the limit: CachePort, the fact after it, is the finding, and so what an entry names; each
    finding of the file says the same count, how many the file keeps. An entry naming StorePort accepts nothing."""
    accepted = {**ONE_PORT, "accepted": [{"file": "store/ports.py", "name": "CachePort", "why": "a cache beside it"}]}
    assert found(tmp_path, {"one-port-per-file": accepted}, {"store/ports.py": PORTS}) == [
        ("app/store/ports.py", 5, "app/store/ports.py declares 3 interfaces, and LockPort at line 5 is one too many")]
    within = {**ONE_PORT, "accepted": [{"file": "store/ports.py", "name": "StorePort", "why": "the first"}]}
    project(tmp_path, {"one-port-per-file": within}, {"store/ports.py": PORTS})
    document = json.loads(runner.invoke(app, ["check", "--format", "json"]).output)
    assert [(v["line"], v["message"]) for v in document["violations"] if v["rule"] == "one-port-per-file"] == [
        (None, "checks.one-port-per-file.accepted accepts a finding of store/ports.py with name StorePort, and the check "
            "finds none (checks.one-port-per-file.accepted)"),
        (4, "app/store/ports.py declares 3 interfaces, and CachePort at line 4 is one too many"),
        (5, "app/store/ports.py declares 3 interfaces, and LockPort at line 5 is one too many")]


SOME_PORT = {
    "read": "class", "in": {"part": "store"}, "keep": [{"named": "*Port"}], "at_least": 1,
    "message": "{file} declares {count} interfaces, and needs one", "fix": "declare its port, or move the file",
    "examples": {"flagged": {"store/ports.py": "class Store: ...\n"}, "clean": {"store/ports.py": PORTS}}}


def test_at_least_finds_each_file_of_the_scope_that_keeps_fewer_facts_than_the_number(tmp_path):
    assert found(tmp_path, {"a-port-per-file": SOME_PORT}, {"store/ports.py": PORTS, "store/none.py": "x = 1\n"}) == [
        ("app/store/none.py", None, "app/store/none.py declares 0 interfaces, and needs one")]


ONE_PORT_PER_PART = {
    **ONE_PORT, "at_most": {"count": 1, "per": "part"},
    "examples": {"flagged": {"store/a.py": PORT, "store/b.py": PORT.replace("Store", "Cache")},
                 "clean": {"store/a.py": PORT}}}


def test_at_most_per_part_counts_the_files_of_a_part_together_finding_each_fact_after_the_number(tmp_path):
    files = {"store/a.py": PORT, "store/b.py": PORTS, "ui/c.py": PORT}
    assert found(tmp_path, {"one-port-per-part": ONE_PORT_PER_PART}, files) == [
        ("app/store/b.py", 3, "app/store/b.py declares 4 interfaces, and StorePort at line 3 is one too many"),
        ("app/store/b.py", 4, "app/store/b.py declares 4 interfaces, and CachePort at line 4 is one too many"),
        ("app/store/b.py", 5, "app/store/b.py declares 4 interfaces, and LockPort at line 5 is one too many")]


def test_at_least_per_part_finds_a_part_that_keeps_fewer_at_its_first_file(tmp_path):
    some = {**SOME_PORT, "at_least": {"count": 1, "per": "part"}, "in": {}, "message": "{file} and its part keep {count}"}
    some["examples"] = {"flagged": {"store/a.py": "x = 1\n"}, "clean": {"store/a.py": PORT}}
    files = {"store/a.py": PORT, "ui/a.py": "x = 1\n", "ui/b.py": "y = 1\n"}
    assert found(tmp_path, {"a-port-per-part": some}, files) == [("app/ui/a.py", None, "app/ui/a.py and its part keep 0")]


def test_a_count_written_as_a_map_is_written_back_as_one(tmp_path):
    project(tmp_path, {"one-port-per-part": ONE_PORT_PER_PART}, {})
    shown = runner.invoke(app, ["profile", "explain", "checks.one-port-per-part", "--rule"])
    assert "at_most: {count: 1, per: part}" in shown.output, shown.output


UNIQUE_NAMES = {
    "read": "class", "unique": {"field": "name", "per": "all"},
    "message": "{name} at line {line} is declared already, at {first}", "fix": "rename one of the two",
    "examples": {"flagged": {"store/a.py": "class Title: ...\n", "ui/b.py": "class Title: ...\n"},
                 "clean": {"store/a.py": "class Title: ...\n", "ui/b.py": "class Draft: ...\n"}}}


def test_unique_finds_a_class_named_as_one_before_it_naming_where_the_first_is_and_an_entry_accepts_it(tmp_path):
    files = {"store/a.py": "class Title: ...\nclass Draft: ...\n", "ui/b.py": "class Title: ...\n",
             "ui/c.py": "class Draft: ...\n"}
    assert found(tmp_path, {"unique-names": UNIQUE_NAMES}, files) == [
        ("app/ui/b.py", 1, "Title at line 1 is declared already, at app/store/a.py:1"),
        ("app/ui/c.py", 1, "Draft at line 1 is declared already, at app/store/a.py:2")]
    accepted = {**UNIQUE_NAMES, "accepted": [{"file": "ui/c.py", "name": "Draft", "why": "the ui keeps its own draft"}]}
    assert found(tmp_path, {"unique-names": accepted}, files) == [
        ("app/ui/b.py", 1, "Title at line 1 is declared already, at app/store/a.py:1")]


def test_unique_written_as_a_field_alone_compares_every_file_of_the_scope(tmp_path):
    files = {"store/a.py": "class Title: ...\n", "ui/b.py": "class Title: ...\n"}
    assert found(tmp_path, {"unique-names": {**UNIQUE_NAMES, "unique": "name"}}, files) == [
        ("app/ui/b.py", 1, "Title at line 1 is declared already, at app/store/a.py:1")]


@pytest.mark.parametrize("unique, written", [
    pytest.param({"field": "name", "per": "instance"}, "unique: {field: name, per: instance}", id="a map"),
    pytest.param({"field": "name"}, "unique: name", id="every file compared together"),
])
def test_unique_is_written_back_as_it_was_written(tmp_path, unique, written):
    project(tmp_path, {"unique-names": {**UNIQUE_NAMES, "unique": unique}}, {})
    shown = runner.invoke(app, ["profile", "explain", "checks.unique-names", "--rule"])
    assert written in shown.output, shown.output


@pytest.mark.parametrize("unique, said", [
    pytest.param({"field": "colour"}, "checks.x.unique.field: compares no field 'colour': write one of name, path, text",
                 id="an unknown field"),
    pytest.param({"field": "text"}, "checks.x.unique.field: text is not carried by class: read a kind that carries it",
                 id="a field the kind does not carry"),
    pytest.param({"field": "name", "by": "all"}, "checks.x.unique: unknown key `by`: use field, per", id="an unknown key"),
    pytest.param({"per": "all"}, "checks.x.unique: missing `field`", id="no field"),
])
def test_unique_written_wrong_is_refused_at_its_address(tmp_path, unique, said):
    project(tmp_path, {"x": {**UNIQUE_NAMES, "unique": unique}}, {})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 1 and said in checked.output, checked.output


def test_first_is_said_only_by_a_check_under_unique(tmp_path):
    project(tmp_path, {"x": {**LONG, "message": "{file} again, first at {first}"}}, {})
    checked = runner.invoke(app, ["profile", "check"])
    assert checked.exit_code == 1
    assert ("checks.x.message: {first} is where the first fact of the same value is, which only a check under unique "
            "finds") in checked.output


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
    pytest.param({"at_most": {"count": 1, "per": "folder"}},
                 "checks.x.at_most.per: no files are counted per 'folder': write one of file, part, instance, all",
                 id="an unknown per"),
    pytest.param({"at_most": {"count": 1, "by": "part"}}, "checks.x.at_most: unknown key `by`: use count, per",
                 id="an unknown key"),
    pytest.param({"at_most": {"per": "part"}}, "checks.x.at_most: missing `count`", id="no count"),
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


LIMITS = {
    "read": ["call", "method-call"], "keep": [{"passes-positional": "0=50"}], "may_not": "exist",
    "message": "{file} pages by a literal 50 at line {line}", "fix": "take the page size from the settings",
    "examples": {"flagged": {"store/x.py": "q.limit(50)\n"}, "clean": {"store/x.py": "q.limit(size)\n"}}}
ANY_LITERAL = {**LIMITS, "keep": [{"passes-positional": "1"}], "message": "{file} passes a literal second at line {line}",
               "examples": {"flagged": {"store/x.py": "q.limit(size, 2)\n"}, "clean": {"store/x.py": "q.limit(2)\n"}}}


def test_passes_positional_reads_the_literals_a_call_passes_by_their_place_from_0_and_their_text(tmp_path):
    files = {"store/x.py": ("from app.ui.pages import page\n\nq.limit(50)\nq.limit(size)\npage(50)\n"
                            "q.limit(*sizes, 50)\nq.limit(10, 50)\n"),
             "ui/pages.py": "def page(size): ...\n"}
    assert found(tmp_path, {"no-literal-limit": LIMITS, "second-literal": ANY_LITERAL}, files) == [
        ("app/store/x.py", 3, "app/store/x.py pages by a literal 50 at line 3"),
        ("app/store/x.py", 5, "app/store/x.py pages by a literal 50 at line 5"),
        ("app/store/x.py", 7, "app/store/x.py passes a literal second at line 7")]


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


PORT_IN_UI = {
    "read": "class", "in": {"part": "ui"}, "keep": ["interface"], "may_not": "exist",
    "message": "{name} at line {line} is an interface in {where}", "fix": "move {name} to store/",
    "examples": {"flagged": {"ui/ports.py": "from typing import Protocol\n\nclass ScreenPort(Protocol): ...\n"},
                 "clean": {"ui/ports.py": "class ScreenPort: ...\n"}}}
FROZEN_IN_UI = {
    "read": "class", "in": {"part": "ui"}, "keep": ["immutable"], "may_not": "exist",
    "message": "{name} at line {line} is an immutable record in {where}", "fix": "move {name} to store/",
    "examples": {"flagged": {"ui/rows.py": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Row:\n"
                                          "    a: int\n"},
                 "clean": {"ui/rows.py": "from dataclasses import dataclass\n\n@dataclass\nclass Row:\n    a: int\n"}}}


@pytest.mark.parametrize("check, line", [pytest.param(PORT_IN_UI, 3, id="interface"),
                                         pytest.param(FROZEN_IN_UI, 4, id="immutable")])
def test_the_examples_of_a_check_are_read_with_the_language_s_marks_of_an_interface_and_an_immutable_record(
        tmp_path, check, line):
    """profile check reads its flagged example's class as an interface (or a record) as check reads the project's."""
    assert [at for _, at, _ in found(tmp_path, {"x": check}, check["examples"]["flagged"])] == [line]


FOR_THE_CHECKER = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from app.ui.page import Page\n"
WHEN_IT_RUNS = "from app.ui.page import Page\n"
STORE_BLIND = {
    "read": "import-into-app", "in": {"part": "store"}, "keep": ["not type-only"], "may_not": {"part": ["ui"]},
    "message": "{file} imports the ui at line {line} when its code runs", "fix": "import it only for the type checker",
    "examples": {"flagged": {"store/x.py": WHEN_IT_RUNS, "ui/page.py": "class Page: ...\n"},
                 "clean": {"store/x.py": FOR_THE_CHECKER, "ui/page.py": "class Page: ...\n"}}}
STORE_NEVER_SQL = {
    "read": "import", "in": {"part": "store"}, "must_not_reach": {
        "targets": [{"package": ["sqlalchemy"]}], "through": "import-into-app", "through_only": ["not type-only"]},
    "message": "{file} reaches sqlalchemy at line {line}: {chain}", "fix": "take what it needs through a port",
    "examples": {"flagged": {"store/x.py": WHEN_IT_RUNS, "ui/page.py": "import sqlalchemy\n\nclass Page: ...\n"},
                 "clean": {"store/x.py": FOR_THE_CHECKER, "ui/page.py": "import sqlalchemy\n\nclass Page: ...\n"}}}


def test_an_import_into_the_app_carries_whether_it_is_made_only_for_the_type_checker(tmp_path):
    """Kept, and as a link of a closure, an import under TYPE_CHECKING is skipped by `not type-only`."""
    files = {"store/a.py": WHEN_IT_RUNS, "store/b.py": FOR_THE_CHECKER, "ui/page.py": "import sqlalchemy\n\nclass Page: ...\n"}
    assert found(tmp_path, {"store-blind": STORE_BLIND, "store-never-sql": STORE_NEVER_SQL}, files) == [
        ("app/store/a.py", 1, "app/store/a.py imports the ui at line 1 when its code runs"),
        ("app/store/a.py", 1, "app/store/a.py reaches sqlalchemy at line 1: app.ui.page -> sqlalchemy")]


STORE_PACKAGE = ("from app.store.sql import Repo\nfrom .names import Title as Name\nfrom .inner import Deep\n"
                 "Local = 1\n")
NEVER_SQL_BY_DEFINITION = {
    "read": "import", "in": {"part": "ui"}, "must_not_reach": {
        "targets": [{"package": ["sqlalchemy"]}], "through": "import-to-definition"},
    "message": "{file} reaches sqlalchemy at line {line}: {chain}", "fix": "take what it needs through a port",
    "examples": {"flagged": {"ui/page.py": "from app.store import Repo\n", "store/__init__.py": STORE_PACKAGE,
                             "store/sql.py": "import sqlalchemy\n\nclass Repo: ...\n"},
                 "clean": {"ui/page.py": "from app.store import Name\n", "store/__init__.py": STORE_PACKAGE,
                           "store/sql.py": "import sqlalchemy\n\nclass Repo: ...\n",
                           "store/names.py": "class Title: ...\n"}}}


def test_import_to_definition_follows_a_name_a_package_file_passes_on_to_the_file_that_defines_it(tmp_path):
    """Repo is taken from the package, which takes it from sql.py: the chain skips the package. Name is Title, passed
    on under another name from names.py, which reaches no sqlalchemy; Deep is passed on by two package files; Local is
    the package's own, so the package is reached as before, and every file it imports with it."""
    files = {"ui/page.py": "from app.store import Repo\n", "ui/plain.py": "from app.store import Name\n",
             "ui/deep.py": "from app.store import Deep\n", "ui/own.py": "from app.store import Local\n",
             "store/__init__.py": STORE_PACKAGE, "store/sql.py": "import sqlalchemy\n\nclass Repo: ...\n",
             "store/names.py": "class Title: ...\n", "store/inner/__init__.py": "from .deep import Deep\n",
             "store/inner/deep.py": "class Deep: ...\n"}
    assert found(tmp_path, {"ui-never-sql": NEVER_SQL_BY_DEFINITION}, files) == [
        ("app/ui/own.py", 1, "app/ui/own.py reaches sqlalchemy at line 1: app.store -> app.store.sql -> sqlalchemy"),
        ("app/ui/page.py", 1, "app/ui/page.py reaches sqlalchemy at line 1: app.store.sql -> sqlalchemy")]


def test_import_to_definition_stops_where_package_files_pass_a_name_on_to_each_other(tmp_path):
    files = {"ui/page.py": "from app.store import Repo\n", "store/__init__.py": "from app.ui import Repo\n",
             "ui/__init__.py": "from app.store import Repo\nimport sqlalchemy\n"}
    assert [line for _, line, _ in found(tmp_path, {"ui-never-sql": NEVER_SQL_BY_DEFINITION}, files)] == [2, 1]


CLAIMING = ("from app.ui.drawer import EditDrawer\n\n"
            "def fail_expired(q):\n    q.with_for_update()\n    EditDrawer()\n\n"
            "class Jobs:\n    def claim(self, q):\n        def inner():\n            q.with_for_update()\n"
            "        return inner\n\n"
            "q.with_for_update()\n")
ONE_CLAIM = {
    "read": "method-call", "in": {"part": "store"}, "keep": [{"named": "with_for_update"}],
    "may_not": "exist", "message": "{file} claims rows at line {line}, in '{function}'",
    "fix": "claim them through the shared claim",
    "examples": {"flagged": {"store/x.py": "def f(q):\n    q.with_for_update()\n"},
                 "clean": {"store/x.py": "def f(q):\n    q.all()\n"}}}
DRAWN = {
    "read": "call", "in": {"part": "store"}, "may_not": {"path": ["app.ui.drawer.EditDrawer"]},
    "message": "{path} at line {line}, in '{function}'", "fix": "leave the drawer to the ui",
    "examples": {"flagged": {"store/x.py": "from app.ui.drawer import EditDrawer\n\nEditDrawer()\n"},
                 "clean": {"store/x.py": "from app.ui.drawer import Other\n\nOther()\n"}}}


def test_a_call_carries_the_function_or_method_of_the_top_level_it_sits_in(tmp_path):
    """A call in a function nested in a method is the method's; one at the top level of the file is in none."""
    assert found(tmp_path, {"one-claim": ONE_CLAIM, "drawn": DRAWN}, {"store/x.py": CLAIMING}) == [
        ("app/store/x.py", 4, "app/store/x.py claims rows at line 4, in 'fail_expired'"),
        ("app/store/x.py", 5, "app.ui.drawer.EditDrawer at line 5, in 'fail_expired'"),
        ("app/store/x.py", 10, "app/store/x.py claims rows at line 10, in 'claim'"),
        ("app/store/x.py", 13, "app/store/x.py claims rows at line 13, in ''")]


def test_an_accepted_entry_that_names_a_function_accepts_the_calls_in_that_function_alone(tmp_path):
    accepted = {**ONE_CLAIM, "accepted": [{"file": "store/x.py", "function": "fail_expired",
                                           "why": "it claims what expired, once"}]}
    assert [line for _, line, _ in found(tmp_path, {"one-claim": accepted}, {"store/x.py": CLAIMING})] == [10, 13]


ROWS_OUT = {
    "read": "function", "in": {"part": "store"}, "keep": [{"returns-annotated": "*Row|*Row]|*Row,*"}],
    "may_not": "exist", "message": "{name} returns {returns} at line {line}", "fix": "return a value of the domain",
    "examples": {"flagged": {"store/x.py": "def load() -> list[UserRow]: ...\n"},
                 "clean": {"store/x.py": "def load() -> RowId: ...\n"}}}


def test_a_pattern_may_write_alternatives_so_a_type_ending_in_a_word_is_told_from_one_holding_it(tmp_path):
    """`*Row*` would match RowId and CredentialRowsPage too; the alternatives match only a type that ends in Row."""
    files = {"store/x.py": ("def a() -> UserRow: ...\ndef b() -> list[UserRow]: ...\ndef c() -> dict[UserRow, int]: ...\n"
                            "def d() -> RowId: ...\ndef e() -> CredentialRowsPage: ...\n")}
    assert [line for _, line, _ in found(tmp_path, {"rows-out": ROWS_OUT}, files)] == [1, 2, 3]
