"""In-memory implementations of the modules' filesystem ports. Not adapters: test doubles only."""
from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import replace
from pathlib import Path

from xarch.kernel.logic.testing import CaseTable
from xarch.kernel.source import Import
from xarch.modules.layout.domain.structure import Requirement
from xarch.modules.rules.domain.values import SourceFile
from xarch.modules.scaffold.domain.values import FILE, FOLDER


class FakeSourceTree:
    """Satisfies rules' SourceTree: root folders holding already-parsed source files, each given as its imports or
    as a whole SourceFile (whose name and path are filled in), by its path below the root; the text of any other
    file, by its path; and what a text that is in no file parses to, by the text."""

    def __init__(self, root: Path, files: dict[str, list[Import] | SourceFile],
                 more: dict[Path, dict[str, list[Import] | SourceFile]] | None = None,
                 texts: dict[Path, str] | None = None, parsed: dict[str, list[Import] | SourceFile] | None = None):
        self._trees = {root: files, **(more or {})}
        self._texts, self._parsed = dict(texts or {}), dict(parsed or {})

    def absent(self, roots: Iterable[Path]) -> list[Path]:
        return [root for root in roots if root not in self._trees]

    def paths(self, root: Path, extension: str) -> list[tuple[str, ...]]:
        return [tuple(rel.split("/")) for rel in sorted(self._trees[root])]

    def read(self, root: Path, paths: list[tuple[str, ...]], table: CaseTable | None = None) -> list[SourceFile]:
        files = self._trees[root]
        return [_source(f"{root.name}/{'/'.join(path)}", path, files["/".join(path)]) for path in paths]

    def text(self, path: Path) -> str | None:
        return self._texts.get(path)

    def existing(self, paths: Iterable[Path]) -> frozenset[Path]:
        held = [root / rel for root, files in self._trees.items() for rel in files] + list(self._texts)
        return frozenset(path for path in paths if any(path == file or path in file.parents for file in held))

    def resolved(self, folder: Path, path: Path) -> Path:
        return folder / path

    def parsed(self, text: str) -> SourceFile:
        return _source("", (), self._parsed[text])


def _source(name: str, path: tuple[str, ...], given: list[Import] | SourceFile) -> SourceFile:
    if isinstance(given, SourceFile):
        return replace(given, name=name, path=path)
    return SourceFile(name, path, tuple(given))


class FakeDisk:
    """Satisfies layout's Disk: a fixed set of folders and files."""

    def __init__(self, dirs: set[Path] = frozenset(), files: set[Path] = frozenset()):
        self._dirs, self._files = set(dirs), set(files)

    def present(self, root: Path, required: Iterable[Requirement]) -> set[Requirement]:
        return {item for item in required
                if root.joinpath(*item.path) in (self._dirs if item.is_dir else self._files)}

    def instances(self, root: Path, each: tuple[str, ...]) -> list[str]:
        base = root.joinpath(*each)
        return [d.name for d in self._dirs if d.parent == base]

    def below(self, root: Path, each: tuple[str, ...]) -> list[tuple[str, ...]]:
        base = root.joinpath(*each)
        return sorted(d.relative_to(base).parts for d in self._dirs if d != base and d.is_relative_to(base))


class FakeFiles:
    """Satisfies scaffold's Files: the files that exist (the folders above them exist too), the folders that exist
    though empty, and the content of a file, as the real filesystem holds them; a file given without a text holds ""."""

    def __init__(self, existing: set[Path] = frozenset(), texts: dict[Path, str] | None = None,
                 dirs: set[Path] = frozenset()):
        self._files: dict[Path, str | bytes] = {**{path: "" for path in existing}, **(texts or {})}
        self._dirs: set[Path] = {*dirs, *(parent for path in {*self._files, *dirs} for parent in path.parents)}

    def kind(self, path: Path) -> str | None:
        if path in self._dirs:
            return FOLDER
        return FILE if path in self._files else None

    def lay_down(self, path: Path, content: str | bytes) -> None:
        self._files[path] = content
        self._dirs.update(path.parents)

    def pyproject(self, start: Path) -> tuple[Path, str] | None:
        for folder in [start, *start.parents]:
            found = folder / "pyproject.toml"
            if found in self._files:
                return found, str(self._files[found])
        return None

    def resolved(self, folder: Path, path: Path) -> Path:
        return Path(os.path.normpath(folder / path))

    def content(self, path: Path) -> str | bytes | None:
        """What the file at path holds, or None when there is none: for reading back what was written."""
        return self._files.get(path)
