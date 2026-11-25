"""FsSourceTree on real files: the calls and classes a file holds, each name read through the import that binds it."""
import sys
from dataclasses import replace
from importlib import resources
from pathlib import Path

import pytest
import yaml

from xarch.kernel.source import Import, Unparsable
from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.contract import Piece
from xarch.modules.rules.domain.parsed import (
    Call,
    Callback,
    Class,
    Comment,
    Constant,
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
from xarch.modules.rules.domain.parsed import Test as DeclaredTest
from xarch.platform.filesystem import FileSystem
from xarch.profile_values.language import InterfaceMark, RecordMark
from xarch.profile_values.testing import Place, RowId, TableForm
from xarch.profile_values.testing import TestForm as DeclaredForm

PYTEST = TableForm(Place(0, "argnames"), Place(1, "argvalues"), ("pytest", "param"), RowId(keyword="id"),
                   decorator=("pytest", "mark", "parametrize"))
LOOP = TableForm("bound", None, (), RowId(position=0), loop=True)
"""A form whose rows a loop of the test's body runs, each a tuple or list literal whose id is its first value."""
LOOP_CALL = TableForm("bound", None, ("app", "cases", "case"), RowId(keyword="name"), loop=True)
"""A form whose rows a loop of the test's body runs, each a call of app.cases.case whose id is its keyword name."""
STANDARD = frozenset(sys.stdlib_module_names)
"""The modules spec hands the reader for the language the tests' sources are written in: the interpreter's standard
library."""
PRIVATE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["private"]
"""How the language the tests' sources are written in starts a private name, as its data file says it."""
SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["special"]
"""The pattern of a special name of the language the tests' sources are written in, as its data file says it."""
HANDED = {"private": PRIVATE, "special": SPECIAL}
"""What the reader is handed of the language's tokens, as `check` hands it."""


def parsed(tmp_path: Path, text: str, tables: tuple[TableForm, ...] = (PYTEST,)) -> SourceFile:
    (tmp_path / "x.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], tables, standard=STANDARD, **HANDED)[0]


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


ORDER = "app/domain/order.py"
SERVICES = "app/domain/services.py"


def read_at(tmp_path: Path, files: dict[str, str], path: str) -> SourceFile:
    """The file at path, its first step the root it is read below, once every file given is written below tmp_path."""
    for rel, body in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(body)
    root, *steps = path.split("/")
    return FsSourceTree(FileSystem()).read(tmp_path / root, [tuple(steps)], standard=STANDARD, **HANDED)[0]


def test_a_relative_import_of_a_name_binds_the_place_it_names(tmp_path):
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: "from .order import Order\n\nOrder()\n"}, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)
    assert found.imports == (Import(1, ("order",), ("Order",), relative=True, up=0, written=".order"),)


def test_a_module_imported_relatively_is_the_place_its_names_are_read_on(tmp_path):
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: "from . import order\n\norder.Order()\n"}, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)
    assert found.imports == (Import(1, (), ("order",), relative=True, up=0, written="."),)


def test_a_relative_import_with_more_dots_climbs_a_folder_for_each(tmp_path):
    text = "from ..kernel.errors import Failed\nfrom .. import kernel\n\nFailed\nkernel\n"
    found = read_at(tmp_path, {"app/kernel/errors.py": "class Failed(Exception): ...\n", SERVICES: text}, SERVICES)
    assert found.uses == (Use(4, ("app", "kernel", "errors", "Failed"), 0), Use(5, ("app", "kernel"), 0))
    assert [(i.up, i.unresolved) for i in found.imports] == [(1, False), (1, False)]


def test_a_package_file_imports_relatively_from_its_own_folder(tmp_path):
    init = "app/domain/__init__.py"
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", init: "from .order import Order\n\nOrder()\n"}, init)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)


def test_an_alias_of_a_relative_import_keeps_the_place_it_names(tmp_path):
    text = "from .order import Order as O\nfrom . import order as o\n\nO()\no.Order()\n"
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: text}, SERVICES)
    assert found.calls == (Call(4, ("app", "domain", "order", "Order")), Call(5, ("app", "domain", "order", "Order")))


def test_a_relative_import_of_a_folder_is_followed_to_it(tmp_path):
    files = {"app/domain/order/__init__.py": "class Order: ...\n", SERVICES: "from .order import Order\n\nOrder()\n"}
    found = read_at(tmp_path, files, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")),)
    assert found.imports[0].unresolved is False


def test_a_relative_import_of_nothing_below_the_root_binds_nothing_and_is_unresolved(tmp_path):
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: "from .ordr import Order\n\nOrder()\n"}, SERVICES)
    assert (found.calls, found.uses) == ((), ())
    assert found.imports == (Import(1, ("ordr",), ("Order",), relative=True, up=0, written=".ordr", unresolved=True),)


@pytest.mark.parametrize("text", [
    pytest.param("from .. import x\n\nx()\n", id="one folder above a file at the root"),
    pytest.param("from ... import x\n\nx()\n", id="two folders above it"),
    pytest.param("from ..up import x\n\nx()\n", id="a module of a folder above it"),
])
def test_a_relative_import_that_climbs_above_the_root_binds_nothing_and_is_unresolved(tmp_path, text):
    found = read_at(tmp_path, {"app/a.py": text}, "app/a.py")
    assert (found.calls, [i.unresolved for i in found.imports]) == ((), [True])


def test_a_file_at_the_root_imports_relatively_from_the_root_s_own_folder(tmp_path):
    found = read_at(tmp_path, {"app/a.py": "from . import b\n\nb()\n"}, "app/a.py")
    assert (found.calls, [i.unresolved for i in found.imports]) == ((Call(3, ("app", "b")),), [False])


def test_a_name_imported_relatively_reaches_every_reading_at_its_place_bound_none_of_its_steps(tmp_path):
    text = ("from unittest.mock import Mock\nfrom .base import Base\nfrom .ports import Repo\n\n\nclass Store(Base): ...\n\n\n"
            "def build(repo: Repo):\n    return Mock(spec=Repo)\n")
    files = {"app/domain/base.py": "class Base: ...\n", "app/domain/ports.py": "class Repo: ...\n", SERVICES: text}
    found = read_at(tmp_path, files, SERVICES)
    assert found.classes[0].bases == (("app", "domain", "base", "Base"),)
    assert found.calls == (Call(10, ("unittest", "mock", "Mock"), (), (("spec", ("app", "domain", "ports", "Repo")),)),)
    assert Use(9, ("app", "domain", "ports", "Repo"), 0) in found.uses


def test_a_relative_import_in_a_function_or_a_class_body_is_followed_there(tmp_path):
    text = ("def make():\n    from .order import Order\n    return Order()\n\n\n"
            "class Shop:\n    from .order import Order\n    built = Order()\n")
    found = read_at(tmp_path, {ORDER: "class Order: ...\n", SERVICES: text}, SERVICES)
    assert found.calls == (Call(3, ("app", "domain", "order", "Order")), Call(8, ("app", "domain", "order", "Order")))


def test_an_absolute_import_is_resolved_and_read_as_before(tmp_path):
    found = read_at(tmp_path, {SERVICES: "from app.domain.order import Order\nimport os\n\nOrder()\nos.getcwd()\n"}, SERVICES)
    assert [i.unresolved for i in found.imports] == [False, False]
    assert found.calls == (Call(4, ("app", "domain", "order", "Order")), Call(5, ("os", "getcwd")))
    assert found.uses == (Use(4, ("app", "domain", "order", "Order"), 4), Use(5, ("os", "getcwd"), 1))


def test_a_relative_import_of_a_file_beside_binds_its_name(tmp_path):
    files = {"app/domain/helpers.py": "def build(): ...\n", "app/domain/x.py": "from .helpers import build\nbuild()\n"}
    assert read_at(tmp_path, files, "app/domain/x.py").calls == (Call(2, ("app", "domain", "helpers", "build")),)


def test_a_text_read_with_no_file_follows_no_relative_import():
    found = FsSourceTree(FileSystem()).parsed("from .order import Order\nimport os\n\nOrder()\nos.getcwd()\n", STANDARD, **HANDED)
    assert found.calls == (Call(5, ("os", "getcwd")),)
    assert [i.unresolved for i in found.imports] == [True, False]


