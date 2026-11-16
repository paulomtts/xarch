"""Where the app folder is: its name, which is the package name `check` uses, and the folder holding it, where the
project docs and files go."""
from __future__ import annotations

from pathlib import Path


def app_name(root: Path, resolved: Path) -> str:
    """The name of the app folder, which is the package name `check` uses: for `.` and `..`, that of resolved, the
    folder root names with every step resolved."""
    return root.name if root.name not in ("", "..") else resolved.name


def holder(root: Path, absolute: Path) -> Path:
    """The folder holding the app folder: where the project docs go. For `.` and `..`, the folder above absolute, root
    made absolute."""
    return root.parent if root.name not in ("", "..") else absolute.parent
