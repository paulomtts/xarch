"""FsSourceTree on real files: the calls and classes a file holds, each name read through the import that binds it."""
from dataclasses import replace
from pathlib import Path

import pytest

from xarch.kernel.logic.testing import CaseTable
from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.values import (
    Call,
    Callback,
    Class,
    Method,
    MethodCall,
    ParameterCall,
    Row,
    Signature,
    SoleCall,
    SourceFile,
    Table,
    Use,
)
from xarch.platform.filesystem import FileSystem

PYTEST = CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues"))


def parsed(tmp_path: Path, text: str, table: CaseTable | None = PYTEST) -> SourceFile:
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
               Method(8, "later", "None")), ("size",), fields=("size",)),
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


OTHER = CaseTable(("cases", "table"), ("cases", "row"), "name", ("names", "rows"))
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
    form = CaseTable(("cases", "table"), ("cases", "row"), "name")
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
    assert tree.existing([tmp_path / "a", tmp_path / "a" / "x.py", tmp_path / "b"]) == {tmp_path / "a",
                                                                                         tmp_path / "a" / "x.py"}


def test_a_root_that_is_no_folder_is_absent_in_the_order_given(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "f.py").write_text("")
    tree = FsSourceTree(FileSystem())
    assert tree.absent([tmp_path / "f.py", tmp_path / "a", tmp_path / "b"]) == [tmp_path / "f.py", tmp_path / "b"]


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


@pytest.mark.parametrize("body, call", [
    pytest.param("return self.repo.get(id)", SoleCall(('self', 'repo', 'get'), ('id',)), id="a return of one call on a collaborator"),
    pytest.param("self.repo.save(id)", SoleCall(('self', 'repo', 'save'), ('id',)), id="a bare call"),
    pytest.param("return await self.repo.get(id)", SoleCall(('self', 'repo', 'get'), ('id',)), id="an awaited call"),
    pytest.param("return self.repo.get(id=id)", SoleCall(('self', 'repo', 'get'), (), (('id', 'id'),)),
                 id="a keyword with the parameter's value"),
    pytest.param("return self.repo.get(other=id)", SoleCall(('self', 'repo', 'get'), (), (('other', 'id'),)),
                 id="a keyword of another name"),
    pytest.param("return self.a.b.get(id)", SoleCall(('self', 'a', 'b', 'get'), ('id',)), id="a deeper chain"),
    pytest.param('"""Doc."""\n        return self.repo.get(id)', SoleCall(('self', 'repo', 'get'), ('id',)),
                 id="a docstring is no statement"),
    pytest.param("return self.repo.get(id, 1)", SoleCall(('self', 'repo', 'get'), ('id', '')), id="an extra argument"),
    pytest.param("return self.repo.get(id + 1)", SoleCall(('self', 'repo', 'get'), ('',)), id="a changed argument"),
    pytest.param("return self.repo.get(str(id))", SoleCall(('self', 'repo', 'get'), ('',)), id="a transformed argument"),
    pytest.param("return self.repo.get()", SoleCall(('self', 'repo', 'get')), id="a parameter that is not passed"),
    pytest.param("return self.repo.get(id, id)", SoleCall(('self', 'repo', 'get'), ('id', 'id')), id="a parameter passed twice"),
    pytest.param("return self.repo.get(id) or None", None, id="a changed result"),
    pytest.param("x = self.repo.get(id)\n        return x", None, id="two statements"),
    pytest.param("if id:\n            return self.repo.get(id)", None, id="a condition"),
    pytest.param("return self.helper(id)", SoleCall(('self', 'helper'), ('id',)), id="a method of the object itself, no collaborator"),
    pytest.param("return other.repo.get(id)", SoleCall(('other', 'repo', 'get'), ('id',)),
                 id="a chain that does not start at the first parameter"),
    pytest.param("return self.repo.get(id).name", SoleCall(('self', 'repo', 'get'), ('id',), then=('name',)),
                 id="a read of the result"),
    pytest.param("return (await self.repo.get(id)).value.text",
                 SoleCall(('self', 'repo', 'get'), ('id',), then=('value', 'text')), id="a chain read of an awaited result"),
    pytest.param("self.repo.get(id).name", None, id="a read of the result that is not returned"),
    pytest.param("return self.repo.get(id).name()", SoleCall(()), id="a call on the result is the call"),
    pytest.param("return self.repo.get(id)[0]", None, id="an item of the result"),
    pytest.param("return self.repo.get(self.repo.size(), id)", SoleCall(('self', 'repo', 'get'), ('', 'id')),
                 id="a call inside the arguments"),
])
def test_the_one_call_a_whole_body_makes_is_recorded_with_its_callee_and_arguments(tmp_path, body, call):
    text = f"class S:\n    async def get(self, id):\n        {body}\n"
    found = functions_of(tmp_path, text)["get"]
    assert (found.sole_call, found.signature, found.decorated) == (call, Signature(("self", "id")), False)


