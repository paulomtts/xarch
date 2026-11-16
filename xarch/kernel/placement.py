"""The vocabulary of where a path sits among named path patterns, and of what a rule's target reaches: the values the
placement rule of kernel/logic/ takes and answers (see its placement for the rule).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EACH = "*"
EVERYTHING = "*"

Scope = Literal["own", "any", "none"]


@dataclass(frozen=True)
class Repeat:
    """A repeating folder: the word one instance of it is called by, and the folder it repeats in."""
    word: str
    root: tuple[str, ...]


@dataclass(frozen=True)
class Target:
    """What a part may import: a part, or EVERYTHING; the instance it is in; optionally only a path below it; and
    optionally (names, a pattern) only the names that match it."""
    part: str
    scope: Scope = "none"
    sub: tuple[str, ...] = ()
    names: str = ""


@dataclass(frozen=True)
class Marks:
    """How the language of the app writes a path: the ending a source file's name carries, and the name of the file that
    stands for the folder holding it. Empty marks leave a path as written."""
    extension: str = ""
    package_file: str = ""


@dataclass(frozen=True)
class Place:
    """Where a path sits: the part claiming it (None if none does), the instance `*` captured, and the path below."""
    part: str | None
    instance: str | None = None
    sub: tuple[str, ...] = ()
