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

    def breaks(self, profile: str, app: str, files: tuple[tuple[str, str], ...],
               root: Path | None = None) -> tuple[tuple[str, ...], ...]:
        """For each file given, by its path below the app with its text, in the order given, the parts whose `holds`
        it would break were it to lie there, in the profile's order (its own part among them when it breaks that one):
        read with the other files of the app at root (None: as a small project of the files given alone), the app
        being the package named app; raises Refused for a profile that cannot be used."""
        ...
