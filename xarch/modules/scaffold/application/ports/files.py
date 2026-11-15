from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Files(Protocol):
    """Where the skeleton is written."""

    def kind(self, path: Path) -> str | None:
        """FOLDER for a folder, FILE for anything else that is there, None when nothing is."""
        ...

    def lay_down(self, path: Path, content: str | bytes) -> None:
        """Write a file, creating the folders above it: empty text makes an empty file, other text is written as text,
        bytes as they are."""
        ...

    def pyproject(self, start: Path) -> tuple[Path, str] | None:
        """The nearest pyproject.toml in start or a folder above it, with its text, or None."""
        ...
