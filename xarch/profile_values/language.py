"""The language of the app as a check reads it: spec reads it from the language's data file, the rules module checks
the source with it."""
from __future__ import annotations

import re
from dataclasses import dataclass

from xarch.kernel.placement import Marks
from xarch.profile_values.capabilities import Supply

NOTHING = "nothing"
"""The one value of the data file's `unannotated`: a method with no return annotation gives no value."""


@dataclass(frozen=True)
class RecordMark:
    """What makes a class an immutable record in the language, in one of four forms, exactly one of base, decorator,
    fields and type given: an outside name among its bases (base, as its steps); a decorator (decorator, as its steps)
    called with each keyword of keywords, each (name, value as written) (none: however it is written, bare or called);
    a keyword that marks every field (fields); or a wrapper type (type, as its steps)."""
    base: tuple[str, ...] = ()
    decorator: tuple[str, ...] = ()
    keywords: tuple[tuple[str, str], ...] = ()
    fields: str = ""
    type: tuple[str, ...] = ()


@dataclass(frozen=True)
class InterfaceMark:
    """What makes a class an interface in the language: an outside name among its bases (base, as its steps), or a
    keyword it is declared with or carries (keyword); exactly one of the two is given."""
    base: tuple[str, ...] = ()
    keyword: str = ""


LINE = "line"
"""The kind of a comment form that runs from its marker to the end of its line."""
BLOCK = "block"
"""The kind of a comment form that runs from its opening to its closing."""


@dataclass(frozen=True)
class CommentForm:
    """One form a comment of the language is written in: its kind (LINE, BLOCK or "doc"), the marker that opens it, and
    the one that closes it ("" for a line form, and for a doc form that runs to the end of its line)."""
    kind: str
    opening: str
    closing: str = ""


@dataclass(frozen=True)
class CheckedLanguage:
    """The language of the app as a check reads it: how a message names it, the endings of a source file's name
    (extensions, in the order written; a message prints the first), the files that stand for the folder holding them
    (package_files; none: no file does), the marks that make a class an interface (interface: an outside name
    among its bases, or a keyword it is declared with or carries), the dotted names of what imports by a name worked
    out when the code runs; and the tokens of its code: what a private name starts with, the pattern of a special
    name (special: a regular expression the whole name matches), the special method calling an instance runs, the
    return annotations of no value as its reader writes them (nothing), whether a method with no return annotation
    gives none (unannotated: nothing when it does; empty when the data file does not say), the forms a comment is
    written in (comments, in the order written: a line form runs from its marker to the end of its line, a block form
    from its opening to its closing, and a doc form, a comment the language keeps its documentation in, the same, an
    empty closing being the end of its line; none: the language has no comments), the comments its tools read (after
    the marker of a comment of any form, a space standing for any spaces), how line 1 names the program that runs the
    file, how line 1 or 2 declares the encoding (a regular expression, after the marker of a comment), and
    the keywords of the statements that branch and of the expressions that choose between values
    (branching_expressions); and what makes a class an immutable record (immutable). An empty token: the language
    has none. supplies are the facts its reader supplies, each graded (None: its data file does not say); importing
    is how a file imports a name from another file of the app, {dotted} standing for that file's dotted path and
    {name} for the name (empty: its data file does not say); names is the pattern of a name the language allows, a
    regular expression (empty: its data file gives none); package is the pattern of what an import names from
    outside the app as one step, and member the text that joins a package to a name in it in a profile's lists (both
    empty: its data file does not say, and an outside name is then its whole text); standard_modules are the top-level
    modules of its standard library, which the reader is handed to mark an import of one: spec fills them from the
    data file's lists or from the runtime (empty: no module is standard)."""
    title: str = ""
    extensions: tuple[str, ...] = ()
    package_files: tuple[str, ...] = ()
    interface: tuple[InterfaceMark, ...] = ()
    dynamic: tuple[tuple[str, ...], ...] = ()
    private: str = ""
    special: str = ""
    call: str = ""
    nothing: tuple[str, ...] = ()
    comments: tuple[CommentForm, ...] = ()
    directives: tuple[str, ...] = ()
    shebang: str = ""
    encoding: str = ""
    branching: tuple[str, ...] = ()
    supplies: tuple[Supply, ...] | None = None
    importing: str = ""
    immutable: tuple[RecordMark, ...] = ()
    branching_expressions: tuple[str, ...] = ()
    names: str = ""
    package: str = ""
    member: str = ""
    unannotated: str = ""
    standard_modules: frozenset[str] = frozenset()

    @property
    def marks(self) -> Marks:
        return Marks(self.extensions, self.package_files)

    @property
    def extension(self) -> str:
        """The first ending of a source file's name, the one a message prints; "" when the language gives none. Never
        what decides whether a file is a source file: every ending does (see marks)."""
        return self.extensions[0] if self.extensions else ""

    @property
    def package_file(self) -> str:
        """The first file that stands for its folder, the one a message prints and init writes; "" when the language
        has none."""
        return self.package_files[0] if self.package_files else ""

    @property
    def comment(self) -> str:
        """The marker the docs and `%comment%` print: the first line form's, else the first block form's opening; ""
        when the language has neither. A doc form's opening never is."""
        line = next((form.opening for form in self.comments if form.kind == LINE), "")
        return line or next((form.opening for form in self.comments if form.kind == BLOCK), "")

    def is_special(self, name: str) -> bool:
        """Whether a name is one the language reserves for itself: special, a regular expression, matches the whole
        name; no name is when the language gives none."""
        return bool(self.special) and re.fullmatch(self.special, name) is not None

    def gives_nothing(self, returns: str | None) -> bool:
        """Whether a method whose return annotation is returns, as the reader writes it (None: it has none), gives no
        value: its annotation is one nothing lists, or it has none and unannotated says so."""
        return returns in self.nothing if returns is not None else self.unannotated == NOTHING
