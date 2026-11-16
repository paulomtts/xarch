from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path

from xarch.kernel.errors import DomainError


class UnknownProfile(DomainError):
    def __init__(self, name: str, known: Iterable[str], source: Path | None = None):
        where = f" in {source}" if source else ""
        super().__init__(f"unknown profile '{name}'{where}: use one of {', '.join(known)}")


class NoProfile(DomainError):
    """No profile was asked for, and the project configures none; known: the bundled profiles."""

    def __init__(self, known: Iterable[str]):
        self.known = tuple(known)
        super().__init__(f"no profile: none is asked for or configured; the profiles found are {', '.join(self.known)}")


class UnreadableSettings(DomainError):
    def __init__(self, source: Path, why: str):
        super().__init__(f"cannot read {source}: {why}")


class InvalidArchitecture(DomainError):
    """An architecture file that cannot be read or does not describe a valid architecture.

    problems holds every problem found, each prefixed by the file it is in; reason is them one per line.
    """

    def __init__(self, source: str, problems: Iterable[str]):
        self.source = source
        self.problems = tuple(f"{source}: {problem}" for problem in problems)
        super().__init__("\n".join(self.problems))


class InvalidTemplate(DomainError):
    """A docs template that cannot be filled from its architecture; problems holds every problem, prefixed as above."""

    def __init__(self, source: str, problems: Iterable[str]):
        self.source = source
        self.problems = tuple(f"{source}: {problem}" for problem in problems)
        super().__init__("\n".join(self.problems))


class UnmigratableProfile(DomainError):
    """A profile that its migration cannot convert, or whose conversion cannot be written; reason says why."""


class NewProfileRefused(DomainError):
    """A copy of a bundled profile that cannot be written, as asked; reason says why and what to do."""


class WouldOverwrite(DomainError):
    """Files a profile would be written to that something is at already, in the order written: nothing is written."""

    def __init__(self, taken: Sequence[Path]):
        self.taken = tuple(taken)
        super().__init__(f"{', '.join(path.as_posix() for path in self.taken)} already exist")
