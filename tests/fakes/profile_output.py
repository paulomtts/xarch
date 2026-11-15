"""In-memory implementation of spec's ProfileOutput port. Not an adapter: a test double only."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path


class FakeProfileOutput:
    """Satisfies spec's ProfileOutput: the paths that already exist, and everything written, by path."""

    def __init__(self, existing: set[Path] | None = None):
        self._existing = set(existing or ())
        self.written: dict[Path, bytes] = {}

    def taken(self, folder: Path, names: Iterable[str]) -> list[Path]:
        return [folder / name for name in names if folder / name in self._existing or folder / name in self.written]

    def write(self, folder: Path, outputs: Mapping[str, bytes]) -> None:
        self.written.update({folder / name: data for name, data in outputs.items()})
