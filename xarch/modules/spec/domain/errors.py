from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from xarch.kernel.errors import DomainError


class UnknownProfile(DomainError):
    def __init__(self, name: str, known: Iterable[str], source: Path | None = None):
        where = f" in {source}" if source else ""
        super().__init__(f"unknown profile '{name}'{where}: use one of {', '.join(known)}")


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
