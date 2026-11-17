"""The values the source rules reason about: the profile as the checker sees it, and already-parsed source files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from xarch.kernel.logic.placement import repeat_of
from xarch.kernel.placement import Place
from xarch.kernel.source import CommentSpan, Import, Unparsable
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.published import At, Drift, KnownName, Loosened, Piece, Translation, Weak
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.checks import Condition, Scope, WrittenCheck
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns
from xarch.profile_values.tiers import CheckedTier

if TYPE_CHECKING:
    from xarch.modules.rules.domain.rule import OwnCheck


@dataclass(frozen=True)
class PartInfo:
    """What the profile says of a part in words: its role and litmus test, its name as the docs show it (a path below
    the instance for an instance's part, ending in `/` for a folder) and, for a part no tier tests, why."""
    role: str = ""
    litmus: str = ""
    shown: str = ""
    untested: str = ""


@dataclass(frozen=True)
class Asked:
    """An eval of the profile's own, as rules reads it: the kind of fact one question is asked of, the files it is
    asked in, the filters a fact must pass, in the words of the vocabulary, and its examples, the files of a small
    project it must read as flagged and of one it must read as clean, each by its path below the app with its code."""
    reads: str
    within: Scope
    keep: tuple[Condition, ...] = ()
    flagged: tuple[tuple[str, str], ...] = ()
    clean: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Profile:
    """The architecture in force, in the checker's terms.

    parts maps each part to its path pattern, and rules to what it may import. folders holds every folder of the
    layout as a pattern: those no part claims are structure, the package files that hold the tree together. libraries
    is None when outside packages are not checked. repeats are the repeating folders of the layout, each its word and
    the folder holding its instances. framework names the test files and functions; None: no file is a test.
    package_only, scenarios, no_comments, stand_ins and closed_tree are the guards switched on (None or False: off).
    forbidden holds, by part, the dotted names and modules a part may not use, and the methods it may not call on
    anything, each as ("", "<name>()"). info says each part in words. excluded
    holds the folders below the app that are not its source: no check reads a file below one. must_import holds, by
    part, the targets each of its files must import one of (or an outside package); no_duplicates is the fewest
    statements a function needs to count as a duplicate (None: off); no_twins the fewest fields a class needs to count
    as a twin of another (None: off), no_twins_renamed the fewest a renamed copy needs, no_twins_subset the fewest a copy
    of part of another's fields needs (None: that case is off; see twins), no_twins_translated the parts whose files
    translate one of a pair into the other, which is then no twin; dead_code switches the unused ports and fakes
    check on; pass_through lists the parts whose methods that only forward are listed (empty: off). untested lists,
    with dead_code, the files of a tiered part no test of its tier reaches; tests_only, with dead_code, the public names
    of the app no other file of the app names, but those tests_only_known accepts, each `<file below the app>:<name>`.
    holds says, by part, what its files define
    ("classes" or "functions"); immutable the parts every class of which, but an exception, is an immutable record;
    types_only, by part, the parts it may use as types only; no_callbacks the parts whose
    code calls none of its own parameters; names, by part, the patterns its public classes match one of; built_by, by
    part, the parts that alone may build its classes; shared, by part, the fewest users each public name of a part
    declared shared must have (see shared); private_imports switches the private-imports guard on. hints
    holds the profile's own advice, by rule id. language is the language of the app. reserved holds the
    standard-library modules (by top-level name, each with why) a part imports only when its libraries list them.
    approximate holds the keys whose check reads a fact the language supplies only partly. written are the checks the
    profile writes itself, by id, as spec read them; checks are those checks made into rules, in the profile's order
    (none until they are made, see own_checks). default_tests is the folder the tests go in, from the folder holding
    the app, when no tests folder is given or there: not a value a profile sets, but the convention spec publishes, the
    same for every profile; it is also the first step of the path of an example's test file. asked are the evals the
    profile writes itself, by id, as rules reads them (see Asked), which no check runs.
    """
    parts: dict[str, tuple[str, ...]]
    rules: dict[str, tuple[Target, ...]]
    folders: tuple[tuple[str, ...], ...] = ()
    tiers: tuple[CheckedTier, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    fakes: Fakes | None = None
    repeats: tuple[Repeat, ...] = ()
    package_only: tuple[str, ...] = ()
    scenarios: ScenarioCoverage | None = None
    no_comments: bool = False
    stand_ins: StandIns | None = None
    closed_tree: bool = False
    framework: Framework | None = None
    forbidden: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
    info: dict[str, PartInfo] = field(default_factory=dict)
    excluded: tuple[Excluded, ...] = ()
    must_import: dict[str, tuple[Target, ...]] = field(default_factory=dict)
    no_duplicates: int | None = None
    no_twins: int | None = None
    no_twins_renamed: int | None = None
    no_twins_subset: int | None = None
    no_twins_translated: tuple[str, ...] = ()
    dead_code: bool = False
    pass_through: tuple[str, ...] = ()
    untested: bool = False
    tests_only: bool = False
    tests_only_known: tuple[str, ...] = ()
    holds: dict[str, str] = field(default_factory=dict)
    immutable: tuple[str, ...] = ()
    types_only: dict[str, tuple[str, ...]] = field(default_factory=dict)
    no_callbacks: tuple[str, ...] = ()
    names: dict[str, tuple[str, ...]] = field(default_factory=dict)
    built_by: dict[str, tuple[str, ...]] = field(default_factory=dict)
    shared: dict[str, int] = field(default_factory=dict)
    private_imports: bool = False
    hints: dict[str, str] = field(default_factory=dict)
    language: CheckedLanguage = CheckedLanguage()
    reserved: dict[str, str] = field(default_factory=dict)
    approximate: tuple[Shortfall, ...] = ()
    written: dict[str, WrittenCheck] = field(default_factory=dict)
    checks: tuple[OwnCheck, ...] = ()
    default_tests: str = ""
    asked: dict[str, Asked] = field(default_factory=dict)

    def words(self) -> dict[str, str]:
        """The word of the repeating folder each part lies in; a part outside every one has none."""
        return {name: repeat.word for name, pattern in self.parts.items()
                if (repeat := repeat_of(self.repeats, pattern)) is not None}


@dataclass(frozen=True)
class Comment:
    """A line comment as written, its marker included, and the line it is on; and where it lies there: from column
    column to column end of line last (0: its own line), columns counted in characters from 0, end past its last
    character."""
    line: int
    text: str
    column: int = 0
    end: int = 0
    last: int = 0

    @property
    def span(self) -> CommentSpan:
        """Where it lies, in the words of a module that reads the source as text."""
        return CommentSpan(self.line, self.column, self.end, self.last)


@dataclass(frozen=True)
class Union:
    """A module-level name bound to one plain name or to plain names joined as alternatives (`Name = A | B | ...`),
    and the line it is on."""
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
class Callback:
    """A call of a function's own parameter by its bare name, `<parameter>(...)`, and the line it is on: the name of
    the function whose parameter it is ("<lambda>" for a lambda), and of the parameter; receiver is whether the
    parameter is the first one of a method, the object or class it is called on; annotated whether its annotation
    says it is a callable. Only a parameter its function's signature alone binds is read, as for a ParameterCall."""
    line: int
    function: str
    parameter: str
    receiver: bool = False
    annotated: bool = False


@dataclass(frozen=True)
class Use:
    """A name read where it is used, called or not, as the dotted path it reaches, and the line it is on: `dt.now`
    after `from datetime import datetime as dt` is ("datetime", "datetime", "now"). bound is how many steps of the
    path the import that binds its first name bound (2 here: `from datetime import datetime`); a builtin used by its
    bare name is (<its namespace>, <name>), bound 0."""
    line: int
    name: tuple[str, ...]
    bound: int


@dataclass(frozen=True)
class MethodCall:
    """A call of a name read as an attribute of an expression, `<expr>.<name>(...)`, whose callee no import binds (a
    callee an import binds, such as `Path.cwd()` after `from pathlib import Path`, is a Call), and the line it is on:
    the attribute's name, and held: whether the expression is the object a method is called on (its first parameter,
    not a staticmethod's) or a chain of attributes on it, `self.name()` or `self.repo.name()`, as in a function nested
    in that method too."""
    line: int
    name: str
    held: bool = False


@dataclass(frozen=True)
class Method:
    """A function defined in a class body: its name and its return annotation as written (a string annotation by its
    text), None when it has none."""
    line: int
    name: str
    returns: str | None


@dataclass(frozen=True)
class Class:
    """A module-level class: its bases, each a Ref (a generic interface names the interface alone), the methods of its body, and its
    attributes: the names its body assigns, and those its methods assign on their first parameter (`self.x = ...`);
    named: every name its bases and body mention, by its last step alone; exception: it derives from one of the language's
    builtin exceptions, named by its bare name, directly or through a class defined before it in the same file;
    fields: the names a statement of its body itself declares with an annotation (`x: int`, with a default or not), in
    order, those annotated as a class variable left out; types: the annotation of each of its fields, in the same order,
    as written (a string annotation by its text); immutable: it is an immutable record, as the reader was told one is
    marked (see RecordMark)."""
    line: int
    name: str
    bases: tuple[Ref, ...] = ()
    methods: tuple[Method, ...] = ()
    attributes: tuple[str, ...] = ()
    named: frozenset[str] = frozenset()
    exception: bool = False
    fields: tuple[str, ...] = ()
    types: tuple[str, ...] = ()
    immutable: bool = False


@dataclass(frozen=True)
class Constant:
    """A name a statement at the top level of a file binds by an assignment (one of several, in a branch too, or a type
    alias), the line it is on, and every name that statement mentions, by its last step: its annotation (a string
    annotation read as the expression it holds) and its value, but no text of its value."""
    line: int
    name: str
    named: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Row:
    """One element of the rows of a table, and the line it is on. param is whether it is a call of the table's row
    (a bare tuple or anything else is not); id is its id keyword when that is a string literal, as written, else None;
    cells holds the name that heads each positional value (the callee of a call, a bare name, the last name of an
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
class Signature:
    """The parameters of a function by kind: its positional ones in order (the first of a method is its receiver),
    its keyword-only ones, and the names of its `*` and `**` parameters ("" for none)."""
    positional: tuple[str, ...] = ()
    keyword_only: tuple[str, ...] = ()
    star: str = ""
    double: str = ""


@dataclass(frozen=True)
class SoleCall:
    """The one call a function's whole body returns or makes, a docstring aside, perhaps awaited: its callee as the
    chain of names it is (("self", "repo", "get")), empty when it is no such chain; each positional argument as the
    bare name it passes, `*` before a starred one, "" for any other expression; each keyword argument as (its
    keyword, or `**` for an unpacked one; the bare name it passes, "" for any other expression); and then, for a body
    that returns a chain of attributes read on the call's result (`return self.repo.get(id).name`), those attributes
    in order, empty when it returns or makes the call itself."""
    callee: tuple[str, ...]
    args: tuple[str, ...] = ()
    keywords: tuple[tuple[str, str], ...] = ()
    then: tuple[str, ...] = ()


@dataclass(frozen=True)
class Function:
    """A function at module level or in a class: its tables, every name its body uses (`mentions`), and each
    statement of its body that holds a block of its own, as (line, the keyword that opens it); asserts: its body holds
    an assertion. owner is the class it is defined in ("" at module level). statements counts the statements of its
    body, nested ones included, and inert those of them that do nothing (a docstring, a statement that only fills a
    place), as the reader of the language tells them; its real statements are the others (see real_statements).
    shape is the reader's fingerprint of its code, the same for two functions the reader holds the same code (see the
    reader); "" when it has no real statement. decorated: it has a decorator; signature: its parameters;
    sole_call: the one call its whole body makes, None when it does not (see SoleCall). returns_named is every name
    its return annotation mentions, by its last step alone, a string annotation read as the expression it holds.
    forwards is the dotted callee of the one call a method only passes its arguments on to, as the reader of the
    language tells a method that does (see the reader), "" for one that does not. named is every name its definition
    mentions, by its last step: its decorators, its parameters' annotations and defaults, its return annotation and its
    body (a string annotation read as the expression it holds, no other text). expressions holds each expression of its
    body that chooses between values, as (line, the keyword the reader records it by)."""
    line: int
    name: str
    tables: tuple[Table, ...] = ()
    mentions: frozenset[str] = frozenset()
    blocks: tuple[tuple[int, str], ...] = ()
    asserts: bool = False
    owner: str = ""
    statements: int = 0
    shape: str = ""
    decorated: bool = False
    signature: Signature = Signature()
    sole_call: SoleCall | None = None
    returns_named: frozenset[str] = frozenset()
    inert: int = 0
    forwards: str = ""
    named: frozenset[str] = frozenset()
    expressions: tuple[tuple[int, str], ...] = ()

    @property
    def real_statements(self) -> int:
        """How many statements of its body do something."""
        return self.statements - self.inert


@dataclass(frozen=True)
class SourceFile:
    """A source file as parsed, never run: how it is shown (e.g. "app/kernel/x" and its ending), its path below the root, what
    it imports, its comments, its functions (at module level and in its classes), its unions, its calls, its
    classes, the calls of the methods of its functions' parameters, the uses of the names it reads and the names it
    defines at module level as functions, in order (module_functions: a name that one `def` binds and nothing else
    binds, so that what it names is a function). named is every name the file mentions anywhere, annotations
    included, by its last step alone; callbacks are the calls of a function's own parameter; method_calls the calls
    of an attribute no import binds (see MethodCall). constants are the names it binds at the top level by an
    assignment (see Constant). unmentioned holds, as (the line of the import, the name it takes), each name an import
    takes from a module that nothing else in the file mentions, in code or an annotation: a name it only passes on
    (listed as text for those who import it from here) or does not use. pieces are its functions and classes at the
    top level and the methods of those classes, in the order of their first line (see Piece). error is how it fails to
    parse, and then it holds nothing else."""
    name: str
    path: tuple[str, ...]
    imports: tuple[Import, ...]
    comments: tuple[Comment, ...] = ()
    functions: tuple[Function, ...] = ()
    unions: tuple[Union, ...] = ()
    error: Unparsable | None = None
    calls: tuple[Call, ...] = ()
    classes: tuple[Class, ...] = ()
    uses: tuple[Use, ...] = ()
    parameter_calls: tuple[ParameterCall, ...] = ()
    module_functions: tuple[str, ...] = ()
    named: frozenset[str] = frozenset()
    callbacks: tuple[Callback, ...] = ()
    method_calls: tuple[MethodCall, ...] = ()
    constants: tuple[Constant, ...] = ()
    unmentioned: frozenset[tuple[int, str]] = frozenset()
    pieces: tuple[Piece, ...] = ()


@dataclass(frozen=True)
class InitFile:
    """A file `init` writes beside the app folder: its path below the folder holding the app, the text `init` would
    write now, and whether it is pinned: the project keeps it as written."""
    path: tuple[str, ...]
    text: str
    pinned: bool = False


@dataclass(frozen=True)
class Known:
    """The profiles a project knows: the one in force for it (None: none is configured), and the bundled ones."""
    in_force: str | None
    bundled: tuple[str, ...]


@dataclass(frozen=True)
class Standing:
    """How the profile in force stands, besides its rules: the guards xarch has that it leaves off, in xarch's order,
    and those the bundled profile it is, or is compared with, leaves off too (baseline_off); the files `init` would
    write now beside the app folder, in the profile's order; and, for a custom profile, every way it is looser than the
    bundled profile it is compared with (looser)."""
    guards_off: tuple[str, ...]
    baseline_off: tuple[str, ...]
    init_files: tuple[InitFile, ...]
    looser: tuple[Loosened, ...] = ()


@dataclass(frozen=True)
class Finding:
    """An enforcement finding that `--strict` fails on: the key of the enforcement section it is under, and the item
    there that fails: a guard left off or an ungoverned file (by name), an init file that drifted, a skip or a dynamic
    import (where it is), a weak check, a key whose check reads a fact the language supplies only partly, a check
    of the profile's own that read nothing (its id), or a part redefined without its litmus (as said)."""
    key: str
    item: str | Drift | At | Weak | Shortfall


@dataclass(frozen=True)
class Enforcement:
    """The state of the check's own enforcement, beside its violations: the guards the profile leaves off, and those the
    bundled profile it is, or is compared with, leaves off too (baseline_off); the app's source files no part and no
    folder of the layout governs (never read, so never checked), as shown; the init files missing or changed; the
    tests skipped or expected to fail, and the dynamic imports, where they are; the checks satisfied to the letter
    only; and strict, the findings `--strict` fails on; the folders the profile excludes, which no check reads; app,
    the name of the app folder the shown paths start with; language, how the language of the app is named;
    approximate, the keys whose check reads a fact the language supplies only partly, so that it may miss what it
    looks for; and checks, the checks the profile writes itself, each by its id with how many facts it read in the
    project (one that read none passes for want of anything to check, and fails `--strict`); unplaced, each part
    the profile redefines without the litmus the bundled profile it is compared with gives it, as said; and known, the
    public names only the tests use that the profile accepts (guards.dead-code.known), which the tests-only check
    then does not list; and translated, the pairs of classes no-twins accepts as translations
    (guards.no-twins.translated), which it then does not report."""
    guards_off: tuple[str, ...] = ()
    baseline_off: tuple[str, ...] = ()
    ungoverned: tuple[str, ...] = ()
    init_files: tuple[Drift, ...] = ()
    skipped: tuple[At, ...] = ()
    dynamic: tuple[At, ...] = ()
    weak: tuple[Weak, ...] = ()
    strict: tuple[Finding, ...] = ()
    excluded: tuple[Excluded, ...] = ()
    app: str = ""
    language: str = ""
    approximate: tuple[Shortfall, ...] = ()
    checks: tuple[tuple[str, int], ...] = ()
    unplaced: tuple[str, ...] = ()
    known: tuple[KnownName, ...] = ()
    translated: tuple[Translation, ...] = ()


@dataclass(frozen=True)
class Twins:
    """What the no-twins check found: the violations, and the pairs it accepts as translations, which it does not
    report."""
    violations: tuple[Violation, ...]
    translated: tuple[Translation, ...]


@dataclass(frozen=True)
class Accepting:
    """What the tests-only check lists once the public names the profile accepts as only the tests' are taken out:
    the findings still listed, each entry that no longer holds among them, and the names accepted."""
    listed: tuple[Violation | Weak, ...]
    known: tuple[KnownName, ...]


@dataclass(frozen=True)
class Checked:
    """What a check found: the violations, in the order the checks found them; the state of its enforcement; and the
    profile it checked against."""
    violations: tuple[Violation, ...]
    enforcement: Enforcement
    profile: Profile


@dataclass(frozen=True)
class Resolved:
    """A path settled: which folder it lies in (app, tests or project), its steps below that folder, the path in full,
    whether it exists, and how it is shown: below the folder holding the app, or in full when it lies outside it."""
    within: str
    steps: tuple[str, ...]
    path: Path
    exists: bool
    shown: str


@dataclass(frozen=True)
class Sited:
    """A file where the profile places it, read for a module that reads the app's code: where it lies (one of the
    places of published, IN_PART to NO_PART) and the part it lies in ("" for none)."""
    lies: str
    part: str


@dataclass(frozen=True)
class PartAt:
    """A part as a target names it (the part, its scope, a path below it), how the docs name it, and its folder below
    the project root (a placeholder for an instance that is not fixed, such as <module>): what a place may import, and
    the parts near a place no part claims."""
    target: Target
    folder: str
    path: str


@dataclass(frozen=True)
class PartPlace:
    """A place in a part: the path as resolved; the part claiming it (place: its name, the instance it is in and the
    path below), its words (info) and the word of one instance of its repeating folder (singular); what its code may
    import, as places and in the docs' words; the outside packages it may import (None: not checked) and the names it
    may not use; and the tier that tests it with the folder and the file its test would be in (the file a name
    pattern when it is not its own, empty when the place is no source file), or None when no tier does, and then why
    (untested; "" when the profile does not say)."""
    found: Resolved
    place: Place
    info: PartInfo
    singular: str
    reaches: tuple[PartAt, ...]
    may_import_text: str
    libraries: tuple[str, ...] | None
    forbidden: tuple[str, ...]
    tier: CheckedTier | None
    test_folder: str
    test_file: str
    untested: str


@dataclass(frozen=True)
class StructurePlace:
    """A folder of the layout no part claims: the path as resolved, and the parts below it."""
    found: Resolved
    nearest: tuple[PartAt, ...]


@dataclass(frozen=True)
class UngovernedPlace:
    """A place in no part and no folder of the layout, below a folder the profile excludes, or outside the app and its
    tests: the path as resolved; the parts near it (none when it is excluded or outside the app); whether a file there
    is a violation (None when no part is near, so that the closed-tree guard has nothing to say); and why it is
    ungoverned when that is not plain."""
    found: Resolved
    nearest: tuple[PartAt, ...]
    closed_tree: bool | None
    note: str


@dataclass(frozen=True)
class SuitePlace:
    """A file or folder below the tests root that is no fake: the path as resolved; whether it is a test (else a
    helper or other support); the tier it lies in (None: none), the part it mirrors (place, with its words and the
    word of one instance of its folder, None when it mirrors none) and what it may import, as places and in the docs'
    words; the names it may not use; whether it may import the fakes and where they live; and the one folder it may
    import test code from; note, why it is in no tier, for a test."""
    found: Resolved
    test: bool
    tier: CheckedTier | None
    place: Place | None
    info: PartInfo | None
    singular: str
    reaches: tuple[PartAt, ...]
    may_import_text: str
    forbidden: tuple[str, ...]
    may_use_fakes: bool
    fakes_path: str
    test_code_from: str
    note: str


@dataclass(frozen=True)
class FakePlace:
    """A test fake: the path as resolved, where the fakes live, the one folder it may import test code from, and that
    it is no test."""
    found: Resolved
    fakes_path: str
    test_code_from: str
    note: str


Placed = PartPlace | StructurePlace | UngovernedPlace | SuitePlace | FakePlace
"""What a place is and what code there may do, the answer of `xarch where`, one variant per kind of place."""