def test_a_test_file_s_relative_import_binds_a_place_of_the_tests(tmp_path):
    files = {"tests/fakes/repo.py": "class FakeRepo: ...\n",
             "tests/modules/test_x.py": "from ..fakes.repo import FakeRepo\n\nFakeRepo()\n"}
    found = read_at(tmp_path, files, "tests/modules/test_x.py")
    assert found.calls == (Call(3, ("tests", "fakes", "repo", "FakeRepo")),)


def test_a_relative_star_import_is_resolved_as_any_other_relative_import(tmp_path):
    found = read_at(tmp_path, {ORDER: "", SERVICES: "from .order import *\nfrom .ordr import *\n"}, SERVICES)
    assert [i.unresolved for i in found.imports] == [False, True]


def denied(self: FileSystem, path: Path) -> bool:
    raise PermissionError(13, "Permission denied", str(path))


def test_a_place_the_file_system_cannot_look_up_is_missing(tmp_path, monkeypatch):
    files = {ORDER: "class Order: ...\n", SERVICES: "from .order import Order\n\nOrder()\n"}
    for rel, body in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(body)
    monkeypatch.setattr(FileSystem, "is_dir", denied)
    monkeypatch.setattr(FileSystem, "is_file", denied)
    found = FsSourceTree(FileSystem()).read(tmp_path / "app", [("domain", "services.py")], standard=STANDARD, **HANDED)[0]
    assert (found.calls, [i.unresolved for i in found.imports]) == ((), [True])


def test_a_class_lists_its_bases_as_paths_and_its_methods_with_their_return_annotations(tmp_path):
    text = ('import typing\nfrom typing import Protocol\n\n'
            'class Repo(Protocol):\n    def get(self, id: int) -> str | None: ...\n'
            '    def save(self, x) -> None: ...\n    def raw(self): ...\n'
            '    async def later(self) -> "None": ...\n    size: int\n'
            'class Typed(typing.Protocol[T], Base):\n    pass\n')
    assert tuple(replace(c, named=frozenset()) for c in parsed(tmp_path, text).classes) == (
        Class(4, "Repo", (("typing", "Protocol"),),
              (Method(5, "get", "str | None"), Method(6, "save", "None"), Method(7, "raw", None),
               Method(8, "later", "None")), ("size",), fields=("size",), types=("int",)),
        Class(10, "Typed", (("typing", "Protocol"), None), ()))


MARKS = (RecordMark(base=("typing", "NamedTuple")),
         RecordMark(decorator=("dataclasses", "dataclass"), keywords=(("frozen", "True"),)))
"""The marks of an immutable record the language's data file writes, as its loader reads them."""


def immutable_of(tmp_path: Path, text: str, marks: tuple[RecordMark, ...]) -> bool:
    (tmp_path / "a.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], immutable=marks, standard=STANDARD,
                                           **HANDED)[0].classes[0].immutable


@pytest.mark.parametrize("text, immutable", [
    pytest.param("from dataclasses import dataclass\n@dataclass(frozen=True, order=True)\nclass A:\n    x: int\n", True,
                 id="a decorator a mark names, called with its keyword among others"),
    pytest.param("import dataclasses\n@dataclasses.dataclass(frozen=True)\nclass A:\n    x: int\n", True,
                 id="the decorator read through the import that binds it"),
    pytest.param("import dataclasses\n@dataclasses.dataclass(frozen=True, slots=True)\nclass A:\n    x: int\n", True,
                 id="through the module, with another keyword"),
    pytest.param("from dataclasses import dataclass\n@dataclass\nclass A:\n    x: int\n", False,
                 id="the decorator of a mark, bare"),
    pytest.param("from dataclasses import dataclass\n@dataclass()\nclass A:\n    x: int\n", False,
                 id="the decorator of a mark, called without its keyword"),
    pytest.param("from dataclasses import dataclass\n@dataclass(frozen=False)\nclass A:\n    x: int\n", False,
                 id="its keyword with another value"),
    pytest.param("from typing import NamedTuple\nclass A(NamedTuple):\n    x: int\n", True, id="a base a mark names"),
    pytest.param("import typing\nclass A(typing.NamedTuple):\n    x: int\n", True, id="the base read through the module"),
    pytest.param("from typing import NamedTuple\n@NamedTuple\nclass A:\n    x: int\n", False,
                 id="a decorator a base mark names"),
    pytest.param("from dataclasses import dataclass\nclass A(dataclass):\n    x: int\n", False,
                 id="a base a decorator mark names"),
    pytest.param("def dataclass(**k): ...\n@dataclass(frozen=True)\nclass A:\n    x: int\n", False,
                 id="a decorator no import binds"),
])
def test_a_class_is_an_immutable_record_when_a_base_mark_names_a_base_or_a_decorator_mark_a_decorator(tmp_path, text,
                                                                                                    immutable):
    assert immutable_of(tmp_path, text, MARKS) is immutable


@pytest.mark.parametrize("text, immutable", [
    pytest.param("from dataclasses import dataclass\n@dataclass\nclass A:\n    x: int\n", True, id="the decorator bare"),
    pytest.param("from dataclasses import dataclass\n@dataclass()\nclass A:\n    x: int\n", True, id="the decorator called"),
    pytest.param("from dataclasses import dataclass\n@dataclass(frozen=True)\nclass A:\n    x: int\n", True,
                 id="the decorator called with keywords"),
    pytest.param("from dataclasses import dataclass\nclass A(dataclass):\n    x: int\n", False, id="a base of that name"),
])
def test_a_decorator_mark_with_no_keywords_marks_the_decorator_however_it_is_written_and_no_base(tmp_path, text, immutable):
    assert immutable_of(tmp_path, text, (RecordMark(decorator=("dataclasses", "dataclass")),)) is immutable


@pytest.mark.parametrize("text", [
    pytest.param("from typing import Final\nclass A(Final):\n    readonly: int\n", id="a base named as a type mark"),
    pytest.param("from typing import Final\n@Final\nclass A:\n    readonly: int\n", id="a decorator named as a type mark"),
])
def test_a_fields_or_a_type_mark_marks_no_class_of_this_language(tmp_path, text):
    assert immutable_of(tmp_path, text, (RecordMark(fields="readonly"), RecordMark(type=("typing", "Final")))) is False


def test_no_class_is_an_immutable_record_when_the_reader_is_given_no_mark(tmp_path):
    text = "from typing import NamedTuple\nclass A(NamedTuple):\n    x: int\n"
    assert parsed(tmp_path, text).classes[0].immutable is False


INTERFACE = (InterfaceMark(("typing", "Protocol")), InterfaceMark(("typing_extensions", "Protocol")))


@pytest.mark.parametrize("text, interface", [
    pytest.param("from typing import Protocol\nclass P(Protocol): ...\n", True, id="a base a mark names"),
    pytest.param("import typing\nclass P(typing.Protocol): ...\n", True,
                 id="the base read through the import that binds it"),
    pytest.param("import typing_extensions\nclass P(typing_extensions.Protocol): ...\n", True, id="any of the marks"),
    pytest.param("from typing import Protocol, TypeVar\nT = TypeVar('T')\nclass P(Protocol[T]): ...\n", True,
                 id="a subscripted base names what it subscripts"),
    pytest.param("from typing import Protocol as Port\nclass P(Port): ...\n", True, id="an alias reaches the path"),
    pytest.param("class P: ...\n", False, id="a class with no base"),
    pytest.param("from typing import NamedTuple\nclass P(NamedTuple): ...\n", False, id="a base no mark names"),
    pytest.param("class Protocol: ...\nclass P(Protocol): ...\n", False,
                 id="a class of the file's own named like a mark"),
])
def test_a_class_is_an_interface_when_a_base_mark_names_one_of_its_bases(tmp_path, text, interface):
    (tmp_path / "a.py").write_text(text)
    read = FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], interface=INTERFACE, standard=STANDARD, **HANDED)[0]
    assert read.classes[-1].interface is interface


def test_no_class_is_an_interface_when_the_reader_is_given_no_mark(tmp_path):
    assert parsed(tmp_path, "from typing import Protocol\nclass P(Protocol): ...\n").classes[0].interface is False


@pytest.mark.parametrize("keyword", [pytest.param("Protocol", id="the name of a base"),
                                     pytest.param("class", id="the keyword of a class")])
def test_a_keyword_mark_marks_no_class_of_this_language(tmp_path, keyword):
    (tmp_path / "a.py").write_text("from typing import Protocol\nclass P(Protocol): ...\n")
    read = FsSourceTree(FileSystem()).read(tmp_path, [("a.py",)], interface=(InterfaceMark(keyword=keyword),),
                                           standard=STANDARD, **HANDED)[0]
    assert read.classes[0].interface is False


