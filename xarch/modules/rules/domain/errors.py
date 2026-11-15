from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError
from xarch.kernel.logic.source import Unparsable


class RootMissing(DomainError):
    def __init__(self, root: Path):
        super().__init__(f"{root} is not a directory")
        self.root = root


class OutsideProject(DomainError):
    """A path that lies outside the project: not below the folder holding the app folder."""

    def __init__(self, path: Path, project: Path):
        super().__init__(f"{path.as_posix()} lies outside the project: it is not below {project.as_posix()}")


class Unreadable(DomainError):
    """A source text that does not parse, and where and why, as the reader says it."""

    def __init__(self, found: Unparsable):
        super().__init__(f"line {found.line}: {found.message}")
        self.found = found


class ProfileUnusable(DomainError):
    """The profile in force cannot be read for what the check needs of it; reason says why, as the spec module put
    it."""
