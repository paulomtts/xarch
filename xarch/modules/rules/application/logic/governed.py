"""Which source files of the app the checks read: a file below a folder the profile excludes is not looked at at all;
of the rest, one that lies in a part, or is the package file of a folder of the layout (the file the language has
stand for the root, for `modules`, for `modules/<name>` and the like), is governed and read; anything else, such as a
file `modules/<name>/helpers`, an extra top-level folder or a script at the root, is ungoverned: never read, listed in
the enforcement section, and what the closed-tree guard (the "closed-tree" rules of expansion.book) reports. Only
source files, the ones the reader lists, are looked at.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.modules.rules.application.logic.places import excluded_by, file_place
from xarch.modules.rules.domain.values import Profile, SourceFile


def ungoverned(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[str]:
    """The files in no part and no folder of the layout, whether the guard is on or not, each shown as
    shown/<path>: no check reads them."""
    return ["/".join((shown, *path)) for path in paths if not governed(profile, path)]


def excluded(profile: Profile, path: tuple[str, ...]) -> bool:
    """Whether the file at path below the app lies below a folder the profile excludes."""
    return excluded_by(profile, path) is not None


def governed(profile: Profile, path: tuple[str, ...]) -> bool:
    """Whether a part or a folder of the layout governs the file at path below the app, so that it is read."""
    return file_place(profile, path) is not None


def unread(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[SourceFile]:
    """The files no check reads, each a file with no content, shown as shown/<path>: what the checks that list them
    know of them."""
    return [SourceFile("/".join((shown, *path)), path, ()) for path in paths if not governed(profile, path)]
