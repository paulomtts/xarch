"""The closed-tree guard: every Python file of the app lies in a part, or is the package file of a folder of the
layout (the root's `__init__.py`, `modules/__init__.py`, `modules/<name>/__init__.py` and the like), which only holds
the tree together. Anything else, such as `modules/<name>/helpers.py`, an extra top-level folder or a script at the
root, is a violation. Only .py files are looked at.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Profile

MESSAGE = ("lies in no part and no folder of the layout: move it into a part, or add its folder to the layout "
           "(closed-tree)")
FIX = "move it into a part, or add its folder to the layout"


def violations(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[Violation]:
    """paths are below the app root, shown as shown/<path>."""
    if not profile.closed_tree:
        return []
    return [Violation(file, 0, MESSAGE, "closed-tree", FIX) for file in ungoverned(paths, profile, shown)]


def ungoverned(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[str]:
    """The files in no part and no folder of the layout, whether the guard is on or not, each shown as
    shown/<path>: no check reads them."""
    return ["/".join((shown, *path)) for path in paths if place(profile, dotted(path)[0]) is None]
