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
