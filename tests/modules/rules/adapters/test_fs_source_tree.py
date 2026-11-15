"""FsSourceTree on real files: the calls and classes a file holds, each name read through the import that binds it."""
from dataclasses import replace
from pathlib import Path

import pytest

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.values import (
    Call,
    Class,
    Method,
    ParameterCall,
    Row,
    SourceFile,
    Table,
    TableForm,
    Use,
)
from xarch.platform.filesystem import FileSystem

PYTEST = TableForm(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues"))


def parsed(tmp_path: Path, text: str, table: TableForm | None = PYTEST) -> SourceFile:
    (tmp_path / "x.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], table)[0]


def line_of(text: str, marker: str) -> int:
    """The line of text that holds marker, counted from 1, as the parser counts it."""
    return next(n for n, line in enumerate(text.splitlines(), 1) if marker in line)


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
    assert tuple(replace(c, named=frozenset()) for c in parsed(tmp_path, text).classes) == (
        Class(4, "Repo", (("typing", "Protocol"),),
              (Method(5, "get", "str | None"), Method(6, "save", "None"), Method(7, "raw", None),
               Method(8, "later", "None")), ("size",)),
        Class(10, "Typed", (("typing", "Protocol"), None), ()))


def test_a_use_names_what_it_reaches_by_the_path_its_import_binds_and_how_many_steps_the_import_bound(tmp_path):
    text = ("from datetime import datetime as dt\nimport datetime\nimport urllib.request\n"
            "dt.now()\ndatetime.datetime.now\nurllib.request.urlopen(url)\nf().now\nx = dt\n")
    assert parsed(tmp_path, text).uses == (
        Use(4, ("datetime", "datetime", "now"), 2), Use(5, ("datetime", "datetime", "now"), 1),
        Use(6, ("urllib", "request", "urlopen"), 1), Use(8, ("datetime", "datetime"), 2))


def test_a_builtin_is_used_by_its_bare_name_unless_its_scope_binds_the_name(tmp_path):
    text = ("open('x')\nprint\nundefined()\ndef f(open):\n    return open()\n"
            "def g():\n    print = log\n    print()\nclass C:\n    input = 1\n    def m(self):\n        input()\n"
            "import builtins\nbuiltins.open\n")
    assert parsed(tmp_path, text).uses == (
        Use(1, ("builtins", "open"), 0), Use(2, ("builtins", "print"), 0), Use(12, ("builtins", "input"), 0),
        Use(14, ("builtins", "open"), 1))


def test_a_name_rebound_at_module_level_or_a_star_import_hides_the_builtin(tmp_path):
    assert parsed(tmp_path, "open = safe_open\nopen('x')\n").uses == ()
    assert parsed(tmp_path, "from os import *\nopen('x')\n").uses == ()


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
    assert (function.name, function.line) == ("test_go", line_of(TABLE, "def test_go"))
    assert function.tables == (Table(line_of(TABLE, "@pytest.mark.parametrize"), ("given", "when", "then"), (
        Row(line_of(TABLE, "Go(1)"), True, "a", (None, "Go", "Missing")),
        Row(line_of(TABLE, "Go(2)"), True, None, (None, "Go", "Published")),
        Row(line_of(TABLE, "Go(3)"), True, None, (None, "Go", "Gone")),
        Row(line_of(TABLE, "Go(4)"), False, None, (None, "Go", None)),
        Row(line_of(TABLE, "other,"), False, None, ()))),)


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


OTHER = TableForm(("cases", "table"), ("cases", "row"), "name", ("names", "rows"))
OTHER_TEXT = ("import cases\nfrom cases import row\nimport pytest\n\n"
              "@cases.table('a, b', [row(1, 2, name='x'), cases.row(3, 4, id='y')])\ndef it_a(): ...\n\n"
              "@pytest.mark.parametrize('a', [1])\ndef it_b(): ...\n\n"
              "@cases.table(names='a', rows=[1])\ndef it_c(): ...\n")


def test_a_table_is_read_in_the_names_the_form_gives(tmp_path):
    functions = parsed(tmp_path, OTHER_TEXT, OTHER).functions
    a, c = line_of(OTHER_TEXT, "@cases.table('a, b'"), line_of(OTHER_TEXT, "@cases.table(names=")
    assert [(f.name, f.tables) for f in functions] == [
        ("it_a", (Table(a, ("a", "b"), (Row(a, True, "x", (None, None)), Row(a, True, None, (None, None)))),)),
        ("it_b", ()),
        ("it_c", (Table(c, ("a",), (Row(c, False, None, ()),)),)),
    ]


def test_without_keywords_only_positional_arguments_are_read(tmp_path):
    form = TableForm(("cases", "table"), ("cases", "row"), "name")
    functions = parsed(tmp_path, OTHER_TEXT, form).functions
    assert [len(f.tables) for f in functions] == [1, 0, 0]


def test_without_a_form_no_table_is_recognised(tmp_path):
    assert [f.tables for f in parsed(tmp_path, OTHER_TEXT, None).functions] == [(), (), ()]


def test_a_function_says_whether_its_body_holds_an_assert(tmp_path):
    text = "def test_a():\n    assert 1\n\ndef test_b():\n    Rejected()\n"
    assert [f.asserts for f in parsed(tmp_path, text).functions] == [True, False]


def test_a_class_lists_the_attributes_its_body_and_its_methods_assign(tmp_path):
    text = ("class FakeRepo:\n    size: int = 0\n    name = 'x'\n    def __init__(self, items):\n"
            "        self.items = items\n        self.seen: list = []\n        other.x = 1\n")
    assert parsed(tmp_path, text).classes[0].attributes == ("size", "name", "items", "seen")


def test_a_file_or_a_folder_exists_and_a_path_that_is_not_there_does_not(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.py").write_text("")
    tree = FsSourceTree(FileSystem())
    assert [tree.exists(tmp_path / "a"), tree.exists(tmp_path / "a" / "x.py"), tree.exists(tmp_path / "b")] == [
        True, True, False]


@pytest.mark.parametrize("text, calls", [
    pytest.param("X = 1\nfrom app import X\nX()\n", [], id="an assignment then an import of the name"),
    pytest.param("from app import X\nX = 1\nX()\n", [], id="an import then an assignment of the name"),
    pytest.param("from a import X\nfrom b import X\nX()\n", [], id="two different imports of the name"),
    pytest.param("if c:\n    from a import X\nelse:\n    X = None\nX()\n", [],
                 id="an import and an assignment in two branches"),
    pytest.param("from a import X\nfrom a import X\nX()\n", [("a", "X")], id="the same import twice is one binding"),
])
def test_a_name_with_two_different_bindings_in_its_scope_is_read_as_neither(tmp_path, text, calls):
    assert [c.func for c in parsed(tmp_path, text).calls] == calls


@pytest.mark.parametrize("text, calls", [
    pytest.param("class C:\n    from a import X\n    def m(self):\n        X()\n    X()\n", [(5, ("a", "X"))],
                 id="a name the class body imports is read in the body, not in its methods"),
    pytest.param("from a import X\nclass C:\n    X = 2\n    def m(self):\n        X()\n", [(5, ("a", "X"))],
                 id="a method reads past the class body to the module"),
    pytest.param("from a import X\nclass C:\n    X = 2\n    class D:\n        X()\n", [(5, ("a", "X"))],
                 id="a nested class body reads past the class around it to the module"),
    pytest.param("from a import X\nclass C:\n    X = 2\n    X()\n", [], id="the class body reads its own names"),
    pytest.param("from a import d\nclass C:\n    d = 1\n    @d()\n    def m(self): ...\n", [],
                 id="a method's decorator is read in the class body"),
    pytest.param("from a import d\nclass C:\n    @d()\n    def m(self): ...\n", [(3, ("a", "d"))],
                 id="a method's decorator the class body does not bind is read in the module"),
])
def test_a_class_body_binds_names_only_for_its_own_statements(tmp_path, text, calls):
    assert [(c.line, c.func) for c in parsed(tmp_path, text).calls] == calls


def test_a_class_base_is_read_in_the_scope_around_the_class_not_in_its_body(tmp_path):
    text = "from a import B\nclass C(B):\n    B = 1\n"
    assert parsed(tmp_path, text).classes[0].bases == (("a", "B"),)


ROWS = ("import pytest\nimport other\n\n@pytest.mark.parametrize('a', [other.param(1, id='x'), param(2, id='y'), "
        "pytest.param(3, id='z')])\ndef test_a(): ...\n")


def test_only_a_call_of_the_forms_row_is_a_row(tmp_path):
    assert [r.param for r in parsed(tmp_path, ROWS).functions[0].tables[0].rows] == [False, False, True]


@pytest.mark.parametrize("body, branches", [
    pytest.param("    async for x in y:\n        pass\n", ((2, "for"),), id="an async for is a for"),
    pytest.param("    while x:\n        pass\n", ((2, "while"),), id="a while"),
    pytest.param("    match x:\n        case _:\n            pass\n", ((2, "match"),), id="a match"),
    pytest.param("    try:\n        pass\n    except* E:\n        pass\n", ((2, "try"),), id="a try with except*"),
    pytest.param("    x = [y for y in z if y]\n", (), id="a comprehension is no branch"),
])
def test_a_loop_or_branch_of_any_kind_in_a_function_body_is_listed(tmp_path, body, branches):
    text = f"async def test_a():\n{body}"
    assert parsed(tmp_path, text).functions[0].branches == branches


def test_an_async_with_is_no_branch(tmp_path):
    assert parsed(tmp_path, "async def test_a():\n    async with x:\n        pass\n").functions[0].branches == ()


@pytest.mark.parametrize("text, unions", [
    pytest.param("R = A | B\n", [("R", ("A", "B"))], id="an assignment of names joined by |"),
    pytest.param("R: TypeAlias = A | B | C\n", [("R", ("A", "B", "C"))], id="an annotated assignment"),
    pytest.param("type R = A | B\n", [("R", ("A", "B"))], id="a type statement"),
    pytest.param("R = A\n", [], id="a single name is an alias, not a union"),
    pytest.param("type R = A\n", [], id="a type statement of a single name is an alias"),
    pytest.param("R = A | m.B\n", [], id="a member that is not a plain name"),
    pytest.param("R = A | None\n", [], id="None is a literal, not a plain name"),
    pytest.param("R: TypeAlias\n", [], id="an annotation with no value"),
    pytest.param("def f():\n    R = A | B\n", [], id="a union inside a function is not at module level"),
])
def test_a_union_is_a_module_level_alias_of_two_or_more_plain_names(tmp_path, text, unions):
    assert [(u.name, u.members) for u in parsed(tmp_path, text).unions] == unions


@pytest.mark.parametrize("text, found", [
    pytest.param("def test_a(mocker):\n    mocker.Mock()\n", [ParameterCall(2, "mocker", "Mock")],
                 id="a method called on a parameter is a call of that parameter"),
    pytest.param("from app.ports import Notifier\ndef test_a(mocker):\n    mocker.Mock(Notifier, spec=Notifier, name='n')\n",
                 [ParameterCall(3, "mocker", "Mock", (("app", "ports", "Notifier"),),
                                (("spec", ("app", "ports", "Notifier")), ("name", None)))],
                 id="its arguments are kept as a call keeps them"),
    pytest.param("def test_a(mocker):\n    mocker.Mock(*specs)\n    mocker.Mock(**options)\n",
                 [ParameterCall(2, "mocker", "Mock", unpacked=True), ParameterCall(3, "mocker", "Mock", unpacked=True)],
                 id="unpacked arguments are flagged"),
    pytest.param("async def test_a(mocker, *, other):\n    other.go()\n",
                 [ParameterCall(2, "other", "go")], id="an async function and a keyword-only parameter are read"),
    pytest.param("class T:\n    def test_a(self, mocker):\n        mocker.Mock()\n",
                 [ParameterCall(3, "mocker", "Mock")], id="a method's parameter is read"),
    pytest.param("def test_a(mocker):\n    mocker = other()\n    mocker.Mock()\n", [],
                 id="a parameter rebound in the body by an assignment is not read"),
    pytest.param("def test_a(mocker):\n    for mocker in many:\n        mocker.Mock()\n", [],
                 id="a parameter rebound by a loop is not read"),
    pytest.param("def test_a(mocker):\n    from unittest import mock as mocker\n    mocker.Mock()\n", [],
                 id="a parameter rebound by an import is not read"),
    pytest.param("def test_a(mocker):\n    def mocker(): ...\n    mocker.Mock()\n", [],
                 id="a parameter rebound by a def is not read"),
    pytest.param("def test_a(mocker):\n    mocker.patch.object(T, 'x')\n", [],
                 id="a call below a method of the parameter is not read"),
    pytest.param("def test_a(mocker):\n    mocker()\n    x = mocker.Mock\n", [],
                 id="a call of the parameter itself, or a method not called, is not read"),
    pytest.param("def test_a(mocker):\n    make().Mock()\n    (mocker or z).Mock()\n", [],
                 id="a method of anything but a bare name is not read"),
    pytest.param("def test_a(mocker):\n    def inner(other):\n        mocker.Mock()\n        other.Mock()\n",
                 [ParameterCall(3, "mocker", "Mock"), ParameterCall(4, "other", "Mock")],
                 id="a parameter of an enclosing function is read inside a nested one"),
    pytest.param("def test_a(mocker):\n    def inner(mocker):\n        mocker.Mock()\n", [ParameterCall(3, "mocker", "Mock")],
                 id="the nearest function's parameter is the one read"),
    pytest.param("def test_a(mocker):\n    f = lambda: mocker.Mock()\n    g = [mocker.Mock() for _ in range(2)]\n",
                 [ParameterCall(2, "mocker", "Mock"), ParameterCall(3, "mocker", "Mock")],
                 id="a lambda and a comprehension read the parameter around them"),
    pytest.param("mocker = make()\nmocker.Mock()\ndef test_a():\n    mocker.Mock()\n", [],
                 id="a module-level name is no parameter"),
    pytest.param("def test_a(mocker):\n    global mocker\n    mocker.Mock()\n", [],
                 id="a parameter declared global is not read"),
    pytest.param("class T:\n    mocker = 1\n    def test_a(self):\n        self.mocker.Mock()\n", [],
                 id="an attribute is no parameter"),
])
def test_a_call_of_a_method_of_a_parameter_is_listed_with_the_names_of_both(tmp_path, text, found):
    assert list(parsed(tmp_path, text).parameter_calls) == found


@pytest.mark.parametrize("text, found", [
    pytest.param("def build(): ...\nasync def later(): ...\n", ("build", "later"),
                 id="a def and an async def at module level are functions"),
    pytest.param("class Builder: ...\n", (), id="a class is no function"),
    pytest.param("def build(): ...\nbuild = other\n", (), id="a name assigned again is not read as a function"),
    pytest.param("def build(): ...\ndef build(): ...\n", (), id="a name defined twice is not read as a function"),
    pytest.param("from a import build\ndef build(): ...\n", (), id="a name imported and defined is not read"),
    pytest.param("class build: ...\ndef build(): ...\n", (), id="a name that is a class and a def is not read"),
    pytest.param("if x:\n    def build(): ...\nelse:\n    build = None\n", (),
                 id="a def in one branch and an assignment in another is not read"),
    pytest.param("if x:\n    def build(): ...\n", ("build",), id="a def in a branch bound once is a function"),
    pytest.param("class C:\n    def method(self): ...\ndef outer():\n    def inner(): ...\n", ("outer",),
                 id="a method and a nested def are no module-level function"),
    pytest.param("def build(): ...\n@decorate\ndef wrapped(): ...\n", ("build", "wrapped"),
                 id="a decorated def is still a function"),
    pytest.param("build = lambda: 1\nvalues = [1]\n", (), id="a lambda assigned is not a def"),
    pytest.param("def build(): ...\nglobal build\n", (), id="a name declared global is not read"),
])
def test_the_names_a_file_defines_as_functions_at_module_level_are_listed(tmp_path, text, found):
    assert parsed(tmp_path, text).module_functions == found


@pytest.mark.parametrize("make, listed", [
    pytest.param(lambda root: (root / "a.py").write_text(""), [("a.py",)], id="a file ending in .py is listed"),
    pytest.param(lambda root: (root / "__main__.py").mkdir(), [], id="a folder whose name ends in .py is not a source file"),
    pytest.param(lambda root: (root / "pkg" / "x.py").mkdir(parents=True), [],
                 id="nor is one below a folder, and its folder is not read as a file either"),
    pytest.param(lambda root: (root / "gone.py").symlink_to(root / "nowhere"), [],
                 id="a link that points at nothing is not a source file"),
])
def test_only_files_are_listed_as_source(tmp_path, make, listed):
    make(tmp_path)
    assert FsSourceTree(FileSystem()).paths(tmp_path) == listed


def functions_of(tmp_path: Path, text: str):
    return {f.name: f for f in parsed(tmp_path, text).functions}


def test_a_function_counts_its_real_statements_nested_ones_too_and_not_a_docstring_pass_or_ellipsis(tmp_path):
    text = ('def a(x):\n    """Doc."""\n    if x:\n        return 1\n    return 2\n\n'
            'def b():\n    """Doc."""\n    pass\n\ndef c():\n    ...\n\nclass K:\n    def m(self):\n        return 1\n')
    found = functions_of(tmp_path, text)
    assert (found["a"].statements, found["b"].statements, found["c"].statements, found["m"].statements) == (3, 0, 0, 1)
    assert (found["b"].shape, found["c"].shape) == ("", "")
    assert (found["a"].owner, found["m"].owner) == ("", "K")


def test_two_functions_have_one_shape_when_only_formatting_docstrings_and_local_names_differ(tmp_path):
    text = ('def a(items, limit):\n    """One."""\n    out = []\n    for item in items:\n        out.append(item.name)\n'
            '    return out[:limit]\n\n'
            'def b(rows,   cap):\n    result=[]\n    for row in rows:\n        result.append( row.name )\n'
            '    return result[:cap]\n')
    found = functions_of(tmp_path, text)
    assert found["a"].shape == found["b"].shape != ""


@pytest.mark.parametrize("other", [
    pytest.param("def b(items, limit):\n    out = []\n    for item in items:\n        out.append(item.title)\n"
                 "    return out[:limit]\n", id="another attribute"),
    pytest.param("def b(items, limit):\n    out = []\n    for item in items:\n        out.add(item.name)\n"
                 "    return out[:limit]\n", id="another method called"),
    pytest.param("def b(items, limit):\n    out = []\n    for item in items:\n        out.append(item.name)\n"
                 "    return out[:3]\n", id="another constant"),
    pytest.param("def b(items):\n    out = []\n    for item in items:\n        out.append(item.name)\n"
                 "    return out[:2]\n", id="another number of parameters"),
    pytest.param("async def b(items, limit):\n    out = []\n    for item in items:\n        out.append(item.name)\n"
                 "    return out[:limit]\n", id="async"),
    pytest.param("def b(items, limit):\n    out = []\n    for item in items:\n        sink(item.name)\n"
                 "    return out[:limit]\n", id="another function called"),
])
def test_a_change_of_what_is_called_or_read_changes_the_shape(tmp_path, other):
    one = 'def a(items, limit):\n    out = []\n    for item in items:\n        out.append(item.name)\n    return out[:limit]\n'
    found = functions_of(tmp_path, one + "\n" + other)
    assert found["a"].shape != found["b"].shape


def test_annotations_defaults_and_decorators_are_no_part_of_the_shape(tmp_path):
    text = ('def a(x: int, y=1) -> int:\n    z = x + y\n    return z\n\n'
            '@staticmethod\ndef b(p: str, q="s") -> str:\n    r = p + q\n    return r\n')
    found = functions_of(tmp_path, text)
    assert found["a"].shape == found["b"].shape


@pytest.mark.parametrize("body, forwards", [
    pytest.param("return self.repo.get(id)", "self.repo.get", id="a return of one call on a collaborator"),
    pytest.param("self.repo.save(id)", "self.repo.save", id="a bare call"),
    pytest.param("return await self.repo.get(id)", "self.repo.get", id="an awaited call"),
    pytest.param("return self.repo.get(id=id)", "self.repo.get", id="a keyword with the parameter's value"),
    pytest.param("return self.repo.get(other=id)", "self.repo.get", id="a keyword of another name"),
    pytest.param("return self.a.b.get(id)", "self.a.b.get", id="a deeper chain"),
    pytest.param('"""Doc."""\n        return self.repo.get(id)', "self.repo.get", id="a docstring is no statement"),
    pytest.param("return self.repo.get(id, 1)", "", id="an extra argument"),
    pytest.param("return self.repo.get(id + 1)", "", id="a changed argument"),
    pytest.param("return self.repo.get(str(id))", "", id="a transformed argument"),
    pytest.param("return self.repo.get()", "", id="a parameter that is not passed"),
    pytest.param("return self.repo.get(id, id)", "", id="a parameter passed twice"),
    pytest.param("return self.repo.get(id) or None", "", id="a changed result"),
    pytest.param("x = self.repo.get(id)\n        return x", "", id="two statements"),
    pytest.param("if id:\n            return self.repo.get(id)", "", id="a condition"),
    pytest.param("return self.helper(id)", "", id="a method of the object itself, no collaborator"),
    pytest.param("return other.repo.get(id)", "", id="a chain that does not start at the first parameter"),
    pytest.param("return self.repo.get(id).name", "", id="a read of the result"),
    pytest.param("return self.repo.get(self.repo.size(), id)", "", id="a call inside the arguments"),
])
def test_a_method_that_only_forwards_names_the_call_it_forwards_to(tmp_path, body, forwards):
    text = f"class S:\n    async def get(self, id):\n        {body}\n"
    assert functions_of(tmp_path, text)["get"].forwards == forwards


def test_a_method_forwards_its_starred_arguments_and_nothing_else_does(tmp_path):
    text = ("class S:\n    def a(self, *args, **kwargs):\n        return self.r.a(*args, **kwargs)\n"
            "    def b(self, *args):\n        return self.r.b(args)\n"
            "    @property\n    def c(self):\n        return self.r.c()\n"
            "    def __len__(self):\n        return self.r.size()\n"
            "    def d(self):\n        return self.r.d()\n")
    found = functions_of(tmp_path, text)
    assert [(n, f.forwards) for n, f in found.items()] == [
        ("a", "self.r.a"), ("b", ""), ("c", ""), ("__len__", ""), ("d", "self.r.d")]


def test_a_file_names_every_name_it_mentions_annotations_and_string_annotations_included(tmp_path):
    text = ("from app.ports import Repo, Clock as C\nimport app.stores as stores\n\n\n"
            "class S:\n    def __init__(self, repo: Repo, other: 'Notifier | None', extra: list['Late']) -> None:\n"
            "        self.s = stores.Store()\n        self.size: Sized = 0\n")
    named = parsed(tmp_path, text).named
    assert {"Repo", "Clock", "stores", "Store", "Notifier", "Late", "Sized"} <= named
    cls = parsed(tmp_path, text).classes[0]
    assert {"Repo", "Notifier", "Store"} <= cls.named and "Clock" not in cls.named
