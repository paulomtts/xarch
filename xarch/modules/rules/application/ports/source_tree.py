from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from xarch.kernel.logic.testing import CaseTable
from xarch.modules.rules.domain.values import SourceFile


class SourceTree(Protocol):
    """The source files below a root folder, listed, then read already parsed."""

    def absent(self, roots: Iterable[Path]) -> list[Path]:
        """The roots that are no folder, in the order given."""
        ...

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        """The path below root of every source file, sorted."""
        ...

    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised."""
        ...

    def existing(self, paths: Iterable[Path]) -> frozenset[Path]:
        """The paths at which a file or a folder is."""
        ...

    def text(self, path: Path) -> str | None:
        """The text of any file at path, None when there is no file there."""
        ...

    def parsed(self, text: str) -> SourceFile:
        """A source text of the app's language that is in no file, parsed as a file of it is; one that does not parse
        holds its error."""
        ...

    def resolved(self, path: Path) -> Path:
        """The path in full, from the working folder when it is relative, every link followed: the folder a path
        given on the command line names."""
        ...
