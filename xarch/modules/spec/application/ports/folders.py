from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol


class Folders(Protocol):
    """Which folders of the project around an app folder there are, and which folder a relative path is read from."""

    def existing(self, folders: Iterable[Path]) -> tuple[Path, ...]:
        """Those of folders that are folders, in the order given."""
        ...

    def working_folder(self) -> Path:
        """The folder a relative path given on the command line is read from, in full."""
        ...
