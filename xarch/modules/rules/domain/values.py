"""The values the source rules reason about: the profile as the checker sees it, and already-parsed source files."""
from __future__ import annotations

from dataclasses import dataclass, field

from xarch.kernel.logic.placement import Target

NAME = "{name}"
"""Stands, in the file name the scenario-coverage guard expects, for the use case's name in snake_case."""


@dataclass(frozen=True)
class TestTier:
    """A kind of test as the checker sees it.

    subject holds the parts it tests, each as a target: a part inside the modules in the test's own module. folder is
    the folder below the tests root that places the tests of a tier whose tests mirror no part; an empty folder
    places nothing. types_only holds the parts its tests may use as types but never call. forbidden: its tests are held to the
    forbidden list of the part they mirror. proves, may_touch, litmus and one_file_per are the profile's words for the
    tier, which `where` shows.
    """
    name: str
    subject: tuple[Target, ...]
    folder: tuple[str, ...] | None = None
    types_only: tuple[str, ...] = ()
    forbidden: bool = False
    proves: str = ""
    may_touch: str = ""
    litmus: str = ""
    one_file_per: str = ""


@dataclass(frozen=True)
class Fakes:
    """Where the test fakes live below the tests root, the parts they stand in for, and how a fake's name starts."""
    path: tuple[str, ...]
    stand_in_for: tuple[str, ...]
    prefix: str = ""


@dataclass(frozen=True)
class Framework:
    """How the test framework names things: the patterns of a test file's name (against the file name alone, `*` for
    any text) and of a test function's, and the dotted names of what skips a test or expects it to fail."""
    files: tuple[str, ...]
    functions: str
    skips: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class TableForm:
    """How a test function holds a table: the dotted names of its decorator and of its row (each a Ref), the keyword
    that gives a row its id, and (None: positional only) the keywords its two arguments, the parameter names and the
    rows, may be given by."""
    decorator: tuple[str, ...]
    row: tuple[str, ...]
    id: str
    keywords: tuple[str, str] | None = None


@dataclass(frozen=True)
class Scenarios:
    """The scenario-coverage guard: the part holding the result unions, the tier holding their tables, how a union's
    name ends, the names of the three columns of a table (the state, the command and the result, in that order),
    how a table is written, and the name of a use case's test file, `{name}` standing for the use case in
    snake_case."""
    results: str
    tier: str
    suffix: str
    columns: tuple[str, str, str]
    table: TableForm
    file: str


@dataclass(frozen=True)
class Fixture:
    """A test function's parameter that hands over a mock builder: its name, and the names of its methods that build
    a mock and of those that build one from a spec given as an argument."""
    name: str
    mocks: tuple[str, ...]
    autospec: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandIns:
    """The stand-ins guard: the dotted names of the calls that build a mock, of those that build one from a spec given
    as an argument, and the keywords a mock is given its spec by (the first is the one the latter take); and the
    fixtures: parameters whose methods build mocks the same way."""
    mocks: tuple[tuple[str, ...], ...]
    autospec: tuple[tuple[str, ...], ...]
    spec: tuple[str, ...]
    fixtures: tuple[Fixture, ...] = ()


@dataclass(frozen=True)
class Exclusion:
    """A folder below the app that is not its source: its path below the app folder, and why."""
    path: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class PartInfo:
    """What the profile says of a part in words: its role and litmus test, its name as the docs show it (a path below
    the instance for an instance's part, ending in `/` for a folder) and, for a part no tier tests, why."""
    role: str = ""
    litmus: str = ""
    shown: str = ""
    untested: str = ""


@dataclass(frozen=True)
class Profile:
    """The architecture in force, in the checker's terms.

    parts maps each part to its path pattern, and rules to what it may import. folders holds every folder of the
    layout as a pattern: those no part claims are structure, the package files that hold the tree together. libraries
    is None when outside packages are not checked. each_root is the folder holding the instances of the layout's
    `each` folder. framework names the test files and functions; None: no file is a test. package_only, scenarios,
    no_comments, stand_ins and closed_tree are the guards switched on (None or False: off). forbidden holds, by part,
    the dotted names and modules a part may not use. info says each part in words, and singular names one instance
    of the `each` folder, for `where`. excluded holds the folders below the app that are not its source: no check reads
    a file below one.
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
    stand_ins: StandIns | None = None
    closed_tree: bool = False
    framework: Framework | None = None
    forbidden: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
    info: dict[str, PartInfo] = field(default_factory=dict)
    singular: str = ""
    excluded: tuple[Exclusion, ...] = ()


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
"""A name as the dotted path its absolute import binds, e.g. ("pkg", "sub", "Name") for `Name` after `from pkg.sub
import Name`, or `sub.Name` after `from pkg import sub`; None for anything else: a literal, an expression, or a name
bound some other way (a parameter, an assignment, a relative import) in the scope it is read."""


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
class ParameterCall:
    """A call of a method of a function's parameter, `<parameter>.<method>(...)`, and the line it is on: the names of
    the parameter and of the method, and the arguments as a Call holds them. Only a parameter its function's
    signature alone binds is read: one the body rebinds, or that is no function's parameter, is not."""
    line: int
    parameter: str
    method: str
    args: tuple[Ref, ...] = ()
    keywords: tuple[tuple[str, Ref], ...] = ()
    unpacked: bool = False


