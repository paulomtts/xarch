"""What the spec module publishes: the skeleton of a profile as flat lists of entries, and which profile is in force."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.spec.domain.values import (
    Architecture,
    CaseTable,
    ClosedTree,
    Fixture,
    Framework,
    NoComments,
    PackageOnly,
    Part,
    ScenarioCoverage,
    StandIns,
    Subject,
    Target,
    Tier,
    TierExample,
)

__all__ = ["Architecture", "CaseTable", "ClosedTree", "Fixture", "Framework", "NoComments", "PackageOnly", "Part",
           "ScenarioCoverage", "StandIns", "Subject", "Target", "Tier", "TierExample", "Entry", "Skeleton", "DocFile",
           "Docs", "ProjectFile", "Loosened", "ProfileOrigin", "SelectProfile", "ProfileSelected", "ProfileRefused",
           "ProfileResult"]


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
class ProjectFile:
    """A file `init` writes beside the app folder, in the folder holding it.

    path: below the folder holding the app, e.g. ("tests", "architecture", "test_rules.py"); a file inside the app
        folder starts with the app folder's name
    content: the file's text, the app folder's name filled in, or, for a file that is not filled, its bytes as they are
    pinned: the project keeps it as written; `check` reports it when it differs
    preset: it comes from a folder entry of the profile
    """
    path: tuple[str, ...]
    content: str | bytes
    pinned: bool = False
    preset: bool = False


@dataclass(frozen=True)
class Loosened:
    """One way a profile is looser than the bundled profile it is compared with. key is what loosened:

        rules           part may also import what (a target as written)
        libraries       part may also import the outside package what; with no part, outside packages are unchecked
        forbidden       part no longer forbids what
        untested        part is newly marked untested
        types_only      the tests of tier part may now call what
        tier_forbidden  the tests of tier part are no longer held to their part's forbidden list
        skips           what is no longer counted as a skip
        pinned          the init file what is no longer pinned
    """
    key: str
    part: str
    what: str = ""


@dataclass(frozen=True)
class ProfileOrigin:
    """Where a profile comes from and how far it can be trusted. location: as selected, a bundled name or a path;
    closest: for a custom file, the bundled profile sharing the most parts (the first by name on a tie), None when it
    is bundled or shares none; guards_off: the guards xarch has that it leaves off, in xarch's order; baseline_off:
    those the bundled profile it is, or is compared with, leaves off too; looser: how it is looser than closest."""
    location: str
    bundled: bool
    closest: str | None
    guards_off: tuple[str, ...]
    baseline_off: tuple[str, ...]
    looser: tuple[Loosened, ...]


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
