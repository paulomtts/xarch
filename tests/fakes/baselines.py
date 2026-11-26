"""In-memory implementation of rules' Baselines port. Not an adapter: a test double only."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.published import Recorded


class FakeBaselines:
    """Satisfies rules' Baselines: the records held by their path (none unless given), each write kept in their place;
    a path unreadable names raises ProfileUnusable with that reason."""

    def __init__(self, records: dict[Path, tuple[Recorded, ...]] | None = None,
                 unreadable: dict[Path, str] | None = None):
        self.records, self._unreadable = dict(records or {}), dict(unreadable or {})

    def read(self, record: Path) -> tuple[Recorded, ...] | None:
        if record in self._unreadable:
            raise ProfileUnusable(self._unreadable[record])
        return self.records.get(record)

    def write(self, record: Path, findings: tuple[Recorded, ...]) -> None:
        self.records[record] = findings
