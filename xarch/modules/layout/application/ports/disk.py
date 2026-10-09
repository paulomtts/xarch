from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Disk(Protocol):
    """What exists below the root."""

    def is_dir(self, path: Path) -> bool: ...

    def is_file(self, path: Path) -> bool: ...

    def subdirectories(self, path: Path) -> list[str]: ...
