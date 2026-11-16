"""The values the rules module hands out as they are, which its contract re-exports as it does an id: each is read
outside rules just as rules holds it, so there is nothing to reshape. Everything else rules hands out is a type of the
contract's own.

    At    a place in a file, as the enforcement section names a skip or a dynamic import; the command line shows it
    Weak  a check met to the letter only, which the enforcement section lists and the command line shows
    Slot  a slot of a check as a profile writes it, which `profile explain checks` shows
    Drift an init file as it stands against what `init` would write, which the enforcement section lists
    KeyFacts what the format says of a key the profile sets nowhere, which the command line shows
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


@dataclass(frozen=True)
class Drift:
    """An init file as it stands: missing, or changed from what `init` would write (pinned files only). path is its
    path below the folder holding the app."""
    path: tuple[str, ...]
    state: str


@dataclass(frozen=True)
class KeyFacts:
    """What the format says of a key: how a profile writes it ("" for no example), its own name, and what holds it
    when it is set on each of a kind of thing (part or tier, "" for neither)."""
    example: str = ""
    name: str = ""
    holder: str = ""
