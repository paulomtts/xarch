"""What the scaffold module promises: build the skeleton, never overwriting a file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Init:
    root: Path
    profile: str = "cli"           # the skeleton profile to build


@dataclass(frozen=True)
class NewModule:
    root: Path
    name: str
    profile: str = "cli"


@dataclass
class Report:
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class Scaffolded:
    report: Report


@dataclass(frozen=True)
class Refused:
    reason: str                    # safe to show the user as-is


NewModuleResult = Scaffolded | Refused
