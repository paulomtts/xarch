from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ProfileOutput(Protocol):
    """Where a converted profile and its files are written."""

    def exists(self, path: Path) -> bool:
        """Whether a file or folder is at path."""
        ...

    def write(self, path: Path, data: bytes) -> None:
        """Write a file, creating the folders above it."""
        ...
