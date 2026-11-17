from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.parsed import SourceFile
from xarch.profile_values.language import RecordMark
from xarch.profile_values.testing import CaseTable


class SourceTree(Protocol):
    """The source files below a root folder, listed, then read already parsed."""

    def absent(self, roots: Iterable[Path]) -> list[Path]:
        """The roots that are no folder, in the order given."""
        ...

    def paths(self, root: Path, extension: str) -> list[tuple[str, ...]]:
        """The path below root of every source file, a file whose name ends in extension, sorted."""
        ...

    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None,
             immutable: tuple[RecordMark, ...] = ()) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in the form `table` names; with none, no table is recognised. A class is an immutable record
        when one of the marks `immutable` holds marks it so."""
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

    def resolved(self, folder: Path, path: Path) -> Path:
        """The path, read from folder (given in full) when it is relative, in full with every link followed and every
        `..` taken."""
        ...
