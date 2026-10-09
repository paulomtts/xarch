"""A finding at a place in a file tree. No business meaning: what was found is in the message."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    file: str
    line: int
    message: str

    def __str__(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        return f"{where}: {self.message}"
