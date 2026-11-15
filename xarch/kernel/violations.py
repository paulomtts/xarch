"""A finding at a place in a file tree. No business meaning: what was found is in the message."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    """file and line (0: the file as a whole) say where; message what was found, as a sentence. rule is the stable id
    of the check that found it, and fix, when the check knows one, a short instruction that removes it."""
    file: str
    line: int
    message: str
    rule: str
    fix: str | None = None

    def __str__(self) -> str:
        where = f"{self.file}:{self.line}" if self.line else self.file
        return f"{where}: {self.message}"