@dataclass(frozen=True)
class Use:
    """A name read where it is used, called or not, as the dotted path it reaches, and the line it is on: `dt.now`
    after `from datetime import datetime as dt` is ("datetime", "datetime", "now"). bound is how many steps of the
    path the import that binds its first name bound (2 here: `from datetime import datetime`); a builtin used by its
    bare name is ("builtins", <name>), bound 0."""
    line: int
    name: tuple[str, ...]
    bound: int


@dataclass(frozen=True)
class Method:
    """A function defined in a class body: its name and its return annotation as written (a string annotation by its
    text), None when it has none."""
    line: int
    name: str
    returns: str | None


@dataclass(frozen=True)
class Class:
    """A module-level class: its bases, each a Ref (`Protocol[T]` names Protocol), the methods of its body, and its
    attributes: the names its body assigns, and those its methods assign on their first parameter (`self.x = ...`)."""
    line: int
    name: str
    bases: tuple[Ref, ...] = ()
    methods: tuple[Method, ...] = ()
    attributes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Row:
    """One element of the rows of a table, and the line it is on. param is whether it is a call of the table's row
    (a bare tuple or anything else is not); id is its id keyword when that is a non-empty string literal, else None; cells
    holds the name that heads each positional value (the callee of a call, a bare name, the last name of an
    attribute), None where a value has none."""
    line: int
    param: bool
    id: str | None
    cells: tuple[str | None, ...]


@dataclass(frozen=True)
class Table:
    """One table decorating a test function (the decorator the profile names), and the line it is on: its parameter names, and its rows
    (None when the rows are neither a list or tuple literal nor the name of one assigned at the top of the file)."""
    line: int
    columns: tuple[str, ...]
    rows: tuple[Row, ...] | None


@dataclass(frozen=True)
class Function:
    """A function at module level or in a class: its tables, every name its body uses (`mentions`), and each
    `if`, `match`, `try`, `for` or `while` statement of its body as (line, keyword); asserts: its body holds an
    `assert` statement."""
    line: int
    name: str
    tables: tuple[Table, ...] = ()
    mentions: frozenset[str] = frozenset()
    branches: tuple[tuple[int, str], ...] = ()
    asserts: bool = False


