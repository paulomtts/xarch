from __future__ import annotations

from dataclasses import dataclass, field

from app.kernel.violations import Place


@dataclass(frozen=True)
class ImportRule:
    part: str
    allowed: frozenset[str] = field(default_factory=frozenset)
    everything: bool = False

    def __post_init__(self) -> None:
        if self.everything and self.allowed:
            raise ValueError(f"part {self.part!r} may import everything, so it lists no part besides")
        if self.part in self.allowed:
            raise ValueError(f"part {self.part!r} imports its own files freely and does not list itself")

    def allows(self, target: str) -> bool:
        return self.everything or target == self.part or target in self.allowed


@dataclass(frozen=True)
class ImportSeen:
    place: Place
    importer: str
    target: str

    def __post_init__(self) -> None:
        if not self.target:
            raise ValueError(f"{self.place.shown()}: an import names what it imports")
