"""What a skeleton turns into on disk: the package file of every folder, when the language has one, and every file,
parents first."""
from __future__ import annotations

from collections.abc import Iterable


def plan(entries: Iterable[tuple[tuple[str, ...], bool]], package_file: str) -> list[tuple[str, ...]]:
    """The files to write: package_file at the root and in every folder (none at all when it is "": the language has
    no package file), and every file, in the order given."""
    found = [((), True), *entries]
    return [path + (package_file,) if is_dir else path for path, is_dir in found if package_file or not is_dir]
