"""How every command shows a path: from the working folder when it lies below it, else in full."""
from __future__ import annotations

from pathlib import Path


def shown(path: Path, cwd: Path) -> str:
    """The path below cwd, written with `/`, when it lies there; else as it is."""
    return (path.relative_to(cwd) if path.is_relative_to(cwd) else path).as_posix()
