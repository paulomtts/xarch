from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.values import SourceFile


class SourceTree(Protocol):
    """The Python files below a root folder, listed, then read already parsed."""

    def is_dir(self, root: Path) -> bool: ...

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        """The path below root of every .py file, sorted."""
        ...

    def read(self, root: Path, paths: list[tuple[str, ...]]) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error."""
        ...
