from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError


class RootMissing(DomainError):
    def __init__(self, root: Path):
        super().__init__(f"{root} is not a directory")
        self.root = root


class OutsideProject(DomainError):
    """A path that lies outside the project: not below the folder holding the app folder."""

    def __init__(self, path: Path, project: Path):
        super().__init__(f"{path.as_posix()} lies outside the project: it is not below {project.as_posix()}")


class ProfileUnusable(DomainError):
    """The profile in force cannot be read for what the check needs of it; reason says why, as the spec module put
    it."""