def test_a_use_names_what_it_reaches_by_the_path_its_import_binds_and_how_many_steps_the_import_bound(tmp_path):
    text = ("from datetime import datetime as dt\nimport datetime\nimport urllib.request\n"
            "dt.now()\ndatetime.datetime.now\nurllib.request.urlopen(url)\nf().now\nx = dt\n")
    assert parsed(tmp_path, text).uses == (
        Use(4, ("datetime", "datetime", "now"), 2), Use(5, ("datetime", "datetime", "now"), 1),
        Use(6, ("urllib", "request", "urlopen"), 1), Use(8, ("datetime", "datetime"), 2))


def test_an_annotation_is_a_use_of_what_it_names_a_signature_s_and_a_field_s_alike_but_not_a_string_s(tmp_path):
    text = ("import typing\nclass A:\n    x: typing.Any\ndef f(a: typing.Any, *b: typing.Any) -> typing.Any:\n"
            "    return a\ny: 'typing.Any' = 1\n")
    assert parsed(tmp_path, text).uses == (
        Use(3, ("typing", "Any"), 1), Use(4, ("typing", "Any"), 1), Use(4, ("typing", "Any"), 1),
        Use(4, ("typing", "Any"), 1))


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


LOOPED_TABLE = TABLE.replace("    if given:\n        pass\n", "    for each in CASES:\n        pass\n")
"""TABLE, the body of its test a loop over the list CASES of the file."""


def test_a_parametrized_function_lists_its_rows_with_their_ids_and_the_names_heading_their_values(tmp_path):
    function = parsed(tmp_path, TABLE).functions[0]
    assert (function.name, function.line) == ("test_go", line_of(TABLE, "def test_go"))
    assert function.tables == (Table(line_of(TABLE, "@pytest.mark.parametrize"), ("given", "when", "then"), (
        Row(line_of(TABLE, "Go(1)"), written=True, id="a", cells=(None, "Go", "Missing")),
        Row(line_of(TABLE, "Go(2)"), written=True, id=None, cells=(None, "Go", "Published")),
        Row(line_of(TABLE, "Go(3)"), written=True, id="", cells=(None, "Go", "Gone")),
        Row(line_of(TABLE, "Go(4)"), written=False, id=None, cells=(None, "Go", None)),
        Row(line_of(TABLE, "other,"), written=False, id=None, cells=())), form=0, runs=0),)


def test_a_function_lists_the_names_its_body_uses_and_its_branches(tmp_path):
    text = "def test_a():\n    for x in xs:\n        try:\n            Rejected(y.z)\n        finally:\n            pass\n"
    function = parsed(tmp_path, text).functions[0]
    assert function.mentions >= {"Rejected", "y", "z", "xs"}
    assert function.blocks == ((2, "for"), (3, "try"))


@pytest.mark.parametrize("arguments, columns", [
    ('"a,b", [1]', ("a", "b")), ('"a", [1]', ("a",)), ('["a", "b"], [1]', ("a", "b")),
    ('("a", "b"), [1]', ("a", "b")), ('argnames="a", argvalues=[1]', ("a",))])
def test_the_parameter_names_are_read_from_a_string_or_a_sequence_of_strings(tmp_path, arguments, columns):
    text = f"import pytest\n\n@pytest.mark.parametrize({arguments})\ndef test_a(): ...\n"
    assert parsed(tmp_path, text).functions[0].tables[0].columns == columns


@pytest.mark.parametrize("rows", ["CASES", "(pytest.param(1, id='a'),)"])
def test_rows_are_read_from_a_literal_or_the_name_of_a_module_level_one(tmp_path, rows):
    text = f"import pytest\nCASES = [pytest.param(1, id='a')]\n\n@pytest.mark.parametrize('a', {rows})\ndef test_a(): ...\n"
    assert len(parsed(tmp_path, text).functions[0].tables[0].rows) == 1


@pytest.mark.parametrize("rows", ["load()", "CASES + MORE", "[*MORE]", "MISSING", "[x for x in y]"])
def test_rows_that_are_no_literal_and_no_module_level_one_are_unreadable(tmp_path, rows):
    text = f"import pytest\nCASES = [pytest.param(1, id='a')]\n\n@pytest.mark.parametrize('a', {rows})\ndef test_a(): ...\n"
    assert parsed(tmp_path, text).functions[0].tables[0].rows is None


def test_a_name_assigned_twice_is_not_a_list_literal(tmp_path):
    text = "import pytest\nCASES = [1]\nCASES = [2]\n\n@pytest.mark.parametrize('a', CASES)\ndef test_a(): ...\n"
    assert parsed(tmp_path, text).functions[0].tables[0].rows is None


def test_only_the_parametrize_of_pytest_makes_a_table(tmp_path):
    text = "import pytest\nfrom other import mark\n\n@mark.parametrize('a', [1])\n@pytest.mark.skip\ndef test_a(): ...\n"
    assert parsed(tmp_path, text).functions[0].tables == ()


@pytest.mark.parametrize("text, count", [
    pytest.param("import pytest\n\n@pytest.mark.parametrize('a', load())\ndef test_a(): ...\n", 1,
                 id="a table whose rows cannot be read"),
    pytest.param("import pytest\nCASES = [pytest.param(1, id='a')]\n\n@pytest.mark.parametrize('a', CASES)\n"
                 "def test_a(): ...\n", 1, id="a table whose rows are a name assigned at the top of the file"),
    pytest.param("import pytest\n\n@pytest.mark.parametrize('a', [1])\n@pytest.mark.parametrize('b', [2])\n"
                 "def test_a(a, b): ...\n", 2, id="two tables of one function"),
    pytest.param("import pytest\nCASES = [1]\n\n@pytest.mark.parametrize('a', [1])\ndef test_a(a):\n"
                 "    for case in CASES:\n        assert case\n", 1, id="a test whose own body loops over cases"),
])
def test_every_table_the_reader_finds_is_read_by_the_first_form_and_run_by_no_statement(tmp_path, text, count):
    assert [(t.form, t.runs) for t in parsed(tmp_path, text).functions[0].tables] == [(0, 0)] * count


def test_the_functions_of_a_class_are_listed_in_source_order(tmp_path):
    text = "def a(): ...\nclass K:\n    def b(self): ...\ndef c(): ...\n"
    assert [f.name for f in parsed(tmp_path, text).functions] == ["a", "b", "c"]


OTHER = TableForm(Place(0, "names"), Place(1, "rows"), ("cases", "row"), RowId(keyword="name"),
                  decorator=("cases", "table"))
OTHER_TEXT = ("import cases\nfrom cases import row\nimport pytest\n\n"
              "@cases.table('a, b', [row(1, 2, name='x'), cases.row(3, 4, id='y')])\ndef it_a(): ...\n\n"
              "@pytest.mark.parametrize('a', [1])\ndef it_b(): ...\n\n"
              "@cases.table(names='a', rows=[1])\ndef it_c(): ...\n")


def test_a_table_is_read_in_the_names_the_form_gives(tmp_path):
    functions = parsed(tmp_path, OTHER_TEXT, (OTHER,)).functions
    a, c = line_of(OTHER_TEXT, "@cases.table('a, b'"), line_of(OTHER_TEXT, "@cases.table(names=")
    assert [(f.name, f.tables) for f in functions] == [
        ("it_a", (Table(a, ("a", "b"), (Row(a, True, "x", (None, None)), Row(a, True, None, (None, None))), form=0, runs=0),)),
        ("it_b", ()),
        ("it_c", (Table(c, ("a",), (Row(c, False, None, ()),), form=0, runs=0),)),
    ]


def test_without_keywords_only_positional_arguments_are_read(tmp_path):
    form = TableForm(Place(0), Place(1), ("cases", "row"), RowId(keyword="name"), decorator=("cases", "table"))
    functions = parsed(tmp_path, OTHER_TEXT, (form,)).functions
    assert [len(f.tables) for f in functions] == [1, 0, 0]


def test_under_a_place_with_a_keyword_alone_only_the_keyword_is_read(tmp_path):
    form = TableForm(Place(keyword="names"), Place(keyword="rows"), ("cases", "row"), RowId(keyword="name"),
                     decorator=("cases", "table"))
    functions = parsed(tmp_path, OTHER_TEXT, (form,)).functions
    assert [len(f.tables) for f in functions] == [0, 0, 1]


