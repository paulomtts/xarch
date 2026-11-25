"""Which violations a check of some paths shows: each of a file or folder at or below one of the paths, the rest only
counted. A violation names its file from the folder holding the app folder, or, when its first step is the tests
folder's name, from the folder holding the tests folder."""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import PurePath

from xarch.kernel.violations import Violation


def chosen(found: Sequence[Violation], paths: Sequence[PurePath], home: PurePath,
           tests: PurePath | None) -> tuple[list[Violation], int]:
    """The violations of found at or below one of paths, in their order, and how many others there are; paths are
    given in full, as home, the folder holding the app folder, and tests, the tests folder (None: none)."""
    kept = [v for v in found if any(_below(_place(v.file, home, tests), path) for path in paths)]
    return kept, len(found) - len(kept)


def _place(file: str, home: PurePath, tests: PurePath | None) -> PurePath:
    steps = PurePath(file).parts
    if tests is not None and steps and steps[0] == tests.name:
        return tests.parent.joinpath(*steps)
    return home.joinpath(*steps)


def _below(place: PurePath, path: PurePath) -> bool:
    return place == path or path in place.parents
