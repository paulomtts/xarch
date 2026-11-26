from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.published import Recorded


class Baselines(Protocol):
    """The record of the baseline: the violations a project had when it adopted xarch, each with how many."""

    def read(self, record: Path) -> tuple[Recorded, ...] | None:
        """The findings recorded in the file at record; None when there is none."""
        ...

    def write(self, record: Path, findings: tuple[Recorded, ...]) -> None:
        """Record the findings in the file at record, in place of what it held."""
        ...