def test_without_a_form_no_table_is_recognised(tmp_path):
    assert [f.tables for f in parsed(tmp_path, OTHER_TEXT, ()).functions] == [(), (), ()]


def test_each_table_is_tagged_with_the_index_of_the_form_that_read_it(tmp_path):
    functions = parsed(tmp_path, OTHER_TEXT, (OTHER, PYTEST)).functions
    assert [[t.form for t in f.tables] for f in functions] == [[0], [1], [0]]


def test_a_table_read_by_the_second_form_is_tagged_with_its_index_and_read_the_same(tmp_path):
    first = parsed(tmp_path, TABLE).functions[0].tables[0]
    second = parsed(tmp_path, TABLE, (replace(PYTEST, decorator=("a", "cases")), PYTEST)).functions[0].tables[0]
    assert second == replace(first, form=1)


@pytest.mark.parametrize("skipped", [
    pytest.param(replace(PYTEST, row=()), id="a form whose rows are literals"),
    pytest.param(replace(PYTEST, id=RowId(position=0)), id="a form whose id is a position"),
    pytest.param(replace(PYTEST, columns_from="fields"), id="a form whose columns are the fields of each row"),
    pytest.param(replace(PYTEST, decorator=(), call=(("pytest", "mark", "parametrize"),)), id="a call form"),
    pytest.param(TableForm("fields", None, (), RowId(position=0), loop=True),
                 id="a loop form whose columns are the fields of each row"),
    pytest.param(TableForm("bound", None, ("pytest", "param"), RowId(position=0), loop=True),
                 id="a loop form whose call row has an id by position"),
    pytest.param(TableForm("bound", None, (), RowId(field="name"), loop=True),
                 id="a loop form whose literal row has an id by field"),
])
def test_a_form_the_reader_cannot_read_reads_no_table_and_the_next_form_still_does(tmp_path, skipped):
    assert parsed(tmp_path, LOOPED_TABLE, (skipped,)).functions[0].tables == ()
    assert [t.form for t in parsed(tmp_path, LOOPED_TABLE, (skipped, PYTEST)).functions[0].tables] == [1]


def test_the_text_the_forms_the_reader_cannot_read_are_tried_on_is_read_by_the_forms_it_reads(tmp_path):
    tables = parsed(tmp_path, LOOPED_TABLE, (PYTEST, LOOP)).functions[0].tables
    assert [(t.form, t.runs) for t in tables] == [(0, 0), (1, line_of(LOOPED_TABLE, "for each in CASES"))]


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
    assert [r.written for r in parsed(tmp_path, ROWS).functions[0].tables[0].rows] == [False, False, True]


@pytest.mark.parametrize("body, blocks", [
    pytest.param("    async for x in y:\n        pass\n", ((2, "for"),), id="an async for is a for"),
    pytest.param("    while x:\n        pass\n", ((2, "while"),), id="a while"),
    pytest.param("    match x:\n        case _:\n            pass\n", ((2, "match"),), id="a match"),
    pytest.param("    try:\n        pass\n    except* E:\n        pass\n", ((2, "try"),), id="a try with except*"),
    pytest.param("    x = [y for y in z if y]\n", (), id="a comprehension is no branch"),
])
def test_a_loop_or_branch_of_any_kind_in_a_function_body_is_listed(tmp_path, body, blocks):
    text = f"async def test_a():\n{body}"
    assert parsed(tmp_path, text).functions[0].blocks == blocks


@pytest.mark.parametrize("body, expressions", [
    pytest.param("    assert (x if y else z) == w\n", ((2, "if"),), id="a conditional expression is listed by if"),
    pytest.param("    a = [b if c else (d if e else f) for g in h]\n", ((2, "if"), (2, "if")),
                 id="nested ones too, one each"),
    pytest.param("    if x:\n        pass\n    a = [y for y in z if y]\n", (), id="a statement or a comprehension is none"),
])
def test_an_expression_that_chooses_between_values_in_a_function_body_is_listed(tmp_path, body, expressions):
    assert parsed(tmp_path, f"def test_a():\n{body}").functions[0].expressions == expressions


def test_an_async_with_is_a_block_opened_by_with(tmp_path):
    assert parsed(tmp_path, "async def test_a():\n    async with x:\n        pass\n").functions[0].blocks == (
        (2, "with"),)


@pytest.mark.parametrize("text, unions", [
    pytest.param("R = A | B\n", [("R", ("A", "B"))], id="an assignment of names joined by |"),
    pytest.param("R: TypeAlias = A | B | C\n", [("R", ("A", "B", "C"))], id="an annotated assignment"),
    pytest.param("type R = A | B\n", [("R", ("A", "B"))], id="a type statement"),
    pytest.param("R = A\n", [("R", ("A",))], id="a single name is an alias, listed with its one name"),
    pytest.param("type R = A\n", [("R", ("A",))], id="a type statement of a single name is an alias too"),
    pytest.param("R = A | m.B\n", [], id="a member that is not a plain name"),
    pytest.param("R = A | None\n", [], id="None is a literal, not a plain name"),
    pytest.param("R: TypeAlias\n", [], id="an annotation with no value"),
    pytest.param("def f():\n    R = A | B\n", [], id="a union inside a function is not at module level"),
])
def test_a_module_level_alias_of_plain_names_is_listed_with_its_names(tmp_path, text, unions):
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
    assert FsSourceTree(FileSystem()).paths(tmp_path, (".py",)) == listed


def functions_of(tmp_path: Path, text: str):
    return {f.name: f for f in parsed(tmp_path, text).functions}


def test_a_function_counts_its_real_statements_nested_ones_too_and_not_a_docstring_pass_or_ellipsis(tmp_path):
    text = ('def a(x):\n    """Doc."""\n    if x:\n        return 1\n    return 2\n\n'
            'def b():\n    """Doc."""\n    pass\n\ndef c():\n    ...\n\nclass K:\n    def m(self):\n        return 1\n')
    found = functions_of(tmp_path, text)
    assert (found["a"].real_statements, found["b"].real_statements, found["c"].real_statements,
            found["m"].real_statements) == (3, 0, 0, 1)
    assert (found["a"].inert, found["b"].inert, found["c"].inert) == (1, 2, 1)
    assert (found["b"].shape, found["c"].shape) == ("", "")
    assert (found["a"].owner, found["m"].owner) == ("", "K")


def test_the_files_listed_are_those_whose_name_ends_in_the_extension_given(tmp_path):
    (tmp_path / "a.py").write_text("")
    (tmp_path / "b.pas").write_text("")
    assert FsSourceTree(FileSystem()).paths(tmp_path, (".pas",)) == [("b.pas",)]


def test_the_files_listed_are_those_whose_name_ends_in_one_of_the_endings_given_each_once(tmp_path):
    (tmp_path / "b").mkdir()
    for name in ("x.d.ts", "a.ts", "b/c.tsx", "d.js"):
        (tmp_path / name).write_text("")
    assert FsSourceTree(FileSystem()).paths(tmp_path, (".ts", ".tsx", ".d.ts")) == [("a.ts",), ("b", "c.tsx"), ("x.d.ts",)]


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


@pytest.mark.parametrize("body, callee", [
    pytest.param("return self.repo.get(id)", "self.repo.get", id="a return of one call on a collaborator"),
    pytest.param("self.repo.save(id)", "self.repo.save", id="a bare call"),
    pytest.param("return await self.repo.get(id)", "self.repo.get", id="an awaited call"),
    pytest.param("return self.repo.get(id=id)", "self.repo.get", id="a keyword with the parameter's value"),
    pytest.param("return self.repo.get(other=id)", "self.repo.get", id="a keyword of another name"),
    pytest.param("return self.a.b.get(id)", "self.a.b.get", id="a deeper chain"),
    pytest.param('"""Get it."""\n        return self.repo.get(id)', "self.repo.get", id="a docstring is no statement"),
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
    pytest.param("return self.repo.get(id).name", "self.repo.get", id="a read of the result"),
    pytest.param("return self.repo.get(id, 1).name", "", id="a read of the result of a call that does not forward"),
    pytest.param("return self.repo.get(self.repo.size(), id)", "", id="a call inside the arguments"),
])
def test_a_method_forwards_when_its_one_call_passes_each_parameter_once_to_a_collaborator(tmp_path, body, callee):
    assert functions_of(tmp_path, f"class S:\n    async def get(self, id):\n        {body}\n")["get"].forwards == callee


