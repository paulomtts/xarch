"""What the scaffold module promises: build the skeleton, never overwriting a file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class InitProject:
    """Build the top level of the architecture at a location (a bundled name or a path) below root; cwd is the working
    folder, in full, that a relative root or location is read from."""
    root: Path
    profile: str
    cwd: Path


@dataclass(frozen=True)
class NewInstance:
    """Build one instance, called name, of a kind: a folder of the layout that declares `each:`, by the word one
    instance of it is called."""
    root: Path
    kind: str
    name: str
    profile: str


@dataclass
class ReportView:
    """What was created, what existing file was updated, and what already existed and was left alone."""
    created: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)


@dataclass(frozen=True)
class Scaffolded:
    report: ReportView


@dataclass(frozen=True)
class Refused:
    """A refusal; reason is safe to show the user as-is."""
    reason: str


@dataclass(frozen=True)
class KindIsAFolder:
    """The folder of a kind was given in place of its word: the kind as given, and the word that names it."""
    kind: str
    word: str


@dataclass(frozen=True)
class NotInitialized:
    """The folder a new instance goes in does not exist: the skeleton that init builds is not there."""
    folder: Path


@dataclass(frozen=True)
class InstanceExists:
    """The instance to create is there already: its name, and its folder in full."""
    name: str
    folder: Path


NewResult = Scaffolded | KindIsAFolder | NotInitialized | InstanceExists | Refused
InitResult = Scaffolded | Refused
