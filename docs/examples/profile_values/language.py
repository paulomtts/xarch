from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Language:
    name: str
    extension: str
    facts: frozenset[str] = field(default_factory=frozenset)
    approximate: frozenset[str] = field(default_factory=frozenset)
    standard_names: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.extension.startswith("."):
            raise ValueError(f"language {self.name!r}: an extension starts with '.', not {self.extension!r}")
        if not self.approximate <= self.facts:
            raise ValueError(f"language {self.name!r}: a fact supplied approximately is a fact it supplies")

    def reads(self, file: str) -> bool:
        return file.endswith(self.extension)
