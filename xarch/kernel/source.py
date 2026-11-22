"""What a source file says as its language's reader records it, in terms no language owns: the values a reader answers
with, which the rules module checks the app's imports with and spec its examples' imports with, and where each
comment lies, which review hides before it sends a text."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Import:
    """One import as written. module is the name it imports from, as steps; names is None when it imports module as
    a whole, else the names it imports from it. relative: module is named from the importing file's own folder, which
    the import climbs up folders above before it takes module's steps; else module is named from the top. standard:
    an absolute import whose first step names the standard library. written: the module as the source writes it.
    every: it imports every name the module makes public rather than names it lists (names then holds how the source
    writes that). last: the last line the import spans, when it is not its first (0: it spans one line). unresolved:
    the import names a place of the code being read (relative, or by an alias the project maps) that the reader found
    no file or folder for."""
    line: int
    module: tuple[str, ...]
    names: tuple[str, ...] | None = None
    relative: bool = False
    up: int = 0
    standard: bool = False
    written: str = ""
    every: bool = False
    last: int = 0
    unresolved: bool = False


@dataclass(frozen=True)
class Unparsable:
    """A source text that does not parse: the line the parser stopped at (0 when it gives none) and its message;
    unreadable: the file could not be read as text at all (it is not UTF-8, or it cannot be opened), so it was never
    parsed, and the message says which."""
    line: int
    message: str
    unreadable: bool = False


@dataclass(frozen=True)
class CommentSpan:
    """Where one comment of a source text lies, as its language's reader finds it: from column start of line to
    column end of line last (0: the line it starts on), columns counted in characters from 0, end being past its last
    character. The text before it on its first line and after it on its last are not part of it."""
    line: int
    start: int
    end: int
    last: int = 0
