"""What the scaffold module promises: build the skeleton, never overwriting a file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Init:
    """Build the top level of the architecture at a location (a bundled name or a path) below root; cwd is the working
    folder, in full, that a relative root or location is read from."""
    root: Path
    profile: str
    cwd: Path


@dataclass(frozen=True)
class New:
    """Build one instance, called name, of a kind: a folder of the layout that declares `each:`, by its path."""
    root: Path
    kind: str
    name: str
    profile: str


@dataclass
class Report:
    """What was created, what existing file was updated, and what already existed and was left alone."""
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class Scaffolded:
    report: Report


@dataclass(frozen=True)
class Refused:
    """A refusal; reason is safe to show the user as-is."""
    reason: str


NewResult = Scaffolded | Refused
