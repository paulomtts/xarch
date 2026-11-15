"""What the spec module publishes: the skeleton of a profile as flat lists of entries, and which profile is in force."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.spec.domain.values import (Architecture, ClosedTree, NoComments, PackageOnly, Part, ScenarioCoverage,
                                              StandIns, Subject, Target, Tier, TierExample)

__all__ = ["Architecture", "ClosedTree", "NoComments", "PackageOnly", "Part", "ScenarioCoverage", "StandIns", "Subject",
           "Target", "Tier",
           "TierExample", "Entry", "Skeleton", "DocFile", "Docs",
           "SelectProfile", "ProfileSelected", "ProfileRefused", "ProfileResult"]


@dataclass(frozen=True)
class Entry:
    """
    path: e.g. ("application", "controller.py")
    leaf: a file, or a directory that holds nothing in the spec
    """
    path: tuple[str, ...]
    is_dir: bool
    leaf: bool


@dataclass(frozen=True)
class Skeleton:
    """The layout as entries: top_level below the app root, with the `each` folder's parent empty; each_root, the
    folder holding the `each` instances (None if the layout has none); each, what every instance holds; entry_point,
    the top-level folder of the part marked `entry` ("" if none)."""
    top_level: tuple[Entry, ...]
    each_root: tuple[str, ...] | None
    each: tuple[Entry, ...]
    entry_point: str


@dataclass(frozen=True)
class DocFile:
    """
    path: below the docs root, e.g. ("adrs", "0000-template.md")
    template: the text a new file starts with, filled from the profile's template
    """
    path: tuple[str, ...]
    template: str


@dataclass(frozen=True)
class Docs:
    """The project docs of a profile; folders exist because the template files inside them do.

    root: below the folder holding the app, e.g. ("docs", "project")
    """
    root: tuple[str, ...]
    files: tuple[DocFile, ...]


@dataclass(frozen=True)
class SelectProfile:
    """Choose the architecture for an app folder, whose project's pyproject.toml may configure it: override is an
    explicit choice (from --profile), tests an explicit tests root (from --tests)."""
    app: Path
    override: str | None = None
    tests: Path | None = None


@dataclass(frozen=True)
class ProfileSelected:
    """The architecture in force, as a bundled name or a path, and the tests root chosen (None: none chosen)."""
    name: str
    tests: Path | None = None


@dataclass(frozen=True)
class ProfileRefused:
    """A refusal; reason is safe to show the user as-is."""
    reason: str


ProfileResult = ProfileSelected | ProfileRefused
