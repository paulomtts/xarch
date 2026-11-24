from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.parsed import SourceFile
from xarch.profile_values.language import InterfaceMark, RecordMark
from xarch.profile_values.testing import TableForm, TestForm


class SourceTree(Protocol):
    """The source files below a root folder, listed, then read already parsed."""

    def absent(self, roots: Iterable[Path]) -> list[Path]:
        """The roots that are no folder, in the order given."""
        ...

    def paths(self, root: Path, extensions: tuple[str, ...]) -> list[tuple[str, ...]]:
        """The path below root of every source file, a file whose name ends in one of extensions, each once, sorted."""
        ...

    def read(self, root: Path, paths: list[tuple[str, ...]], tables: tuple[TableForm, ...] = (),
             immutable: tuple[RecordMark, ...] = (), interface: tuple[InterfaceMark, ...] = (), *,
             standard: frozenset[str], private: str, special: str, declared: tuple[TestForm, ...] = (),
             globals: tuple[tuple[str, ...], ...] = ()) -> list[SourceFile]:
        """The files at paths below root, parsed; one that does not parse holds its error. A function holds the
        tables written in one of the forms `tables` holds, each tagged with the index of its form; with none, no
        table is recognised. A file holds a test for each function whose name matches the pattern of a function form
        `declared` holds, tagged with the index of the first such form; with none, it holds no test. A use or a call
        of a bare name the file does not bind that is the first step of one of `globals` is read as that bare name,
        never as one of the language's predefined names. A class is an immutable record
        when one of the marks `immutable` holds marks it so, and an interface when one of the marks `interface` holds
        marks it so. An absolute import is of the standard library when its first step is one of the modules
        `standard` holds; a relative one never is. A name is public unless it starts with `private`, how the
        language starts a private name ("": every name is public). A class is a record when every method's name
        matches `special` in full, a regular expression ("": no name is special), and a top-level function of its
        file names it in its return annotation."""
        ...

    def existing(self, paths: Iterable[Path]) -> frozenset[Path]:
        """The paths at which a file or a folder is."""
        ...

    def text(self, path: Path) -> str | None:
        """The text of any file at path, None when there is no file there."""
        ...

    def parsed(self, text: str, standard: frozenset[str], *, private: str, special: str) -> SourceFile:
        """A source text of the app's language that is in no file, parsed as a file of it is, an absolute import of
        the standard library when its first step is one of the modules `standard` holds, a name public unless it
        starts with `private`, a class a record as `special` says (see read); one that does not parse holds its
        error."""
        ...

    def resolved(self, folder: Path, path: Path) -> Path:
        """The path, read from folder (given in full) when it is relative, in full with every link followed and every
        `..` taken."""
        ...
