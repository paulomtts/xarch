"""The values of a profile that say where code may reach: what a part's rule names as a target, and a repeating
folder. Spec builds them from the profile, rules checks imports with them, and the placement rule of kernel/logic/
takes them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

InstanceScope = Literal["own", "any", "none"]


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
    scope: InstanceScope = "none"
    sub: tuple[str, ...] = ()
    names: str = ""
