from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.review.domain.values import Found


class Code(Protocol):
    """The app's files at the paths given, read with where the profile places each."""

    def files(self, paths: tuple[Path, ...], cwd: Path, app: Path, profile: str,
              tests: Path | None) -> Found:
        """The files at the paths, each given from cwd, from the folder holding app or from app, a folder standing for
        the files below it, each once: a source file of the app in a part read, any other left out with why; raises
        Refused for a path outside the project or a profile that cannot be used."""
        ...