@pytest.mark.parametrize("text, callee", [
    pytest.param("class S:\n    def a(self, *args, **kwargs):\n        return self.r.a(*args, **kwargs)\n", "self.r.a",
                 id="starred parameters passed on starred"),
    pytest.param("class S:\n    def a(self, *args):\n        return self.r.a(args)\n", "",
                 id="a starred parameter passed as one argument"),
    pytest.param("class S:\n    @property\n    def a(self):\n        return self.r.a()\n", "", id="a decorated method"),
    pytest.param("class S:\n    def __a__(self):\n        return self.r.size()\n", "", id="a special method"),
    pytest.param("class S:\n    def a(self, k, *, only):\n        return self.r.a(k, only=only)\n", "self.r.a",
                 id="a keyword-only parameter passed by keyword"),
    pytest.param("class S:\n    @staticmethod\n    def a():\n        return self.r.a()\n", "",
                 id="no first parameter to hold it"),
    pytest.param("def a(self):\n    return self.r.a()\n", "", id="a function of no class forwards nothing"),
])
def test_a_decorator_a_special_name_or_a_starred_parameter_passed_whole_decides_too(tmp_path, text, callee):
    (function,) = functions_of(tmp_path, text).values()
    assert function.forwards == callee


def test_a_file_names_every_name_it_mentions_annotations_and_string_annotations_included(tmp_path):
    text = ("from app.ports import Repo, Clock as C\nimport app.stores as stores\n\n\n"
            "class S:\n    def __init__(self, repo: Repo, other: 'Notifier | None', extra: list['Late']) -> None:\n"
            "        self.s = stores.Store()\n        self.size: Sized = 0\n")
    named = parsed(tmp_path, text).named
    assert {"Repo", "Clock", "stores", "Store", "Notifier", "Late", "Sized"} <= named
    cls = parsed(tmp_path, text).classes[0]
    assert {"Repo", "Notifier", "Store"} <= cls.named and "Clock" not in cls.named


@pytest.mark.parametrize("escape", [
    pytest.param("\\ud800", id="a lone surrogate, which the parser cannot encode"),
    pytest.param("a\\x00b", id="a null byte, which the parser refuses"),
    pytest.param("(" * 1000, id="a nesting too deep for the parser"),
])
def test_a_string_the_parser_cannot_read_as_code_is_ignored_and_the_file_is_still_read(tmp_path, escape):
    text = (f"from typing import ClassVar\nX = '{escape}'\nY = 'Box[Thing]'\n\n\n"
            f"class A:\n    z: '{escape}'\n\n\ndef f(check: '{escape}') -> '{escape}':\n    return check()\n")
    found = parsed(tmp_path, text)
    assert found.error is None
    assert {"Box", "Thing"} <= found.named
    assert found.classes[0].fields == ("z",)
    assert [c.annotated for c in found.callbacks] == [False]


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


@pytest.mark.parametrize("text, types", [
    pytest.param("class A:\n    x: int\n    y: tuple[str, ...] = ()\n    z: 'Path | None'\n",
                 ("int", "tuple[str, ...]", "Path | None"), id="each field's annotation as written, a string by its text"),
    pytest.param("from typing import ClassVar\nclass A:\n    x: ClassVar[int] = 1\n    y: m.Thing\n", ("m.Thing",),
                 id="a class variable has no field, so no type"),
])
def test_a_class_lists_the_type_of_each_field_as_its_annotation_is_written(tmp_path, text, types):
    assert parsed(tmp_path, text).classes[0].types == types


@pytest.mark.parametrize("text, constants", [
    pytest.param("A = 1\nB: int = 2\nC, D = 3, 4\n", [Constant(1, "A"), Constant(2, "B"), Constant(3, "C"),
                                                     Constant(3, "D")],
                 id="a name an assignment at the top level binds, an annotated one or one of several"),
    pytest.param("E: int\ndef f():\n    g = 1\nclass K:\n    h = 2\nx.y = 3\n", [],
                 id="an annotation with no value, a function's or a class's own name and an attribute bind none"),
    pytest.param("if flag:\n    A = 1\nelse:\n    A = 2\n", [Constant(2, "A"), Constant(4, "A")],
                 id="a branch at the top level binds too"),
    pytest.param("type Pair = tuple[int, int]\n", [Constant(1, "Pair")], id="a type alias"),
])
def test_a_file_lists_the_names_it_binds_at_the_top_level_by_an_assignment(tmp_path, text, constants):
    assert [replace(c, named=frozenset()) for c in parsed(tmp_path, text).constants] == constants


def test_a_constant_lists_the_names_its_statement_mentions_with_its_annotation_but_not_inside_a_string_value(tmp_path):
    found = parsed(tmp_path, "A: 'Box[Thing]' = make(other.part, 'Word')\n").constants
    assert list(found) == [Constant(1, "A", frozenset({"A", "Box", "Thing", "make", "other", "part"}))]


def test_a_function_lists_every_name_its_definition_mentions_its_signature_and_decorators_included(tmp_path):
    text = "@wrap(Mode)\ndef f(a: Kind, b: 'Box[Item]' = DEFAULT) -> Result:\n    return a.go(Helper, 'Word')\n"
    assert parsed(tmp_path, text).functions[0].named == frozenset(
        {"wrap", "Mode", "Kind", "Box", "Item", "DEFAULT", "Result", "a", "go", "Helper"})


@pytest.mark.parametrize("text, unmentioned", [
    pytest.param("from m import A, B\n__all__ = ['A']\nx: B\n", {(1, "A")},
                 id="a name listed only as text is not mentioned; one in an annotation is"),
    pytest.param("from m import A as C\nfrom n import D\nprint(C)\n", {(2, "D")},
                 id="an alias is mentioned by the name it binds; a name not mentioned at all is listed"),
    pytest.param("from m import A\ndef f(x: 'A'): pass\n", set(), id="a string annotation mentions its names"),
    pytest.param("import m\nfrom . import n\n", {(2, "n")}, id="an import of a whole module is not read"),
])
def test_a_file_lists_the_names_its_imports_take_that_nothing_else_in_it_mentions(tmp_path, text, unmentioned):
    assert parsed(tmp_path, text).unmentioned == frozenset(unmentioned)


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


def test_a_path_is_resolved_from_the_folder_given_with_its_links_followed(tmp_path):
    (tmp_path / "real").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "real")
    assert FsSourceTree(FileSystem()).resolved(tmp_path, Path("link")) == tmp_path / "real"


@pytest.mark.parametrize("text, imports", [
    pytest.param("import os.path\n", (Import(1, ("os", "path"), standard=True, written="os.path"),),
         id="a module imported as a whole, of the standard library"),
    pytest.param("from app.kernel import ids, Name\n", (Import(1, ("app", "kernel"), ("ids", "Name"), written="app.kernel"),),
         id="names imported from a module named from the top"),
    pytest.param("from . import doc\nfrom ..store import Repo\n",
         (Import(1, (), ("doc",), True, 0, written=".", unresolved=True),
          Import(2, ("store",), ("Repo",), True, 1, written="..store", unresolved=True)),
         id="a relative import climbs one folder fewer than its dots, and with no file it is not followed"),
    pytest.param("from app.kernel import *\n", (Import(1, ("app", "kernel"), ("*",), written="app.kernel", every=True),),
         id="a star import imports every public name"),
    pytest.param("from \\\n    app.kernel import (\n    ids,\n)\nimport app . platform\n",
         (Import(1, ("app", "kernel"), ("ids",), written="app.kernel", last=4),
          Import(5, ("app", "platform"), standard=False, written="app.platform")),
         id="an import over several lines says its last line"),
])
def test_the_imports_are_recorded_in_terms_no_language_owns(text, imports):
    assert FsSourceTree(FileSystem()).parsed(text, STANDARD, **HANDED).imports == imports


@pytest.mark.parametrize("standard, marked", [
    pytest.param(frozenset({"fs"}), [True, True, True, False],
                 id="an import whose first step is a module the reader is handed is of the standard library"),
    pytest.param(frozenset(), [False, False, False, False], id="handed none, no import is"),
])
def test_an_import_is_of_the_standard_library_by_the_modules_the_reader_is_handed(tmp_path, standard, marked):
    (tmp_path / "x.py").write_text("import fs\nimport fs.sub\nfrom fs.sub import x\nimport os\n")
    read = FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=standard, **HANDED)[0]
    assert [i.standard for i in read.imports] == marked


