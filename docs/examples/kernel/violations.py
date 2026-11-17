from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Place:
    file: str
    line: int = 0

    def __post_init__(self) -> None:
        if self.line < 0:
            raise ValueError(f"{self.file}: a line is 1 or more, or 0 for the whole file")

    def shown(self) -> str:
        return f"{self.file}:{self.line}" if self.line else self.file


@dataclass(frozen=True)
class Violation:
    place: Place
    rule: str
    message: str
    fix: str

    def __post_init__(self) -> None:
        if not self.fix.strip():
            raise ValueError(f"a violation of {self.rule!r} at {self.place.shown()} says nothing to do about it")
