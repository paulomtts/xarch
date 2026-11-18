from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.review.domain.values import AcceptedFile


class Acceptances(Protocol):
    """The record of the doubtful files a person accepted, in a file the project commits, by the file as review shows
    it."""

    def get(self, record: Path) -> dict[str, AcceptedFile]:
        """The files recorded, by file; none when there is no record, and an entry that cannot be read is left out;
        raises Refused, naming the record, when it is a link or cannot be read."""
        ...

    def put(self, record: Path, accepted: dict[str, AcceptedFile]) -> None:
        """Record the files, by file, in place of those it held, creating its folder; raises Refused, naming the
        record, when it is a link, cannot be read or cannot be written."""
        ...
