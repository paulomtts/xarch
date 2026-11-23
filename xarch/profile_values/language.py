"""The language of the app as a check reads it: spec reads it from the language's data file, the rules module checks
the source with it."""
from __future__ import annotations

import re
from dataclasses import dataclass

from xarch.kernel.placement import Marks
from xarch.profile_values.capabilities import Supply


@dataclass(frozen=True)
class RecordMark:
    """What makes a class an immutable record in the language: an outside name among its bases or its decorators, and,
    for a decorator, the keywords it is called with, each with its value as written (none: any call, or none)."""
    path: tuple[str, ...]
    keywords: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class InterfaceMark:
    """What makes a class an interface in the language: an outside name among its bases (base, as its steps), or a
    keyword it is declared with or carries (keyword); exactly one of the two is given."""
    base: tuple[str, ...] = ()
    keyword: str = ""


@dataclass(frozen=True)
class CheckedLanguage:
    """The language of the app as a check reads it: how a message names it, the ending of a source file's name, the file
    that stands for the folder holding it, the dotted names that mark a class as an interface, and those of what
    imports by a name worked out when the code runs; and the tokens of its code: what a private name starts with,
    the pattern of a special name (special: a regular expression the whole name matches), the special method calling
    an instance runs, the return annotation of no value, the marker of a line comment, the comments its tools read
    (after the marker, a space standing for any spaces), how line 1 names the program that runs the file, how line 1
    or 2 declares the encoding (a regular expression, after the marker), and the keywords of the statements that
    branch and of the expressions that choose between values (branching_expressions); and what makes a class an
    immutable record (immutable). An empty token: the language has none. supplies are the facts its reader supplies,
    each graded (None: its data file does not say); importing is how a file imports a name from another file of the
    app, {dotted} standing for that file's dotted path and {name} for the name (empty: its data file does not say);
    names is the pattern of a name the language allows, a regular expression (empty: its data file gives none);
    package is the pattern of what an import names from outside the app as one step, and member the text that joins
    a package to a name in it in a profile's lists (both empty: its data file does not say, and an outside name is
    then its whole text)."""
    title: str = ""
    extension: str = ""
    package_file: str = ""
    interface: tuple[tuple[str, ...], ...] = ()
    dynamic: tuple[tuple[str, ...], ...] = ()
    private: str = ""
    special: str = ""
    call: str = ""
    nothing: str = ""
    comment: str = ""
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

    @property
    def marks(self) -> Marks:
        return Marks(self.extension, self.package_file)

    def is_special(self, name: str) -> bool:
        """Whether a name is one the language reserves for itself: special, a regular expression, matches the whole
        name; no name is when the language gives none."""
        return bool(self.special) and re.fullmatch(self.special, name) is not None

    def is_public(self, name: str) -> bool:
        """Whether a name is for other files to use: it does not start as a private name does, which a special one may."""
        return not (self.private and name.startswith(self.private))
