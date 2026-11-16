"""The values review reads through its ports: the parts of the profile as placement offers them, and the files found
at the paths given, read or not."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.source import Import, Unparsable
from xarch.modules.review.domain.published import LeftOut


@dataclass(frozen=True)
class PartText:
    """A part as placement offers it: its name, its folder as the docs show it, its litmus test ("" for none) and its
    role."""
    name: str
    folder: str
    litmus: str
    role: str


@dataclass(frozen=True)
class CodeFile:
    """A source file of the app in a part, read: the file, as `check` shows it; the part; its text; its imports; and
    how it fails to parse (None: it parses)."""
    file: str
    part: str
    text: str
    imports: tuple[Import, ...] = ()
    error: Unparsable | None = None


@dataclass(frozen=True)
class Found:
    """The files found at the paths given, each once: those read, in a part of the app, and those that are not, each
    with why, both in the order they were found."""
    read: tuple[CodeFile, ...]
    unread: tuple[LeftOut, ...] = ()
