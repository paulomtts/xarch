"""The local filesystem, in plain paths and strings. Knows no module."""
from __future__ import annotations

from pathlib import Path


class FileSystem:
    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    def is_file(self, path: Path) -> bool:
        return path.is_file()

    def subdirectories(self, path: Path) -> list[str]:
        """Names of the folders directly inside path, or [] if path is not a folder."""
        if not path.is_dir():
            return []
        return [p.name for p in path.iterdir() if p.is_dir()]

    def folders(self, path: Path) -> list[tuple[str, ...]]:
        """Every folder below path, at any depth, as its path below it, sorted; [] if path is not a folder."""
        if not path.is_dir():
            return []
        return sorted(p.relative_to(path).parts for p in path.rglob("*") if p.is_dir())

    def find_upward(self, start: Path, name: str) -> Path | None:
        """The nearest file called name in start or a folder above it (start made absolute first), or None."""
        here = start.absolute()
        for folder in [here, *here.parents]:
            if (folder / name).is_file():
                return folder / name
        return None

    def files(self, root: Path, pattern: str) -> list[Path]:
        """Every file below root matching the glob pattern, sorted."""
        return sorted(root.rglob(pattern))

    def files_below(self, path: Path) -> list[str]:
        """Every file below path, at any depth, as its path below it written with `/`, sorted; [] if path is not a
        folder."""
        if not path.is_dir():
            return []
        return sorted(p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file())

    def read_text(self, path: Path) -> str:
        return path.read_text()

    def read_bytes(self, path: Path) -> bytes:
        return path.read_bytes()

    def create_empty(self, path: Path) -> None:
        self.write_text(path, "")

    def write_text(self, path: Path, text: str) -> None:
        """Write text to path, creating the folders above it."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def write_bytes(self, path: Path, data: bytes) -> None:
        """Write data to path, creating the folders above it."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
