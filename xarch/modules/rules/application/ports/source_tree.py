from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.values import SourceFile, TableForm


class SourceTree(Protocol):
    """The Python files below a root folder, listed, then read already parsed."""

    def is_dir(self, root: Path) -> bool: ...

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        """The path below root of every .py file, sorted."""
        ...

    def read(self, root: Path, paths: list[tuple[str, ...]], table: TableForm | None = None) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised."""
        ...

    def exists(self, path: Path) -> bool:
        """Whether a file or a folder is at path."""
        ...

    def text(self, path: Path) -> str | None:
        """The text of any file at path, None when there is no file there."""
        ...
