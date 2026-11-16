"""The language of the app as a check reads it: spec reads it from the language's data file, the rules module checks
the source with it."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.capabilities import Supply
from xarch.kernel.placement import Marks


@dataclass(frozen=True)
class CheckedLanguage:
    """The language of the app as a check reads it: how a message names it, the ending of a source file's name, the
    file that stands for the folder holding it, the dotted names that mark a class as an interface, and those of what
    imports by a name worked out when the code runs; and the tokens of its code: what a private name starts with, what
    a special name starts and ends with, the special method calling an instance runs, the return annotation of no
    value, the marker of a line comment, the comments its tools read (after the marker, a space standing for any
    spaces), how line 1 names the program that runs the file, how line 1 or 2 declares the encoding (a regular
    expression, after the marker), and the keywords of the statements that branch. An empty token: the language has
    none. supplies are the facts its reader supplies, each graded (None: its data file does not say); importing is how a
    file imports a name from another file of the app, {dotted} standing for that file's dotted path and {name} for the
    name (empty: its data file does not say)."""
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

    @property
    def marks(self) -> Marks:
        return Marks(self.extension, self.package_file)

    def is_special(self, name: str) -> bool:
        """Whether a name is one the language reserves for itself: it starts and ends as a special name does."""
        return bool(self.special) and name.startswith(self.special) and name.endswith(self.special)

    def is_public(self, name: str) -> bool:
        """Whether a name is for other files to use: it does not start as a private name does, which a special one may."""
        return not (self.private and name.startswith(self.private))

    def is_private(self, name: str) -> bool:
        """Whether a name is private to its file or folder: it is not public, and it is no special name."""
        return not self.is_public(name) and not self.is_special(name)