def test_a_relative_import_is_never_of_the_standard_library_whatever_the_reader_is_handed(tmp_path):
    (tmp_path / "fs.py").write_text("")
    (tmp_path / "x.py").write_text("from . import fs\nfrom .fs import x\n")
    read = FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=frozenset({"fs"}), **HANDED)[0]
    assert [i.standard for i in read.imports] == [False, False]


def test_a_text_in_no_file_marks_its_imports_as_a_file_does(tmp_path):
    text = "import fs\nfrom fs.sub import x\nimport os\nfrom .fs import y\n"
    (tmp_path / "x.py").write_text(text)
    tree = FsSourceTree(FileSystem())
    read = tree.read(tmp_path, [("x.py",)], standard=frozenset({"fs"}), **HANDED)[0]
    assert [i.standard for i in tree.parsed(text, frozenset({"fs"}), **HANDED).imports] == [i.standard for i in read.imports] == [
        True, True, False, False]


def test_handed_the_interpreter_s_standard_library_every_import_of_xarch_s_own_source_is_marked_by_its_first_step():
    root = Path(__file__).parents[4] / "xarch"
    tree = FsSourceTree(FileSystem())
    imports = [i for f in tree.read(root, tree.paths(root, (".py",)), standard=STANDARD, **HANDED) for i in f.imports
               if not i.relative]
    assert {i.standard for i in imports} == {True, False}
    assert [i for i in imports if i.standard != (i.module[0] in STANDARD)] == []


@pytest.mark.parametrize("text, error", [
    pytest.param("def f(:\n", Unparsable(1, "invalid syntax"), id="a syntax error is the parser's message at its line"),
    pytest.param("x = 1\n", None, id="a text that parses has none"),
    pytest.param("x = " + "1 + " * 200_000 + "1\n", Unparsable(0, "maximum recursion depth exceeded during ast construction"),
                 id="a text nested too deep for the parser is unparsable, not a crash"),
])
def test_a_text_in_no_file_is_parsed_as_a_file_is(text, error):
    assert FsSourceTree(FileSystem()).parsed(text, STANDARD, **HANDED).error == error


PIECES = (
    "import os\n"
    "\n"
    "LIMIT = 3\n"
    "\n"
    "@cache\n"
    "@other(1)\n"
    "def first(x):\n"
    "    return x\n"
    "\n"
    "class Shelf:\n"
    "    size = 2\n"
    "\n"
    "    def __init__(self):\n"
    "        self.items = []\n"
    "\n"
    "    @property\n"
    "    async def count(self):\n"
    "        def inner():\n"
    "            return 1\n"
    "        return inner()\n"
    "\n"
    "    class Nested:\n"
    "        def deep(self):\n"
    "            pass\n"
    "\n"
    "if os.name:\n"
    "    async def branch():\n"
    "        pass\n"
    "else:\n"
    "    class Other:\n"
    "        pass\n"
)


@pytest.mark.parametrize("text, pieces", [
    pytest.param(PIECES, (Piece("function", "first", 5, 8), Piece("class", "Shelf", 10, 24),
                          Piece("method", "__init__", 13, 14, "Shelf"), Piece("method", "count", 16, 20, "Shelf"),
                          Piece("function", "branch", 27, 28), Piece("class", "Other", 30, 31)),
                 id="top-level functions and classes and their methods, each spanning its decorators, nested ones not "
                    "pieces of their own"),
    pytest.param("X = 1\nimport os\n", (), id="a file with no function and no class has no piece"),
    pytest.param("try:\n    def a():\n        pass\nexcept ValueError:\n    def b():\n        pass\n",
                 (Piece("function", "a", 2, 3), Piece("function", "b", 5, 6)),
                 id="a function in a branch of a try at the top level is a piece"),
])
def test_the_pieces_of_a_file_are_its_top_level_functions_and_classes_and_their_methods(tmp_path, text, pieces):
    assert parsed(tmp_path, text).pieces == pieces


def test_a_text_in_no_file_has_its_pieces_too():
    assert FsSourceTree(FileSystem()).parsed("def f():\n    pass\n", STANDARD, **HANDED).pieces == (Piece("function", "f", 1, 2),)


@pytest.mark.parametrize("text, comments", [
    pytest.param("x = 1  # one\n    # two\n",
                 (Comment(1, "# one", 7, 12, marker="#"), Comment(2, "# two", 4, 9, marker="#")),
                 id="a comment after code and one on a line of its own, each where it lies on its line"),
    pytest.param("x = '# not one'  # one\n", (Comment(1, "# one", 17, 22, marker="#"),),
                 id="a # inside a string is no comment"),
    pytest.param('"""# no comment"""\ndef f():\n    """Nor # this."""\n', (),
                 id="a docstring is no comment, whatever it holds"),
    pytest.param("x = 1  # one\ry = 2  # two\r\nz = 3  # three\n",
                 (Comment(1, "# one", 7, 12, marker="#"), Comment(2, "# two", 7, 12, marker="#"),
                  Comment(3, "# three", 7, 14, marker="#")),
                 id="a line ended by a carriage return alone is a line of its own, as the parser counts it"),
])
def test_each_comment_is_read_with_where_it_lies(tmp_path, text, comments):
    assert parsed(tmp_path, text).comments == comments
    assert FsSourceTree(FileSystem()).parsed(text, STANDARD, **HANDED).comments == comments
    assert all(comment.marker == "#" and comment.doc is False for comment in parsed(tmp_path, text).comments)


PRIVACY = ("class A: ...\nclass _A: ...\nclass Kept:\n    def __init__(self): ...\n    def m(self): ...\n"
           "    def _m(self): ...\ndef f(): ...\ndef _f(): ...\nX = 1\n_X = 1\n__all__ = ['A']\n"
           "from m import a, _b\nfrom m import _c as c\nimport os\n")
"""A class, a function, a method, a constant and an import of each sort, public and not, special names among them."""


def flags(found: SourceFile) -> tuple:
    """Whether each class, function and constant is public, by its name, and what each import takes and withholds."""
    return ({c.name: c.public for c in found.classes}, {f.name: f.public for f in found.functions},
            {c.name: c.public for c in found.constants}, [(i.names, i.withheld) for i in found.imports])


def test_the_reader_says_a_name_is_public_unless_it_starts_with_the_private_prefix_it_is_handed(tmp_path):
    assert flags(parsed(tmp_path, PRIVACY)) == (
        {"A": True, "_A": False, "Kept": True},
        {"__init__": False, "m": True, "_m": False, "f": True, "_f": False},
        {"X": True, "_X": False, "__all__": False},
        [(("a", "_b"), frozenset({"_b"})), (("_c",), frozenset({"_c"})), (None, frozenset())])


def test_handed_no_prefix_the_reader_makes_every_name_public(tmp_path):
    (tmp_path / "x.py").write_text(PRIVACY)
    classes, functions, constants, imports = flags(
        FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=STANDARD, private="", special=SPECIAL)[0])
    assert {*classes.values(), *functions.values(), *constants.values()} == {True}
    assert [withheld for _, withheld in imports] == [frozenset(), frozenset(), frozenset()]


def test_a_text_in_no_file_is_told_public_as_a_file_is(tmp_path):
    assert flags(FsSourceTree(FileSystem()).parsed(PRIVACY, STANDARD, **HANDED)) == flags(
        parsed(tmp_path, PRIVACY))


def test_the_reader_must_be_handed_the_prefix(tmp_path):
    tree = FsSourceTree(FileSystem())
    with pytest.raises(TypeError):
        tree.read(tmp_path, [], standard=STANDARD)
    with pytest.raises(TypeError):
        tree.parsed("x = 1\n", STANDARD)


@pytest.mark.parametrize("text, record", [
    pytest.param("class P:\n    def __init__(self): ...\n    def __eq__(self, other): ...\n\ndef make() -> P: ...\n", True,
                 id="only special methods, returned by a top-level function"),
    pytest.param("class P:\n    x: int\n\ndef make() -> P: ...\n", True, id="no method at all, returned by a top-level function"),
    pytest.param("class P:\n    async def __aenter__(self): ...\n\nasync def make() -> P: ...\n", True,
                 id="an async special method, returned by an async top-level function"),
    pytest.param("class P:\n    pass\n\ndef find() -> P | None: ...\n", True, id="named inside a union"),
    pytest.param("class P:\n    pass\n\ndef every() -> list[P]: ...\n", True, id="named inside a subscript"),
    pytest.param("class P:\n    pass\n\ndef make() -> 'P': ...\n", True, id="named in a string annotation"),
    pytest.param("class P:\n    def size(self): ...\n\ndef make() -> P: ...\n", False, id="an ordinary method"),
    pytest.param("class P:\n    def __init__(self): ...\n\ndef make(): ...\n", False, id="returned by no function"),
    pytest.param("class P:\n    pass\n\nclass Q:\n    def make(self) -> P: ...\n", False,
                 id="returned by a method of another class only"),
    pytest.param("class P:\n    pass\n\ndef make(p: P) -> None: ...\n", False, id="named only in a parameter's annotation"),
])
def test_a_class_is_a_record_when_its_methods_are_all_special_and_a_top_level_function_returns_it(tmp_path, text, record):
    assert parsed(tmp_path, text).classes[0].record is record