def test_a_function_records_its_parameters_by_kind_and_whether_it_is_decorated(tmp_path):
    text = ("class S:\n    def a(self, *args, **kwargs):\n        return self.r.a(*args, **kwargs)\n"
            "    @property\n    def c(self, k, *, only):\n        return self.r.c(k, only=only)\n")
    found = functions_of(tmp_path, text)
    assert (found["a"].signature, found["a"].sole_call, found["a"].decorated) == (
        Signature(("self",), (), "args", "kwargs"), SoleCall(("self", "r", "a"), ("*args",), (("**", "kwargs"),)), False)
    assert (found["c"].signature, found["c"].decorated) == (Signature(("self", "k"), ("only",)), True)


def test_a_file_names_every_name_it_mentions_annotations_and_string_annotations_included(tmp_path):
    text = ("from app.ports import Repo, Clock as C\nimport app.stores as stores\n\n\n"
            "class S:\n    def __init__(self, repo: Repo, other: 'Notifier | None', extra: list['Late']) -> None:\n"
            "        self.s = stores.Store()\n        self.size: Sized = 0\n")
    named = parsed(tmp_path, text).named
    assert {"Repo", "Clock", "stores", "Store", "Notifier", "Late", "Sized"} <= named
    cls = parsed(tmp_path, text).classes[0]
    assert {"Repo", "Notifier", "Store"} <= cls.named and "Clock" not in cls.named


@pytest.mark.parametrize("text, found", [
    pytest.param("def a(check, path):\n    return check(path)\n", [Callback(2, "a", "check", False)],
                 id="a function calls a parameter by its bare name"),
    pytest.param("def a(rows, key):\n    return sorted(rows, key=key)\n", [],
                 id="a parameter passed on is no call of it"),
    pytest.param("def a(p):\n    return p.read()\n", [], id="a method of a parameter is no call of it"),
    pytest.param("def a(f):\n    f = g\n    f()\n", [], id="a parameter the body rebinds is not read"),
    pytest.param("def a(f):\n    def b():\n        return f()\n    return [f(x) for x in y]\n",
                 [Callback(3, "a", "f", False), Callback(4, "a", "f", False)],
                 id="a nested function and a comprehension call the parameter of the function around them"),
    pytest.param("def a(f):\n    def b(f):\n        return f()\n", [Callback(3, "b", "f", False)],
                 id="the nearest function's parameter is the one read"),
    pytest.param("g = lambda f: f()\n", [Callback(1, "<lambda>", "f", False)], id="a lambda calls its parameter"),
    pytest.param("class C:\n    def a(self, f):\n        self()\n        f()\n"
                 "    @classmethod\n    def b(cls):\n        return cls()\n"
                 "    @staticmethod\n    def c(f):\n        return f()\n",
                 [Callback(3, "a", "self", True), Callback(4, "a", "f", False), Callback(7, "b", "cls", True),
                  Callback(10, "c", "f", False)],
                 id="the first parameter of a method is its receiver, but for a staticmethod"),
    pytest.param("f = 1\nf()\n", [], id="a module-level name is no parameter"),
])
def test_a_call_of_a_parameter_by_its_bare_name_is_listed_with_its_function(tmp_path, text, found):
    assert list(parsed(tmp_path, text).callbacks) == found


@pytest.mark.parametrize("text, exceptions", [
    pytest.param("class E(Exception): ...\nclass F(ValueError): ...\nclass G(E): ...\nclass H: ...\n",
                 {"E": True, "F": True, "G": True, "H": False},
                 id="a class deriving from a builtin exception, or from such a class of the file, is an exception"),
    pytest.param("Exception = object\nclass E(Exception): ...\n", {"E": False},
                 id="a name the file rebinds is no builtin"),
    pytest.param("from app.errors import Base\nclass E(Base): ...\n", {"E": False},
                 id="a base from another file is not known here"),
])
def test_a_class_says_whether_it_derives_from_a_builtin_exception(tmp_path, text, exceptions):
    assert {c.name: c.exception for c in parsed(tmp_path, text).classes} == exceptions


