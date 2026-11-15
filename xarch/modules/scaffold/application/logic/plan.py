"""What a skeleton turns into on disk: a package file for every folder, and every file, parents first.

The project docs and files go beside the app folder, in the folder holding it.
"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


def plan(entries: Iterable[tuple[tuple[str, ...], bool]]) -> list[tuple[str, ...]]:
    files = [("__init__.py",)]
    for path, is_dir in entries:
        files.append(path + ("__init__.py",) if is_dir else path)
    return files


def app_name(root: Path, resolved: Path) -> str:
    """The name of the app folder, which is the package name `check` uses: for `.` and `..`, that of resolved, the
    folder root names with every step resolved."""
    return root.name if root.name not in ("", "..") else resolved.name


def holder(root: Path, absolute: Path) -> Path:
    """The folder holding the app folder: where the project docs go. For `.` and `..`, the folder above absolute, root
    made absolute."""
    return root.parent if root.name not in ("", "..") else absolute.parent
