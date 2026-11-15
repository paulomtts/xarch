"""In-memory implementations of the modules' filesystem ports. Not adapters: test doubles only."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.modules.rules.domain.values import Import, SourceFile


class FakeSourceTree:
    """Satisfies rules' SourceTree: root folders holding already-parsed source files, each given as its imports or
    as a whole SourceFile (whose name and path are filled in), by its path below the root."""

    def __init__(self, root: Path, files: dict[str, list[Import] | SourceFile],
                 more: dict[Path, dict[str, list[Import] | SourceFile]] | None = None):
        self._trees = {root: files, **(more or {})}
        self.read_paths: list[tuple[str, ...]] = []

    def is_dir(self, root: Path) -> bool:
        return root in self._trees

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        return [tuple(rel.split("/")) for rel in sorted(self._trees[root])]

    def read(self, root: Path, paths: list[tuple[str, ...]]) -> list[SourceFile]:
        self.read_paths += paths
        files = self._trees[root]
        return [_source(f"{root.name}/{'/'.join(path)}", path, files["/".join(path)]) for path in paths]


def _source(name: str, path: tuple[str, ...], given: list[Import] | SourceFile) -> SourceFile:
    if isinstance(given, SourceFile):
        return replace(given, name=name, path=path)
    return SourceFile(name, path, tuple(given))


class FakeDisk:
    """Satisfies layout's Disk: a fixed set of folders and files."""

    def __init__(self, dirs: set[Path] = frozenset(), files: set[Path] = frozenset()):
        self._dirs, self._files = set(dirs), set(files)

    def is_dir(self, path: Path) -> bool:
        return path in self._dirs

    def is_file(self, path: Path) -> bool:
        return path in self._files

    def subdirectories(self, path: Path) -> list[str]:
        return [d.name for d in self._dirs if d.parent == path]

    def folders(self, path: Path) -> list[tuple[str, ...]]:
        return sorted(d.relative_to(path).parts for d in self._dirs if d != path and d.is_relative_to(path))


class FakeFiles:
    """Satisfies scaffold's Files: remembers every path that exists and every file it was asked to create."""

    def __init__(self, existing: set[Path] = frozenset(), texts: dict[Path, str] | None = None):
        self.existing: set[Path] = set()
        for path in {*existing, *(texts or {})}:
            self.existing.update([path, *path.parents])
        self.created: list[Path] = []
        self.texts: dict[Path, str] = {}
        self._given = dict(texts or {})

    def exists(self, path: Path) -> bool:
        return path in self.existing

    def is_dir(self, path: Path) -> bool:
        return path in self.existing and any(p.parent == path for p in self.existing)

    def create_empty(self, path: Path) -> None:
        self.existing.update([path, *path.parents])
        self.created.append(path)

    def write_text(self, path: Path, text: str) -> None:
        if path in self.existing:
            self.texts[path] = text
            return
        self.create_empty(path)
        self.texts[path] = text

    def read_text(self, path: Path) -> str:
        return self.texts.get(path, self._given.get(path, ""))

    def find_upward(self, start: Path, name: str) -> Path | None:
        for folder in [start, *start.parents]:
            if folder / name in self.existing:
                return folder / name
        return None
