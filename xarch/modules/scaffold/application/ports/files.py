from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Files(Protocol):
    """Where the skeleton is written."""

    def exists(self, path: Path) -> bool: ...

    def is_dir(self, path: Path) -> bool: ...

    def create_empty(self, path: Path) -> None:
        """Create an empty file, and the folders above it."""
        ...

    def write_text(self, path: Path, text: str) -> None:
        """Write a file holding text, creating the folders above it."""
        ...

    def read_text(self, path: Path) -> str: ...

    def find_upward(self, start: Path, name: str) -> Path | None:
        """The nearest file called name in start or a folder above it, or None."""
        ...
