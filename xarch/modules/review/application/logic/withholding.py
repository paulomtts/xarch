"""Which files review never sends: those a path the profile writes under `review.never` matches. A path is matched
step by step against a file's path below the app: a step as written, `*` for any text inside one step, and a step
that is `**` for any number of folders, none included; a path that matches a folder holds back every file below it."""
from __future__ import annotations

import re

from xarch.modules.review.domain.published import NEVER, LeftOut
from xarch.modules.review.domain.values import CodeFile, Found

ANY_FOLDERS = "**"
"""A step of a path that stands for any number of folders, none included."""


def _step(pattern: str, step: str) -> bool:
    return re.fullmatch("[^/]*".join(re.escape(piece) for piece in pattern.split("*")), step) is not None


def _starts(pattern: tuple[str, ...], path: tuple[str, ...]) -> bool:
    """Whether the pattern matches the path or a folder above it."""
    if not pattern:
        return True
    if pattern[0] == ANY_FOLDERS:
        return any(_starts(pattern[1:], path[skipped:]) for skipped in range(len(path) + 1))
    return bool(path) and _step(pattern[0], path[0]) and _starts(pattern[1:], path[1:])


def _below_app(file: str) -> tuple[str, ...]:
    """The steps below the app of a file of the app, shown from the folder holding the app."""
    return tuple(file.split("/")[1:])


def _held_by(file: CodeFile, never: tuple[str, ...]) -> str:
    """The first path of never that matches the file, "" for none."""
    path = _below_app(file.file)
    return next((pattern for pattern in never if _starts(tuple(pattern.split("/")), path)), "")


def held_back(found: Found, never: tuple[str, ...]) -> Found:
    """The files found, with each file read that a path of never matches moved to those left out, after the others,
    with the path that matched; its text goes nowhere."""
    kept = tuple(file for file in found.read if not _held_by(file, never))
    held = tuple(LeftOut(file.file, NEVER, len(file.text), pattern) for file in found.read
                 if (pattern := _held_by(file, never)))
    return Found(kept, found.unread + held)
