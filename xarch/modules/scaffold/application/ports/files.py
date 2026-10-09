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
        """Create a file holding text, and the folders above it."""
        ...
