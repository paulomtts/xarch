from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tier:
    name: str
    proves: str
    litmus: str
    must_import: tuple[str, ...] = ()
    types_only: tuple[str, ...] = ()
    apply_forbidden: bool = False
    folder: str = ""

    def __post_init__(self) -> None:
        if not self.proves.strip():
            raise ValueError(f"tier {self.name!r} says nothing it proves")
        if self.folder and "/" in self.folder:
            raise ValueError(f"tier {self.name!r}: its folder is one name below the tests, not {self.folder!r}")


@dataclass(frozen=True)
class Tiers:
    tiers: tuple[Tier, ...]

    def named(self, name: str) -> Tier | None:
        return next((tier for tier in self.tiers if tier.name == name), None)
