"""What a skeleton turns into on disk: a package file for every folder, and every file, parents first."""
from __future__ import annotations

from collections.abc import Iterable


def plan(entries: Iterable[tuple[tuple[str, ...], bool]], package_file: str) -> list[tuple[str, ...]]:
    files = [(package_file,)]
    for path, is_dir in entries:
        files.append(path + (package_file,) if is_dir else path)
    return files
