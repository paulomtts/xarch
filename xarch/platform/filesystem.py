"""The local filesystem, in plain paths and strings. Knows no module."""
from __future__ import annotations

from pathlib import Path

HIDDEN = "."
"""How the name of a file or folder starts that the filesystem hides, such as `.cache`."""


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
        """Every folder below path, at any depth, that the filesystem shows, as its path below it, sorted: none it
        hides, such as `.cache`, nor any inside one; [] if path is not a folder."""
        if not path.is_dir():
            return []
        below = (p.relative_to(path).parts for p in path.rglob("*") if p.is_dir())
        return sorted(steps for steps in below if not any(step.startswith(HIDDEN) for step in steps))

    def find_upward(self, start: Path, name: str) -> Path | None:
        """The nearest file called name in start, given in full, or a folder above it, or None; a relative start is
        refused (ValueError), since which folder it is read from is its caller's to say."""
        if not start.is_absolute():
            raise ValueError(f"{start} is not a path in full: say which folder it is read from")
        for folder in [start, *start.parents]:
            if (folder / name).is_file():
                return folder / name
        return None

    def files(self, root: Path, pattern: str) -> list[Path]:
        """Every file below root matching the glob pattern, sorted: a folder or a dangling link that matches is not one."""
        return sorted(path for path in root.rglob(pattern) if path.is_file())

    def files_below(self, path: Path) -> list[str]:
        """Every file below path, at any depth, as its path below it written with `/`, sorted; [] if path is not a
        folder."""
        if not path.is_dir():
            return []
        return sorted(p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file())

    def real(self, path: Path) -> Path:
        """The path, given in full, with every link followed and every `..` taken; a relative path is refused
        (ValueError), since which folder it is read from is its caller's to say."""
        if not path.is_absolute():
            raise ValueError(f"{path} is not a path in full: say which folder it is read from")
        return path.resolve()

    def read_text(self, path: Path) -> str:
        """The text of the file at path, read as UTF-8; raises UnicodeDecodeError when it is not UTF-8, OSError when
        it cannot be read."""
        return path.read_text(encoding="utf-8")

    def read_bytes(self, path: Path) -> bytes:
        return path.read_bytes()

    def create_empty(self, path: Path) -> None:
        self.write_text(path, "")

    def write_text(self, path: Path, text: str) -> None:
        """Write text to path, creating the folders above it."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_bytes(self, path: Path, data: bytes) -> None:
        """Write data to path, creating the folders above it."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
