from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.kernel.errors import DomainError


class UnknownProfile(DomainError):
    def __init__(self, name: str, known: Iterable[str], source: Path | None = None):
        where = f" in {source}" if source else ""
        super().__init__(f"unknown profile '{name}'{where}: use one of {', '.join(known)}")


class NoProfile(DomainError):
    def __init__(self, known: Iterable[str]):
        super().__init__("no profile: pass --profile, or set `profile` under [tool.xarch] in pyproject.toml; "
                         f"the profiles found are {', '.join(known)}")


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
    """A profile that `xarch profile migrate` cannot convert, or whose conversion cannot be written; reason says why."""
