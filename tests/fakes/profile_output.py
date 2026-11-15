"""In-memory implementation of spec's ProfileOutput port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path


class FakeProfileOutput:
    """Satisfies spec's ProfileOutput: the paths that already exist, and everything written, by path."""

    def __init__(self, existing: set[Path] | None = None):
        self._existing = set(existing or ())
        self.written: dict[Path, bytes] = {}

    def exists(self, path: Path) -> bool:
        return path in self._existing or path in self.written

    def write(self, path: Path, data: bytes) -> None:
        self.written[path] = data
