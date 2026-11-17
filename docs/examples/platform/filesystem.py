from __future__ import annotations

from pathlib import Path


class FileSystem:
    def read_text(self, path: Path) -> str:
        self._whole(path)
        return path.read_text(encoding="utf-8")

    def is_file(self, path: Path) -> bool:
        self._whole(path)
        return path.is_file()

    def files(self, root: Path, suffix: str) -> list[Path]:
        self._whole(root)
        return sorted(path for path in root.rglob(f"*{suffix}") if path.is_file())

    def subdirectories(self, root: Path) -> list[str]:
        self._whole(root)
        return sorted(child.name for child in root.iterdir() if child.is_dir()) if root.is_dir() else []

    @staticmethod
    def _whole(path: Path) -> None:
        if not path.is_absolute():
            raise ValueError(f"{path}: give the path in full; which folder it is read from is the caller's to say")
