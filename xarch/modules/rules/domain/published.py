"""The values the rules module hands out as they are, which its contract re-exports as it does an id: each is read
outside rules just as rules holds it, so there is nothing to reshape. Everything else rules hands out is a type of the
contract's own.

    At    a place in a file, as the enforcement section names a skip or a dynamic import; the command line shows it
    Weak  a check met to the letter only, which the enforcement section lists and the command line shows
    Slot  a slot of a check as a profile writes it, which `profile explain checks` shows
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class At:
    """A place in a file: how the file is shown and the line."""
    file: str
    line: int


@dataclass(frozen=True)
class Weak:
    """A check satisfied to the letter only, which is not a violation: the stable id of the check it concerns (one of
    RULES), where, and why; fix is what to do about it, empty when there is no advice."""
    rule: str
    file: str
    line: int
    message: str
    fix: str = ""


@dataclass(frozen=True)
class Slot:
    """A slot of a check as a profile writes it: its name, what it is for, what it accepts, and the category of words
    it is written with ("" for one written in words of its own)."""
    name: str
    meaning: str
    accepts: str
    takes: str = ""
