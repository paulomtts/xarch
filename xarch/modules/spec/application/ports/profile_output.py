from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Protocol


class ProfileOutput(Protocol):
    """Where a new or converted profile and its files are written."""

    def taken(self, folder: Path, names: Iterable[str]) -> list[Path]:
        """The files of names, paths in folder, that something is at already, in the order given."""
        ...

    def write(self, folder: Path, outputs: Mapping[str, bytes]) -> None:
        """Write each file at its path in folder, creating the folders above it."""
        ...
