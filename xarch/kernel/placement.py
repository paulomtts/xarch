"""The primitives of where a path sits among named path patterns: the step of a pattern that stands for any name, the
target that reaches everything, how a language writes a path, and a path's place. The placement rule of kernel/logic/
takes and answers them (see its placement for the rule); the values of a profile it reads, what a target of a rule
reaches and a repeating folder, are profile_values' placement.
"""
from __future__ import annotations

from dataclasses import dataclass

EACH = "*"
EVERYTHING = "*"


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
