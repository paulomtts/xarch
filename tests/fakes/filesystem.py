"""In-memory implementations of the modules' filesystem ports. Not adapters: test doubles only."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.modules.rules.domain.values import Import, SourceFile, TableForm


class FakeSourceTree:
    """Satisfies rules' SourceTree: root folders holding already-parsed source files, each given as its imports or
    as a whole SourceFile (whose name and path are filled in), by its path below the root; and the text of any other
    file, by its path."""

    def __init__(self, root: Path, files: dict[str, list[Import] | SourceFile],
                 more: dict[Path, dict[str, list[Import] | SourceFile]] | None = None,
                 texts: dict[Path, str] | None = None):
        self._trees = {root: files, **(more or {})}
        self._texts = dict(texts or {})

    def is_dir(self, root: Path) -> bool:
        return root in self._trees

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        return [tuple(rel.split("/")) for rel in sorted(self._trees[root])]

    def read(self, root: Path, paths: list[tuple[str, ...]], table: TableForm | None = None) -> list[SourceFile]:
        files = self._trees[root]
        return [_source(f"{root.name}/{'/'.join(path)}", path, files["/".join(path)]) for path in paths]

    def text(self, path: Path) -> str | None:
        return self._texts.get(path)

    def exists(self, path: Path) -> bool:
        held = [root / rel for root, files in self._trees.items() for rel in files] + list(self._texts)
        return any(path == file or path in file.parents for file in held)


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
    """Satisfies scaffold's Files: the files that exist (the folders above them exist too), the folders that exist
    though empty, and the text of a file, as the real filesystem holds them; a file created empty reads as "", and
    reading a file that does not exist raises FileNotFoundError, as the real one does."""

    def __init__(self, existing: set[Path] = frozenset(), texts: dict[Path, str] | None = None,
                 dirs: set[Path] = frozenset()):
        self.files: set[Path] = {*existing, *(texts or {})}
        self.dirs: set[Path] = {*dirs, *(parent for path in {*self.files, *dirs} for parent in path.parents)}
        self.created: list[Path] = []
        self.texts: dict[Path, str] = {}
        self.data: dict[Path, bytes] = {}
        self._given = dict(texts or {})

    def exists(self, path: Path) -> bool:
        return path in self.files or path in self.dirs

    def is_dir(self, path: Path) -> bool:
        return path in self.dirs

    def create_empty(self, path: Path) -> None:
        self._add(path)
        self.created.append(path)

    def write_text(self, path: Path, text: str) -> None:
        if path not in self.files:
            self.create_empty(path)
        self.texts[path] = text

    def write_bytes(self, path: Path, data: bytes) -> None:
        self.create_empty(path)
        self.data[path] = data

    def read_text(self, path: Path) -> str:
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.texts.get(path, self._given.get(path, ""))

    def find_upward(self, start: Path, name: str) -> Path | None:
        for folder in [start, *start.parents]:
            if folder / name in self.files:
                return folder / name
        return None

    def _add(self, path: Path) -> None:
        self.files.add(path)
        self.dirs.update(path.parents)
