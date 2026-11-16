from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.review.domain.values import Calibration


class Calibrations(Protocol):
    """The record of the evals of the profile's own held to their examples, in a file the project commits, by id."""

    def get(self, record: Path) -> dict[str, Calibration]:
        """The evals recorded in the file, by id; none when there is no file, or none that can be read, and an entry
        that cannot be read is left out."""
        ...

    def put(self, record: Path, held: dict[str, Calibration]) -> None:
        """Record the evals in the file, by id, in place of what it held, creating its folder."""
        ...