@dataclass(frozen=True)
class SourceFile:
    """A Python file as parsed, never run: how it is shown (e.g. "app/kernel/x.py"), its path below the root, what
    it imports, its comments, its functions (at module level and in its classes), its unions, its calls, its
    classes, the calls of the methods of its functions' parameters, the uses of the names it reads and the names it
    defines at module level as functions, in order (module_functions: a name that one `def` binds and nothing else
    binds, so that what it names is a function). error is how it fails to parse, as (line, message), and then it
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
    uses: tuple[Use, ...] = ()
    parameter_calls: tuple[ParameterCall, ...] = ()
    module_functions: tuple[str, ...] = ()


@dataclass(frozen=True)
class InitFile:
    """A file `init` writes beside the app folder: its path below the folder holding the app, the text `init` would
    write now, and whether it is pinned: the project keeps it as written."""
    path: tuple[str, ...]
    text: str
    pinned: bool = False


@dataclass(frozen=True)
class Loosened:
    """One way the profile in force is looser than the bundled profile it is compared with (see the spec contract's
    Loosened for the keys); sentence says it."""
    key: str
    part: str
    what: str = ""

    @property
    def sentence(self) -> str:
        match self.key:
            case "rules":
                return f"{self.part} may also import {self.what}"
            case "libraries" if not self.part:
                return "outside packages are not checked"
            case "libraries":
                return f"{self.part} may also import {self.what}"
            case "forbidden":
                return f"{self.part} no longer forbids {self.what}"
            case "untested":
                return f"{self.part} is newly marked untested"
            case "types_only":
                return f"the {self.part} tests may now call {self.what}"
            case "tier_forbidden":
                return f"the {self.part} tests are no longer held to their part's forbidden list"
            case "skips":
                return f"{self.what} is no longer counted as a skip"
            case "pinned":
                return f"{self.what} is no longer pinned"
        return " ".join(filter(None, (self.key, self.part, self.what)))


@dataclass(frozen=True)
class Origin:
    """Where the profile in force comes from: location as selected (a bundled name or a path), whether it is bundled,
    the bundled profile a custom one is compared with (None: it is bundled, or resembles none), the guards it leaves
    off, those of them the bundled profile it is or is compared with leaves off too (baseline_off), and how it is
    looser than that one."""
    location: str = ""
    bundled: bool = True
    closest: str | None = None
    guards_off: tuple[str, ...] = ()
    baseline_off: tuple[str, ...] = ()
    looser: tuple[Loosened, ...] = ()


@dataclass(frozen=True)
class Drift:
    """An init file as it stands: missing, or changed from what `init` would write (pinned files only). file is its
    path below the folder holding the app, as posix."""
    file: str
    state: str


@dataclass(frozen=True)
class At:
    """A place in a file: how the file is shown and the line."""
    file: str
    line: int


@dataclass(frozen=True)
class Weak:
    """A check satisfied to the letter only, which is not a violation: the guard it concerns, where, and why."""
    rule: str
    file: str
    line: int
    message: str


@dataclass(frozen=True)
class Finding:
    """An enforcement finding that `--strict` fails on: the key of the enforcement section it is under, and what."""
    key: str
    detail: str


@dataclass(frozen=True)
class Excluded:
    """A folder the profile leaves out of every check, as it is shown (such as "app/examples"), and why."""
    folder: str
    reason: str


@dataclass(frozen=True)
class Enforcement:
    """The state of the check's own enforcement, beside its violations: where the profile comes from and how loose
    it is; the app's Python files no part and no folder of the layout governs (never read, so never checked), as
    shown; the init files missing or changed; the tests skipped or expected to fail, and the dynamic imports, where
    they are; the checks satisfied to the letter only; and strict, the findings `--strict` fails on; and the folders
    the profile excludes, which no check reads."""
    origin: Origin = Origin()
    ungoverned: tuple[str, ...] = ()
    init_files: tuple[Drift, ...] = ()
    skipped: tuple[At, ...] = ()
    dynamic: tuple[At, ...] = ()
    weak: tuple[Weak, ...] = ()
    strict: tuple[Finding, ...] = ()
    excluded: tuple[Excluded, ...] = ()


@dataclass(frozen=True)
class Reach:
    """One thing a place may import: a part, in which scope (own, any, none), the part as the docs name it, and the
    folder it is at below the project root (a placeholder for an instance that is not fixed, such as <module>)."""
    part: str
    scope: str
    folder: str
    path: str


@dataclass(frozen=True)
class Nearest:
    """A part near a place no part claims: the part, as the docs name it, and its folder below the project root."""
    part: str
    folder: str
    path: str


@dataclass(frozen=True)
class TierInfo:
    """A kind of test as `where` tells it: the profile's words for what it proves, may touch and its litmus test."""
    name: str
    proves: str = ""
    may_touch: str = ""
    litmus: str = ""


@dataclass(frozen=True)
class Where:
    """What a place is and what code there may do, the answer of `xarch where`.

    kind: part (code in a part), structure (a folder of the layout no part claims), ungoverned (in no part and no
    folder of the layout, or outside the app and its tests), test (a test file, or the folder of one), fake (a test
    fake) or support (a file below the tests root that is no test, such as a helper)
    path: below the folder holding the app; exists: whether it is there now
    part, role, litmus, folder, instance: the part claiming it (for a test, the part it mirrors), its role and litmus
    test, its name as the docs show it, and the instance of the `each` folder it is in; singular names one instance
    may_import, may_import_text: the folders its code may import, and the same in the docs' words; libraries: the
    outside packages it may import (None: not checked); forbidden: the names it may not use
    tier, untested, test_folder, test_file: the kind of test that tests it (or why none does), and where its test
    file would live; test_file is a name pattern when the file is not its own (one file per use case)
    nearest: for a place in no part, the parts around it; closed_tree: whether a file there is a violation
    may_use_fakes, fakes_path, types_only, test_code_from: for a test, whether it may import the fakes and where
    they live, the parts it may use as types only, and the one folder it may import test code from
    note: one line of explanation where the kind alone does not say it
    """
    kind: str
    path: str
    exists: bool
    part: str = ""
    role: str = ""
    litmus: str = ""
    folder: str = ""
    instance: str = ""
    singular: str = ""
    may_import: tuple[Reach, ...] = ()
    may_import_text: str = ""
    libraries: tuple[str, ...] | None = None
    forbidden: tuple[str, ...] = ()
    tier: TierInfo | None = None
    untested: str = ""
    test_folder: str = ""
    test_file: str = ""
    nearest: tuple[Nearest, ...] = ()
    closed_tree: bool = False
    may_use_fakes: bool = False
    fakes_path: str = ""
    types_only: tuple[str, ...] = ()
    test_code_from: str = ""
    note: str = ""
