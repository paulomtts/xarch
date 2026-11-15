"""The values the source rules reason about: the profile as the checker sees it, and already-parsed source files."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.logic.placement import Target


@dataclass(frozen=True)
class TestTier:
    """A kind of test as the checker sees it.

    subject holds the parts it tests, each as a target: a part inside the modules in the test's own module. folder is
    the folder of its example test below the tests root, which places the tests of a tier whose folder mirrors no part.
    types_only holds the parts its tests may use as types but never call.
    """
    name: str
    subject: tuple[Target, ...]
    folder: tuple[str, ...] | None = None
    types_only: tuple[str, ...] = ()


@dataclass(frozen=True)
class Fakes:
    """Where the test fakes live below the tests root, the parts they stand in for, and how a fake's name starts."""
    path: tuple[str, ...]
    stand_in_for: tuple[str, ...]
    prefix: str = ""


@dataclass(frozen=True)
class Scenarios:
    """The scenario-coverage guard: the part holding the result unions, the tier holding their tables, how a union's
    name ends, and the names of the three columns of a table: the state, the command and the result, in that order."""
    results: str
    tier: str
    suffix: str
    columns: tuple[str, str, str]


@dataclass(frozen=True)
class Profile:
    """The architecture in force, in the checker's terms.

    parts maps each part to its path pattern, and rules to what it may import. folders holds every folder of the
    layout as a pattern: those no part claims are structure, the package files that hold the tree together. libraries
    is None when outside packages are not checked. each_root is the folder holding the instances of the layout's
    `each` folder. package_only, scenarios, no_comments, stand_ins and closed_tree are the guards switched on.
    """
    parts: dict[str, tuple[str, ...]]
    rules: dict[str, tuple[Target, ...]]
    folders: tuple[tuple[str, ...], ...] = ()
    tiers: tuple[TestTier, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    fakes: Fakes | None = None
    each_root: tuple[str, ...] | None = None
    package_only: tuple[str, ...] = ()
    scenarios: Scenarios | None = None
    no_comments: bool = False
    stand_ins: bool = False
    closed_tree: bool = False


@dataclass(frozen=True)
class Import:
    """One imported name as written. names is None for `import a.b`, the imported names for `from a import x`."""
    line: int
    module: tuple[str, ...]
    level: int = 0
    names: tuple[str, ...] | None = None


@dataclass(frozen=True)
class Comment:
    """A `#` comment as written, and the line it is on."""
    line: int
    text: str


@dataclass(frozen=True)
class Union:
    """A module-level `Name = A | B | ...` of plain names, and the line it is on."""
    line: int
    name: str
    members: tuple[str, ...]


Ref = tuple[str, ...] | None
"""A name as the dotted path its absolute import binds, e.g. ("unittest", "mock", "Mock") for `Mock` after `from
unittest.mock import Mock`, or `mock.Mock` after `from unittest import mock`; None for anything else: a literal, an
expression, or a name bound some other way (a parameter, an assignment, a relative import) in the scope it is read."""


@dataclass(frozen=True)
class Call:
    """A call whose callee is a Ref, and the line it is on: its positional arguments and its keyword arguments as
    (name, value), each value a Ref; unpacked is whether it also passes *args or **kwargs."""
    line: int
    func: tuple[str, ...]
    args: tuple[Ref, ...] = ()
    keywords: tuple[tuple[str, Ref], ...] = ()
    unpacked: bool = False


@dataclass(frozen=True)
class Method:
    """A function defined in a class body: its name and its return annotation as written (a string annotation by its
    text), None when it has none."""
    line: int
    name: str
    returns: str | None


@dataclass(frozen=True)
class Class:
    """A module-level class: its bases, each a Ref (`Protocol[T]` names Protocol), and the methods of its body."""
    line: int
    name: str
    bases: tuple[Ref, ...] = ()
    methods: tuple[Method, ...] = ()


@dataclass(frozen=True)
class Row:
    """One element of the rows of a table, and the line it is on. param is whether it is a `pytest.param(...)` call
    (a bare tuple or anything else is not); id is its `id=` when that is a non-empty string literal, else None; cells
    holds the name that heads each positional value (the callee of a call, a bare name, the last name of an
    attribute), None where a value has none."""
    line: int
    param: bool
    id: str | None
    cells: tuple[str | None, ...]


@dataclass(frozen=True)
class Table:
    """One `pytest.mark.parametrize` of a test function, and the line it is on: its parameter names, and its rows
    (None when the rows are neither a list or tuple literal nor the name of one assigned at the top of the file)."""
    line: int
    columns: tuple[str, ...]
    rows: tuple[Row, ...] | None


@dataclass(frozen=True)
class Function:
    """A function at module level or in a class: its tables, every name its body uses (`mentions`), and each
    `if`, `match`, `try`, `for` or `while` statement of its body as (line, keyword)."""
    line: int
    name: str
    tables: tuple[Table, ...] = ()
    mentions: frozenset[str] = frozenset()
    branches: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True)
class SourceFile:
    """A Python file as parsed, never run: how it is shown (e.g. "app/kernel/x.py"), its path below the root, what
    it imports, its comments, its functions (at module level and in its classes), its unions, its calls and its
    classes. error is how it fails to parse, as (line, message), and then it
    holds nothing else."""
    name: str
    path: tuple[str, ...]
    imports: tuple[Import, ...]
    comments: tuple[Comment, ...] = ()
    functions: tuple[Function, ...] = ()
    unions: tuple[Union, ...] = ()
    error: tuple[int, str] | None = None
    calls: tuple[Call, ...] = ()
    classes: tuple[Class, ...] = ()
