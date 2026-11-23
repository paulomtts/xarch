"""The values the source rules reason about: already-parsed source files."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.source import CommentSpan, Import, Unparsable
from xarch.modules.rules.domain.published import Piece


@dataclass(frozen=True)
class Comment:
    """A comment as written, its marker included (and a block's closing), and the line it is on; where it lies there:
    from column column to column end of line last (0: its own line), columns counted in characters from 0, end past its
    last character; the marker it opens with, as written ("" when the reader does not say); and whether it is a doc
    comment, one the language keeps its documentation in."""
    line: int
    text: str
    column: int = 0
    end: int = 0
    last: int = 0
    marker: str = ""
    doc: bool = False

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
"""The place a name reaches, as steps: for a name of the app, the app's root, the steps of the file that defines it
below the root, then the name; for an outside name, its package as one step, then the steps below it. However the
import is written (absolute, relative, or by a name the project maps to a folder), the reader follows it. None for
a name no import binds (a literal, an expression, a parameter, an assignment), and for an import the reader could
not follow (see Import.unresolved)."""


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
    path the import that binds its first name names from the top (2 here: `from datetime import datetime`; 0 for a
    relative import, which names none of them so, and whose line therefore carries no finding on the path); a builtin
    used by its bare name is (<its namespace>, <name>), bound 0."""
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
    marked (see RecordMark); interface: it is an interface, as the reader was told one is marked (see
    InterfaceMark); public: it is for other files to use, as the language's reader says; record: it is a record, as the
    language's reader says."""
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
    interface: bool = False
    public: bool = True
    record: bool = False


@dataclass(frozen=True)
class Constant:
    """A name a statement at the top level of a file binds by an assignment (one of several, in a branch too, or a type
    alias), the line it is on, and every name that statement mentions, by its last step: its annotation (a string
    annotation read as the expression it holds) and its value, but no text of its value; and whether it is for other
    files to use, as the language's reader says (public)."""
    line: int
    name: str
    named: frozenset[str] = frozenset()
    public: bool = True


@dataclass(frozen=True)
class Row:
    """One element of the rows of a table, and the line it is on. written is whether it is a call of the table's row
    (a bare tuple or anything else is not); id is its id keyword when that is a string literal, as written, else None;
    cells holds the name that heads each positional value (the callee of a call, a bare name, the last name of an
    attribute), None where a value has none."""
    line: int
    written: bool
    id: str | None
    cells: tuple[str | None, ...]


@dataclass(frozen=True)
class Table:
    """One table decorating a test function (the decorator the profile names), and the line it is on: its parameter names, and its rows
    (None when the rows are neither a list or tuple literal nor the name of one assigned at the top of the file); form, the
    index from 0 of the form it was read by in the framework's list of forms; and runs, the line of the statement of the
    test's own body that runs its rows, 0 when none does."""
    line: int
    columns: tuple[str, ...]
    rows: tuple[Row, ...] | None
    form: int
    runs: int


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
    body that chooses between values, as (line, the keyword the reader records it by). public: it is for other files to
    use, as the language's reader says."""
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
    public: bool = True

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
    binds, so that what it names is a function, each public as that function is). named is every name the file
    mentions anywhere, annotations included, by its last step alone; callbacks are the calls of a function's own
    parameter; method_calls the calls of an attribute no import binds (see MethodCall). constants are the names it
    binds at the top level by an assignment (see Constant). unmentioned holds, as (the line of the import, the name it
    takes), each name an import takes from a module that nothing else in the file mentions, in code or an annotation: a
    name it only passes on (listed as text for those who import it from here) or does not use. pieces are its functions and classes at the
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
