from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.values import SourceFile, TableForm


class SourceTree(Protocol):
    """The source files below a root folder, listed, then read already parsed."""

    def absent(self, roots: Iterable[Path]) -> list[Path]:
        """The roots that are no folder, in the order given."""
        ...

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        """The path below root of every source file, sorted."""
        ...

    def read(self, root: Path, paths: list[tuple[str, ...]], table: TableForm | None = None) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised."""
        ...

    def existing(self, paths: Iterable[Path]) -> frozenset[Path]:
        """The paths at which a file or a folder is."""
        ...

    def text(self, path: Path) -> str | None:
        """The text of any file at path, None when there is no file there."""
        ...
