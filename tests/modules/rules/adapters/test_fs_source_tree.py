"""FsSourceTree on real files: the calls and classes a file holds, each name read through the import that binds it."""
from pathlib import Path

import pytest

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.values import Call, Class, Function, Method, Row, SourceFile, Table
from xarch.platform.filesystem import FileSystem


def parsed(tmp_path: Path, text: str) -> SourceFile:
    (tmp_path / "x.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)])[0]


def test_a_call_names_its_callee_by_the_path_its_import_binds(tmp_path):
    text = ("from unittest.mock import Mock, MagicMock as M\nimport unittest.mock\nimport unittest.mock as um\n"
            "from unittest import mock\n"
            "Mock()\nM()\nunittest.mock.AsyncMock()\num.create_autospec()\nmock.Mock()\nprint()\n")
    assert [c.func for c in parsed(tmp_path, text).calls] == [
        ("unittest", "mock", "Mock"), ("unittest", "mock", "MagicMock"), ("unittest", "mock", "AsyncMock"),
        ("unittest", "mock", "create_autospec"), ("unittest", "mock", "Mock")]


def test_a_call_keeps_its_arguments_as_paths_or_none(tmp_path):
    text = ("from unittest.mock import Mock\nfrom app.ports import Notifier\nimport app.ports as ports\n"
            "Mock(Notifier, 3, spec=ports.Repo, name='n')\nMock(*specs)\nMock(**options)\n")
    assert parsed(tmp_path, text).calls == (
        Call(4, ("unittest", "mock", "Mock"), (("app", "ports", "Notifier"), None),
             (("spec", ("app", "ports", "Repo")), ("name", None))),
        Call(5, ("unittest", "mock", "Mock"), unpacked=True),
        Call(6, ("unittest", "mock", "Mock"), unpacked=True))


def test_a_name_bound_otherwise_in_its_scope_is_not_read_through_the_import(tmp_path):
    text = ("from app.controller import Controller\nfrom unittest.mock import Mock\n"
            "def build(Controller):\n    return Controller()\n"
            "def other():\n    Mock = make()\n    return Mock(), Controller()\n"
            "def local():\n    from app.ports import Notifier\n    return Mock(spec=Notifier)\n"
            "[Mock(spec=Spec) for Spec in specs]\n")
    assert [(c.line, c.func, c.keywords) for c in parsed(tmp_path, text).calls] == [
        (7, ("app", "controller", "Controller"), ()),
        (10, ("unittest", "mock", "Mock"), (("spec", ("app", "ports", "Notifier")),)),
        (11, ("unittest", "mock", "Mock"), (("spec", None),))]


def test_a_name_imported_and_rebound_at_module_level_is_not_read_through_the_import(tmp_path):
    text = "from app.controller import Controller\nController = wrap(Controller)\nController()\n"
    assert parsed(tmp_path, text).calls == ()


def test_relative_imports_bind_nothing(tmp_path):
    assert parsed(tmp_path, "from .helpers import build\nbuild()\n").calls == ()


def test_a_class_lists_its_bases_as_paths_and_its_methods_with_their_return_annotations(tmp_path):
    text = ('import typing\nfrom typing import Protocol\n\n'
            'class Repo(Protocol):\n    def get(self, id: int) -> str | None: ...\n'
            '    def save(self, x) -> None: ...\n    def raw(self): ...\n'
            '    async def later(self) -> "None": ...\n    size: int\n'
            'class Typed(typing.Protocol[T], Base):\n    pass\n')
    assert parsed(tmp_path, text).classes == (
        Class(4, "Repo", (("typing", "Protocol"),),
              (Method(5, "get", "str | None"), Method(6, "save", "None"), Method(7, "raw", None),
               Method(8, "later", "None"))),
        Class(10, "Typed", (("typing", "Protocol"), None), ()))


TABLE = '''import pytest
from pytest import param as case

CASES = [pytest.param(1, Ok(), id="one")]


@pytest.mark.parametrize("given, when, then", [
    pytest.param([], Go(1), Missing(), id="a"),
    pytest.param([], Go(2), results.Published(1), marks=pytest.mark.slow),
    case(None, Go(3), Gone, id=""),
    ([], Go(4), []),
    other,
])
def test_go(given, when, then):
    if given:
        pass
    assert run(given, when) == then
'''


def test_a_parametrized_function_lists_its_rows_with_their_ids_and_the_names_heading_their_values(tmp_path):
    function = parsed(tmp_path, TABLE).functions[0]
    assert (function.name, function.line) == ("test_go", 14)
    assert function.tables == (Table(7, ("given", "when", "then"), (
        Row(8, True, "a", (None, "Go", "Missing")),
        Row(9, True, None, (None, "Go", "Published")),
        Row(10, True, None, (None, "Go", "Gone")),
        Row(11, False, None, (None, "Go", None)),
        Row(12, False, None, ()))),)


def test_a_function_lists_the_names_its_body_uses_and_its_branches(tmp_path):
    text = "def test_a():\n    for x in xs:\n        try:\n            Rejected(y.z)\n        finally:\n            pass\n"
    function = parsed(tmp_path, text).functions[0]
    assert function.mentions >= {"Rejected", "y", "z", "xs"}
    assert function.branches == ((2, "for"), (3, "try"))


@pytest.mark.parametrize("arguments, columns", [
    ('"a,b", [1]', ("a", "b")), ('"a", [1]', ("a",)), ('["a", "b"], [1]', ("a", "b")),
    ('("a", "b"), [1]', ("a", "b")), ('argnames="a", argvalues=[1]', ("a",))])
def test_the_parameter_names_are_read_from_a_string_or_a_sequence_of_strings(tmp_path, arguments, columns):
    text = f"import pytest\n\n@pytest.mark.parametrize({arguments})\ndef test_a(): ...\n"
    assert parsed(tmp_path, text).functions[0].tables[0].columns == columns


@pytest.mark.parametrize("rows, found", [
    ("CASES", 1), ("(pytest.param(1, id='a'),)", 1), ("load()", None), ("CASES + MORE", None), ("[*MORE]", None),
    ("MISSING", None), ("[x for x in y]", None)])
def test_rows_are_read_from_a_literal_or_the_name_of_a_module_level_one_else_they_are_unreadable(tmp_path, rows, found):
    text = f"import pytest\nCASES = [pytest.param(1, id='a')]\n\n@pytest.mark.parametrize('a', {rows})\ndef test_a(): ...\n"
    table = parsed(tmp_path, text).functions[0].tables[0]
    assert (None if table.rows is None else len(table.rows)) == found


def test_a_name_assigned_twice_is_not_a_list_literal(tmp_path):
    text = "import pytest\nCASES = [1]\nCASES = [2]\n\n@pytest.mark.parametrize('a', CASES)\ndef test_a(): ...\n"
    assert parsed(tmp_path, text).functions[0].tables[0].rows is None


def test_only_the_parametrize_of_pytest_makes_a_table(tmp_path):
    text = "import pytest\nfrom other import mark\n\n@mark.parametrize('a', [1])\n@pytest.mark.skip\ndef test_a(): ...\n"
    assert parsed(tmp_path, text).functions[0].tables == ()


def test_the_functions_of_a_class_are_listed_in_source_order(tmp_path):
    text = "def a(): ...\nclass K:\n    def b(self): ...\ndef c(): ...\n"
    assert [f.name for f in parsed(tmp_path, text).functions] == ["a", "b", "c"]
