from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.review.domain.values import Found, Reads


class Code(Protocol):
    """The app's files at the paths given, read with where the profile places each."""

    def files(self, paths: tuple[Path, ...], cwd: Path, app: Path, profile: str,
              tests: Path | None) -> Found:
        """The files at the paths, each given from cwd, from the folder holding app or from app, a folder standing for
        the files below it, each once: a source file of the app in a part read, any other left out with why; raises
        Refused for a path outside the project or a profile that cannot be used."""
        ...

    def reads(self, profile: str, app: str, asked: str, files: tuple[tuple[str, str], ...]) -> tuple[Reads, ...]:
        """What the eval of the profile's own asked reads in each file given, by its path below the app with its text,
        read as the app's files of a small project, the app being the package named app; raises Refused for an eval
        that cannot be read or a profile that cannot be used."""
        ...
