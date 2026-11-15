"""In-memory implementation of rules' Structure port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.kernel.violations import Violation


class FakeStructure:
    """Satisfies rules' Structure: the same violations for any app folder (none unless given)."""

    def __init__(self, violations: list[Violation] | None = None):
        self._violations = list(violations or [])

    def violations(self, root: Path, package: str, profile: str, tests: Path | None) -> list[Violation]:
        return list(self._violations)