def test_a_function_lists_the_names_its_return_annotation_mentions(tmp_path):
    text = "def a() -> 'Found | None':\n    ...\ndef b() -> list[Row]:\n    ...\ndef c():\n    ...\n"
    assert {n: f.returns_named for n, f in functions_of(tmp_path, text).items()} == {
        "a": frozenset({"Found"}), "b": frozenset({"list", "Row"}), "c": frozenset()}


@pytest.mark.parametrize("annotation, annotated", [
    pytest.param("Callable[[str], bool]", True, id="typing's Callable, subscripted"),
    pytest.param("abc.Callable", True, id="collections.abc's"),
    pytest.param("Callable | None", True, id="in a union"),
    pytest.param("Optional[Callable]", True, id="inside Optional"),
    pytest.param("'Callable[[str], bool]'", True, id="a string annotation"),
    pytest.param("Check", False, id="another type"),
    pytest.param("list[Callable]", False, id="a container of callables"),
])
def test_a_callback_says_whether_its_parameter_is_annotated_as_a_callable(tmp_path, annotation, annotated):
    text = (f"from typing import Callable, Optional\nfrom collections import abc\n"
            f"def a(check: {annotation}):\n    return check()\n")
    assert [c.annotated for c in parsed(tmp_path, text).callbacks] == [annotated]


@pytest.mark.parametrize("text, fields", [
    pytest.param("class A:\n    x: int\n    y: str = ''\n    z: list = field(default_factory=list)\n", ("x", "y", "z"),
                 id="the names annotated in the class body, in order, with or without a default"),
    pytest.param("class A:\n    x = 1\n    def __init__(self):\n        self.y: int = 2\n", (),
                 id="an assignment with no annotation and an annotated attribute of self are no field"),
    pytest.param("from typing import ClassVar\nimport typing\nclass A:\n    x: ClassVar[int] = 1\n"
                 "    y: typing.ClassVar = 2\n    z: int\n", ("z",), id="a class variable is no field"),
    pytest.param("class A:\n    if flag:\n        x: int\n    class B:\n        y: int\n", (),
                 id="only a statement of the body itself declares one"),
])
def test_a_class_lists_its_fields_the_names_its_body_annotates_in_order(tmp_path, text, fields):
    assert parsed(tmp_path, text).classes[0].fields == fields


@pytest.mark.parametrize("text, found", [
    pytest.param("def a(path):\n    return path.resolve().absolute()\n",
                 [MethodCall(2, "absolute"), MethodCall(2, "resolve")], id="a method of a parameter, then of its result"),
    pytest.param("def a():\n    return make().resolve()\n", [MethodCall(2, "resolve")], id="a method of any expression"),
    pytest.param("from pathlib import Path\nimport os\ndef a():\n    return Path.cwd(), os.path.abspath('.')\n", [],
                 id="a callee an import binds is a call, not a method call"),
    pytest.param("class S:\n    def a(self):\n        return self._paths.resolve(), self.resolve()\n",
                 [MethodCall(3, "resolve", True), MethodCall(3, "resolve", True)],
                 id="a method of what the object holds, or of the object itself, is marked held"),
    pytest.param("class S:\n    def a(self, other):\n        return other.resolve(), self.x(1).resolve()\n",
                 [MethodCall(3, "resolve"), MethodCall(3, "x", True), MethodCall(3, "resolve")],
                 id="another parameter, or a result of a held call, is not held"),
    pytest.param("class S:\n    def a(self):\n        def inner():\n            return self.p.resolve()\n",
                 [MethodCall(4, "resolve", True)], id="the object is held in a nested function too"),
    pytest.param("class S:\n    @staticmethod\n    def a(self):\n        return self.resolve()\n",
                 [MethodCall(4, "resolve")], id="a static method has no object"),
    pytest.param("def a(f):\n    return f()\n", [], id="a call of a bare name is no method call"),
])
def test_a_call_of_an_attribute_no_import_binds_is_listed_as_a_method_call(tmp_path, text, found):
    assert sorted(parsed(tmp_path, text).method_calls, key=lambda c: (c.line, c.name, c.held)) == sorted(
        found, key=lambda c: (c.line, c.name, c.held))
