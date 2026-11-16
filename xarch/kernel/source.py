"""What a source file says as its language's reader records it, in terms no language owns: the values a reader answers
with, which the rules module checks the app's imports with and spec its examples' imports with."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Import:
    """One import as written. module is the name it imports from, as steps; names is None when it imports module as
    a whole, else the names it imports from it. relative: module is named from the importing file's own folder, which
    the import climbs up folders above before it takes module's steps; else module is named from the top. standard:
    an absolute import whose first step names the standard library. written: the module as the source writes it.
    every: it imports every name the module makes public rather than names it lists (names then holds how the source
    writes that)."""
    line: int
    module: tuple[str, ...]
    names: tuple[str, ...] | None = None
    relative: bool = False
    up: int = 0
    standard: bool = False
    written: str = ""
    every: bool = False


@dataclass(frozen=True)
class Unparsable:
    """A source text that does not parse: the line the parser stopped at (0 when it gives none) and its message."""
    line: int
    message: str