def test_handed_no_special_pattern_only_a_class_with_no_method_can_be_a_record(tmp_path):
    (tmp_path / "x.py").write_text("class P:\n    def __init__(self): ...\n\nclass Q:\n    pass\n\ndef make() -> P | Q: ...\n")
    found = FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=STANDARD, private=PRIVATE, special="")[0]
    assert {c.name: c.record for c in found.classes} == {"P": False, "Q": True}


def test_a_text_in_no_file_is_told_its_records_as_a_file_is(tmp_path):
    text = "class P:\n    def __repr__(self): ...\n\nclass Q:\n    def size(self): ...\n\ndef make() -> P | Q: ...\n"
    found = FsSourceTree(FileSystem()).parsed(text, STANDARD, **HANDED)
    assert [c.record for c in found.classes] == [c.record for c in parsed(tmp_path, text).classes] == [True, False]


def test_the_reader_must_be_handed_the_pattern_of_a_special_name(tmp_path):
    tree = FsSourceTree(FileSystem())
    with pytest.raises(TypeError):
        tree.read(tmp_path, [], standard=STANDARD, private=PRIVATE)
    with pytest.raises(TypeError):
        tree.parsed("x = 1\n", STANDARD, private=PRIVATE)


LOOPED = '''from app.results import Gone, Go, Published

CASES = [
    ("a document is published", Go(1), Published),
    ("gone", Go(2), Gone),
]


def test_go(subtests):
    """Each case."""
    for name, when, then in CASES:
        assert run(when) == then
'''


def test_a_loop_of_a_test_s_own_body_over_a_list_of_the_file_is_its_table_run_by_that_loop(tmp_path):
    loop = line_of(LOOPED, "for name, when, then")
    assert parsed(tmp_path, LOOPED, (LOOP,)).functions[0].tables == (Table(loop, ("name", "when", "then"), (
        Row(line_of(LOOPED, "Go(1)"), True, "a document is published", (None, "Go", "Published")),
        Row(line_of(LOOPED, "Go(2)"), True, "gone", (None, "Go", "Gone"))), form=0, runs=loop),)


def looping(iterable: str = "CASES", head: str = "CASES = [('x', 1)]\n", signature: str = "subtests",
            body: str = "    for a, b in {iterable}:\n        assert a == b\n") -> str:
    """A file whose top level is head, then a test of that signature whose body is body, over the iterable."""
    return f"{head}\n\ndef test_a({signature}):\n{body.format(iterable=iterable)}"


@pytest.mark.parametrize("text", [
    pytest.param(looping(), id="a name assigned once at the top of the file"),
    pytest.param(looping("[('x', 1)]"), id="a list literal written in the loop"),
    pytest.param(looping("(('x', 1),)"), id="a tuple literal written in the loop"),
    pytest.param(looping(head="CASES: list = [('x', 1)]\n"), id="a name annotated and assigned once"),
])
def test_the_rows_of_a_loop_are_read_from_a_literal_or_the_name_of_a_module_level_one(tmp_path, text):
    rows = parsed(tmp_path, text, (LOOP,)).functions[0].tables[0].rows
    assert [(row.written, row.id, row.cells) for row in rows] == [(True, "x", (None, None))]


@pytest.mark.parametrize("text", [
    pytest.param(looping(head="CASES = [('x', 1)]\nCASES = [('y', 2)]\n"), id="a name assigned twice"),
    pytest.param(looping(head="CASES = load()\n"), id="a name assigned to a call"),
    pytest.param(looping(head="from app.cases import CASES\n"), id="an imported name"),
    pytest.param(looping("[*MORE]"), id="a list literal holding a starred value"),
    pytest.param(looping(head="CASES = [*MORE]\n"), id="a name assigned to a list holding a starred value"),
])
def test_a_loop_over_a_name_of_the_file_whose_rows_are_no_literal_holds_a_table_whose_rows_cannot_be_read(tmp_path,
                                                                                                        text):
    tables = parsed(tmp_path, text, (LOOP,)).functions[0].tables
    assert [(table.columns, table.rows, table.runs) for table in tables] == [(("a", "b"), None, line_of(text, "for a"))]


@pytest.mark.parametrize("text", [
    pytest.param(looping(body="    for i, (a, b) in enumerate(CASES):\n        assert a\n"), id="a nested target"),
    pytest.param(looping(body="    for a, (b, c) in CASES:\n        assert a\n"), id="a target holding a tuple"),
    pytest.param(looping(body="    for a, *b in CASES:\n        assert a\n"), id="a target holding a starred name"),
    pytest.param(looping(body="    for a.b in CASES:\n        assert a\n"), id="a target that is an attribute"),
    pytest.param(looping("range(3)"), id="a loop over a call"),
    pytest.param(looping("load()"), id="a loop over a call of the file's"),
    pytest.param(looping("result.items"), id="a loop over an attribute"),
    pytest.param(looping("CASES + MORE"), id="a loop over an expression"),
    pytest.param(looping("[x for x in CASES]"), id="a loop over a comprehension"),
    pytest.param(looping("cases", signature="cases"), id="a loop over a parameter"),
    pytest.param(looping("CASES", signature="CASES"), id="a loop over a parameter named as the file's list"),
    pytest.param(looping(body="    cases = [('x', 1)]\n    for a, b in cases:\n        assert a\n"),
                 id="a loop over a name the body assigns"),
    pytest.param(looping(body="    CASES = [('y', 2)]\n    for a, b in CASES:\n        assert a\n"),
                 id="a loop over a name the body rebinds"),
    pytest.param(looping("MISSING"), id="a loop over a name the file does not bind"),
    pytest.param(looping(body="    if True:\n        for a, b in CASES:\n            assert a\n"),
                 id="a loop nested in an if"),
    pytest.param(looping(body="    with x:\n        for a, b in CASES:\n            assert a\n"),
                 id="a loop nested in a with"),
    pytest.param(looping(body="    def inner():\n        for a, b in CASES:\n            assert a\n"),
                 id="a loop of a function nested in the test"),
    pytest.param(looping(body="    async for a, b in CASES:\n        assert a\n"), id="an async for"),
    pytest.param(looping(body="    assert CASES\n"), id="a body with no loop"),
    pytest.param(looping(body="    while CASES:\n        assert CASES\n"), id="a body with a while"),
    pytest.param(looping(body="    for x in range(3):\n        assert x\n    for a, b in CASES:\n        assert a\n"),
                 id="a first loop that holds no table, and a later one is not tried"),
])
def test_a_loop_that_binds_no_plain_names_or_runs_over_no_list_of_the_file_holds_no_table(tmp_path, text):
    assert parsed(tmp_path, text, (LOOP,)).functions[0].tables == ()


@pytest.mark.parametrize("body, columns", [
    pytest.param("    for a in CASES:\n        assert a\n", ("a",), id="one name"),
    pytest.param("    for a, b in CASES:\n        assert a\n", ("a", "b"), id="a tuple of names"),
    pytest.param("    for (a, b) in CASES:\n        assert a\n", ("a", "b"), id="a tuple of names in brackets"),
    pytest.param("    for [b, a] in CASES:\n        assert a\n", ("b", "a"), id="a list of names, in its order"),
])
def test_the_columns_of_a_loop_are_the_names_it_binds_in_order(tmp_path, body, columns):
    assert parsed(tmp_path, looping(body=body), (LOOP,)).functions[0].tables[0].columns == columns


