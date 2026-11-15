"""What the spec module publishes: the skeleton of a profile as flat lists of entries, and which profile is in force."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.spec.domain.values import (
    Architecture,
    CaseTable,
    ClosedTree,
    DeadCode,
    Fixture,
    Framework,
    NoComments,
    NoDuplicates,
    PackageOnly,
    Part,
    PassThrough,
    PrivateImports,
    Repeat,
    ScenarioCoverage,
    StandIns,
    Subject,
    Target,
    Tier,
    TierExample,
)

__all__ = ["Architecture", "CaseTable", "ClosedTree", "DeadCode", "Fixture", "Framework", "NoComments", "NoDuplicates",
           "PackageOnly", "Part", "PassThrough", "PrivateImports", "Repeat",
           "ScenarioCoverage", "StandIns", "Subject", "Target", "Tier", "TierExample", "Entry", "Repeating", "Skeleton", "DocFile",
           "Docs", "ProjectFile", "Loosened", "ProfileOrigin", "SelectProfile", "ProfileSelected", "ProfileRefused",
           "ProfileResult", "MigrateProfile", "MigratedFile", "Migrated", "MigrationRefused", "MigrateResult", "Shown",
           "Symbol", "Explain", "FormatExplained", "KeyExplained", "UnknownKey", "ExplainResult", "ViewProfile",
           "ProfileViewed", "ViewResult", "CheckProfile", "Problem", "ProfileChecked", "CheckResult", "NewProfile",
           "ProfileCreated", "NewResult"]


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
class Repeating:
    """One repeating folder of the layout: word, what one instance is called (the word between `<` and `>` in a
    path); root, the folder holding the instances; entries, what every instance holds."""
    word: str
    root: tuple[str, ...]
    entries: tuple[Entry, ...]


@dataclass(frozen=True)
class Skeleton:
    """The layout as entries: top_level below the app root, with every repeating folder empty; repeating, the
    repeating folders in the order of the profile; entry_point, the top-level folder of the part marked `entry` ("" if
    none)."""
    top_level: tuple[Entry, ...]
    repeating: tuple[Repeating, ...]
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

        may_import      part may also import what (a target as written)
        libraries       part may also import the outside package what; with no part, outside packages are unchecked
        must_import     part may also meet must_import with the target what; with no what, it has none now
        forbidden       part no longer forbids what
        untested        part is newly marked untested
        types_only      the tests of tier part may now call what
        apply_forbidden the tests of tier part are no longer held to their part's forbidden list
        testing.skips   what is no longer counted as a skip
        files.pinned    the init file what is no longer pinned
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


@dataclass(frozen=True)
class MigrateProfile:
    """Convert the profile file at path, in format 1, to format 2 in a new folder: out, else a folder beside the file
    named for it with `-v2`. dry_run: report what would be written and write nothing."""
    path: Path
    out: Path | None = None
    dry_run: bool = False


@dataclass(frozen=True)
class MigratedFile:
    """A file of the converted folder, by its path in it. source: the file next to the old profile it is read from, None
    for the converted profile; rewritten: how many `{{example:...}}` placeholders of a template were rewritten."""
    path: str
    source: str | None
    rewritten: int


@dataclass(frozen=True)
class Migrated:
    """The conversion: the folder, the converted profile, every file of the folder in the order written, what now means
    something else (changes), what has no form in format 2 and is to be written by hand (by_hand), and whether nothing
    was written because it was a dry run."""
    folder: Path
    profile: Path
    files: tuple[MigratedFile, ...]
    changes: tuple[str, ...]
    by_hand: tuple[str, ...]
    dry_run: bool


@dataclass(frozen=True)
class MigrationRefused:
    """A refusal; reason is safe to show the user as-is."""
    reason: str


MigrateResult = Migrated | MigrationRefused


@dataclass(frozen=True)
class Shown:
    """One key of the format, as a line: key is its address as a person types it (parts.may_import), depth how far
    below the keys of the file it sits."""
    key: str
    depth: int
    meaning: str
    required: bool
    enforced: bool


@dataclass(frozen=True)
class Symbol:
    symbol: str
    meaning: str


@dataclass(frozen=True)
class Explain:
    """Explain the format of a profile: the whole of it, or the key at an address such as parts.may_import."""
    key: str | None = None


@dataclass(frozen=True)
class FormatExplained:
    """The whole format: version, the keys as a tree (shape), the symbols, the smallest valid profile (as text), and
    how to go deeper."""
    version: int
    shape: tuple[Shown, ...]
    symbols: tuple[Symbol, ...]
    smallest: str
    deeper: str


@dataclass(frozen=True)
class KeyExplained:
    """One key: its address as typed, the scope it sits in, what it means and accepts, whether the profile needs it,
    whether `check` enforces it and through which rule ids, an example, what it may be set to from a list xarch ships
    (choices) and the keys it holds."""
    key: str
    where: str
    meaning: str
    accepts: str
    required: bool
    enforced: bool
    rules: tuple[str, ...]
    example: str
    choices: tuple[str, ...]
    keys: tuple[Shown, ...]


@dataclass(frozen=True)
class UnknownKey:
    """A key the format does not have, with the nearest ones that exist."""
    key: str
    nearest: tuple[str, ...]


ExplainResult = FormatExplained | KeyExplained | UnknownKey


@dataclass(frozen=True)
class ViewProfile:
    """Show a profile at a glance: the profile chosen as `select` does, from target (a bundled name or a path), else
    the one configured for the project holding app."""
    app: Path
    target: str | None = None


@dataclass(frozen=True)
class ProfileViewed:
    """A profile's folder tree (with the role of each folder) and its import table, as text; bundled: it ships with
    xarch."""
    location: str
    name: str
    tree: str
    imports: str
    bundled: bool


ViewResult = ProfileViewed | ProfileRefused


@dataclass(frozen=True)
class CheckProfile:
    """Validate a profile without an app: target as for ViewProfile."""
    app: Path
    target: str | None = None


@dataclass(frozen=True)
class Problem:
    """One thing wrong with a profile, by the check that found it: load (the loader, every problem at once, which
    includes the files it points to) or examples (an example imports what its part may not)."""
    check: str
    text: str


@dataclass(frozen=True)
class ProfileChecked:
    """What validating a profile found: its problems (none: valid), how many files it points to (when it loads), and,
    when it loads, its origin: how it differs from the bundled profile it is based on, as information."""
    location: str
    problems: tuple[Problem, ...]
    files: int
    origin: ProfileOrigin | None

    @property
    def ok(self) -> bool:
        return not self.problems


CheckResult = ProfileChecked | ProfileRefused


@dataclass(frozen=True)
class NewProfile:
    """Write a custom profile named name as a copy of the bundled profile source, with every file it points to, in
    folder out (default: architecture/<name>/ in root, the folder holding the app folder); nothing is overwritten."""
    name: str
    source: str
    root: Path
    out: Path | None = None


@dataclass(frozen=True)
class ProfileCreated:
    """The copy: its folder, its profile file, every file written (the profile first, paths relative to the folder),
    and the profile file as pyproject.toml records it, for `profile = "..."` under [tool.xarch] to put it in force."""
    folder: Path
    profile: Path
    files: tuple[str, ...]
    location: str


NewResult = ProfileCreated | ProfileRefused
