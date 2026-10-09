"""In-memory implementations of the modules' filesystem ports. Not adapters: test doubles only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.rules.domain.values import Import, SourceFile


class FakeSourceTree:
    """Satisfies rules' SourceTree: a root folder holding already-parsed source files."""

    def __init__(self, root: Path, files: dict[str, list[Import]]):
        self._root = root
        self._files = files

    def is_dir(self, root: Path) -> bool:
        return root == self._root

    def read(self, root: Path) -> list[SourceFile]:
        return [SourceFile(f"{root.name}/{rel}", tuple(rel.split("/")), tuple(imports))
                for rel, imports in sorted(self._files.items())]


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


class FakeFiles:
    """Satisfies scaffold's Files: remembers every path that exists and every file it was asked to create."""

    def __init__(self, existing: set[Path] = frozenset()):
        self.existing: set[Path] = set()
        for path in existing:
            self.existing.update([path, *path.parents])
        self.created: list[Path] = []
        self.texts: dict[Path, str] = {}

    def exists(self, path: Path) -> bool:
        return path in self.existing

    def is_dir(self, path: Path) -> bool:
        return path in self.existing and any(p.parent == path for p in self.existing)

    def create_empty(self, path: Path) -> None:
        self.existing.update([path, *path.parents])
        self.created.append(path)

    def write_text(self, path: Path, text: str) -> None:
        self.create_empty(path)
        self.texts[path] = text