@pytest.mark.parametrize("body", [
    pytest.param("    \"\"\"Each case.\"\"\"\n    x = 1\n    for a, b in CASES:\n        assert a\n",
                 id="a docstring and a statement before the loop"),
    pytest.param("    for a, b in CASES:\n        assert a\n    else:\n        assert CASES\n",
                 id="a loop with an else"),
    pytest.param("    for a, b in CASES:\n        for c in a:\n            assert c\n    for a, b in CASES:\n"
                 "        assert b\n", id="a second loop over the same list, nested and after"),
])
def test_the_first_loop_of_the_body_s_own_statements_is_the_table_and_only_it(tmp_path, body):
    text = looping(body=body)
    first = line_of(text, "for a, b in CASES")
    assert [(t.line, t.runs) for t in parsed(tmp_path, text, (LOOP,)).functions[0].tables] == [(first, first)]


@pytest.mark.parametrize("row, written, id, cells", [
    pytest.param("('an outcome', Go(1), Published)", True, "an outcome", (None, "Go", "Published"), id="a tuple"),
    pytest.param("['an outcome', Go(1), results.Published]", True, "an outcome", (None, "Go", "Published"),
                 id="a list"),
    pytest.param("(1, Go(1), Published)", True, None, (None, "Go", "Published"), id="a tuple whose first value is no text"),
    pytest.param("()", True, None, (), id="a tuple shorter than the id's position"),
    pytest.param("Published", False, None, (), id="a bare name"),
    pytest.param("case('an outcome', Go(1), Published)", False, None, (), id="a call"),
    pytest.param("{'id': 'an outcome'}", False, None, (), id="a dict"),
    pytest.param("(*BASE, Published)", False, None, (), id="a tuple holding a starred value"),
])
def test_a_literal_row_of_a_loop_is_written_when_it_is_a_tuple_or_list_its_id_the_text_at_the_position(
        tmp_path, row, written, id, cells):
    text = looping(head=f"CASES = [\n    {row},\n]\n", body="    for a, b, c in CASES:\n        assert a\n")
    assert parsed(tmp_path, text, (LOOP,)).functions[0].tables[0].rows == (Row(2, written, id, cells),)


def test_an_id_by_position_reads_the_text_at_that_position(tmp_path):
    text = looping(head="CASES = [(Go(1), 'an outcome', Published)]\n")
    second = replace(LOOP, id=RowId(position=1))
    assert [row.id for row in parsed(tmp_path, text, (second,)).functions[0].tables[0].rows] == ["an outcome"]


def test_a_call_row_of_a_loop_is_read_as_a_decorator_s_row_is(tmp_path):
    text = looping(head="from app.cases import case\n\nCASES = [\n    case('a', Go(1), Published, name='x'),\n"
                        "    ('b', Go(2), Gone),\n]\n", body="    for a, b, c in CASES:\n        assert a\n")
    assert parsed(tmp_path, text, (LOOP_CALL,)).functions[0].tables[0].rows == (
        Row(4, True, "x", (None, "Go", "Published")), Row(5, False, None, (None, "Go", "Gone")))


def test_a_call_row_of_a_loop_is_its_form_s_row_by_the_import_that_binds_it(tmp_path):
    text = looping(head="from other import case\n\nCASES = [case('a', name='x')]\n",
                   body="    for a in CASES:\n        assert a\n")
    assert [row.written for row in parsed(tmp_path, text, (LOOP_CALL,)).functions[0].tables[0].rows] == [False]


MIXED = '''import pytest

CASES = [("a", 1)]


@pytest.mark.parametrize("x", [pytest.param(1, id="one")])
def test_a(x):
    for a, b in CASES:
        assert a == x
'''


def test_a_function_holds_its_decorator_s_tables_first_then_its_loop_s_each_by_its_own_form(tmp_path):
    tables = parsed(tmp_path, MIXED, (PYTEST, LOOP)).functions[0].tables
    assert [(t.form, t.line, t.runs) for t in tables] == [
        (0, line_of(MIXED, "@pytest"), 0), (1, line_of(MIXED, "for a, b"), line_of(MIXED, "for a, b"))]


@pytest.mark.parametrize("forms, index", [
    pytest.param((LOOP, LOOP_CALL), 0, id="the first of two loop forms"),
    pytest.param((replace(LOOP, columns_from="fields", id=RowId(field="name")), LOOP), 1,
                 id="a loop form the reader cannot read, written first, is skipped"),
    pytest.param((PYTEST, LOOP), 1, id="a decorator form before it"),
])
def test_a_loop_is_read_by_the_first_loop_form_the_reader_reads_and_tagged_with_its_index(tmp_path, forms, index):
    assert [t.form for t in parsed(tmp_path, looping(), forms).functions[0].tables] == [index]


def test_a_method_s_loop_is_read_too(tmp_path):
    text = "CASES = [('x', 1)]\n\nclass TestA:\n    def test_a(self):\n        for a, b in CASES:\n            assert a\n"
    assert [(f.name, len(f.tables)) for f in parsed(tmp_path, text, (LOOP,)).functions] == [("test_a", 1)]


TESTS = """def test_a():
    assert True


def helper():
    pass


class TestB:
    def test_b(self):
        pass
"""
"""A test file of a function, a helper and a method of a class, by the names pytest would take for tests."""
SKIPPED = "def test_a():\n    it.skip()\n"
"""A test calling a method of a name the file does not bind."""


def declared_in(tmp_path: Path, text: str, declared: tuple[DeclaredForm, ...] = (),
                bound: tuple[tuple[str, ...], ...] = ()) -> SourceFile:
    """The text read as a test file is, handed the forms that declare a test and the framework's globals."""
    (tmp_path / "x.py").write_text(text)
    return FsSourceTree(FileSystem()).read(tmp_path, [("x.py",)], standard=STANDARD, declared=declared, globals=bound,
                                           **HANDED)[0]


def test_a_function_or_a_method_whose_name_matches_a_function_form_is_a_test_whose_body_is_that_function(tmp_path):
    found = declared_in(tmp_path, TESTS, (DeclaredForm(function="test_*"),))
    assert [function.name for function in found.functions] == ["test_a", "helper", "test_b"]
    assert found.tests == (DeclaredTest(1, "test_a", 0, False, found.functions[0]),
                           DeclaredTest(10, "test_b", 0, False, found.functions[2]))
    assert found.tests[0].body is found.functions[0] and found.tests[1].body is found.functions[2]


def test_a_function_is_a_test_of_the_first_form_it_matches_once_and_a_call_form_declares_none_this_reader_reads(
        tmp_path):
    call = DeclaredForm(call=(("it",),), title=Place(0), body=Place(1))
    found = declared_in(tmp_path, "def test_a():\n    pass\n\n\ndef testb():\n    pass\n",
                        (call, DeclaredForm(function="test_*"), DeclaredForm(function="test*")))
    assert [(test.name, test.form, test.titled) for test in found.tests] == [("test_a", 1, False), ("testb", 2, False)]


def test_a_file_read_with_no_form_holds_no_test(tmp_path):
    assert declared_in(tmp_path, TESTS).tests == ()


def test_a_name_the_file_does_not_bind_that_a_global_starts_is_read_as_that_global_in_a_call_and_a_use(tmp_path):
    found = declared_in(tmp_path, SKIPPED, bound=(("it",),))
    assert (found.calls, found.method_calls) == ((Call(2, ("it", "skip")),), ())
    assert Use(2, ("it", "skip"), 0) in found.uses


def test_with_no_globals_a_bare_name_the_file_does_not_bind_is_read_as_before(tmp_path):
    found = declared_in(tmp_path, SKIPPED)
    assert (found.calls, found.uses, found.method_calls) == ((), (), (MethodCall(2, "skip", False),))


def test_a_name_the_file_binds_keeps_its_own_binding_over_a_global(tmp_path):
    imported = declared_in(tmp_path, "from x import it\n\n\ndef test_a():\n    it.skip()\n", bound=(("it",),))
    assert imported.calls == (Call(5, ("x", "it", "skip")),)
    local = declared_in(tmp_path, "def test_a():\n    it = make()\n    it.skip()\n", bound=(("it",),))
    assert (local.calls, local.method_calls) == ((), (MethodCall(3, "skip", False),))


def test_a_global_named_as_a_builtin_is_read_as_the_global(tmp_path):
    found = declared_in(tmp_path, "def test_a():\n    print(1)\n", bound=(("print",),))
    assert found.calls == (Call(2, ("print",), (None,)),)
    assert [use.name for use in found.uses] == [("print",)]


def test_a_file_with_a_star_import_reads_no_global(tmp_path):
    found = declared_in(tmp_path, "from x import *\n\n\ndef test_a():\n    it.skip()\n", bound=(("it",),))
    assert (found.calls, found.method_calls) == ((), (MethodCall(5, "skip", False),))
