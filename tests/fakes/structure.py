"""In-memory implementation of rules' Structure port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.outcomes import StructureFound


class FakeStructure:
    """Satisfies rules' Structure: the same violations, and the same counterparts each with how many sources it read,
    for any app folder (none unless given)."""

    def __init__(self, violations: list[Violation] | None = None, counterparts: tuple[tuple[str, int], ...] = ()):
        self._violations, self._counterparts = list(violations or []), counterparts

    def checked(self, root: Path, package: str, profile: str, tests: Path | None) -> StructureFound:
        return StructureFound(tuple(self._violations), (), self._counterparts)
