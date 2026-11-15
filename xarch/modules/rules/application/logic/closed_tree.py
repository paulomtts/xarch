"""The closed-tree guard: every Python file of the app lies in a part, or is the package file of a folder of the
layout (the root's `__init__.py`, `modules/__init__.py`, `modules/<name>/__init__.py` and the like), which only holds
the tree together. Anything else, such as `modules/<name>/helpers.py`, an extra top-level folder or a script at the
root, is a violation. Only .py files are looked at.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.domain.values import Profile

MESSAGE = "lies in no part and no folder of the layout (closed-tree)"


def violations(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[Violation]:
    """paths are below the app root, shown as shown/<path>."""
    if not profile.closed_tree:
        return []
    return [Violation(file, 0, MESSAGE, "closed-tree",
                      f"move {file} into the part that fits it (run xarch where {file}), or add its folder to the layout")
            for file in ungoverned(paths, profile, shown)]


def ungoverned(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[str]:
    """The files in no part and no folder of the layout, whether the guard is on or not, each shown as
    shown/<path>: no check reads them."""
    return ["/".join((shown, *path)) for path in paths if place(profile, dotted(path)[0]) is None]


def excluded(profile: Profile, path: tuple[str, ...]) -> bool:
    """Whether the file at path below the app lies below a folder the profile excludes."""
    return any(path[:len(e.path)] == e.path for e in profile.excluded)


def governed(profile: Profile, path: tuple[str, ...]) -> bool:
    """Whether a part or a folder of the layout governs the file at path below the app, so that it is read."""
    return place(profile, dotted(path)[0]) is not None
