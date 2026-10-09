"""What a skeleton turns into on disk: a package file for every folder, and every file, parents first.

The project docs go beside the app folder, in the folder holding it.
"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


def plan(entries: Iterable[tuple[tuple[str, ...], bool]]) -> list[tuple[str, ...]]:
    files = [("__init__.py",)]
    for path, is_dir in entries:
        files.append(path + ("__init__.py",) if is_dir else path)
    return files


def holder(root: Path) -> Path:
    """The folder holding the app folder: where the project docs go. `.` and `..` are resolved first."""
    return root.parent if root.name not in ("", "..") else root.absolute().parent
