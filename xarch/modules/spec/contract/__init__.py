"""What the spec module publishes: the skeleton of a profile as flat lists of entries, and which profile is in force."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from xarch.kernel.logic.language import LanguageView
from xarch.kernel.logic.origin import Origin
from xarch.kernel.logic.placement import Excluded, Repeat, Target
from xarch.kernel.logic.project_file import ProjectFile
from xarch.kernel.logic.testing import Fakes, Framework, ScenarioCoverage, StandIns, TierView

__all__ = ["Entry", "Repeating", "Skeleton", "DocFile", "Docs", "ProjectFiles", "FilesResult", "OriginResult", "PartView",
           "GuardsView", "ProfileView", "ChooseApp", "AppChosen", "ChooseAppResult",
           "SelectProfile", "ProfileSelected", "ProfileRefused",
           "NoProfileChosen", "SelectResult", "MigrateProfile", "MigratedFile", "Migrated", "MigrationRefused",
           "MigrateResult", "Shown", "Symbol", "Explain", "FormatExplained", "KeyExplained", "UnknownKey",
           "ExplainResult", "ViewProfile", "ProfileViewed", "ViewResult", "CheckProfile", "LOAD", "EXAMPLES", "Problem", "ProfileChecked",
           "CheckResult", "NewProfile", "ProfileCreated", "NewResult"]


@dataclass(frozen=True)
class Entry:
    """
    path: a folder or a file of the layout, e.g. ("application", "controller<ending>")
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
    none); package_file, the file the language of the app has stand for each folder, which a folder of the layout holds;
    language, how the language of the app is named; reserved, the words no name may be."""
    top_level: tuple[Entry, ...]
    repeating: tuple[Repeating, ...]
    entry_point: str
    package_file: str = ""
    language: str = ""
    reserved: frozenset[str] = frozenset()


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
class ProjectFiles:
    """The files a profile has `init` write beside an app folder, besides the docs, in the profile's order."""
    files: tuple[ProjectFile, ...]


@dataclass(frozen=True)
class PartView:
    """One part of a profile as a check reads it: its name; its path as a pattern, `*` standing for the instance of a
    repeating folder; what it may import besides itself; its role, litmus test, how the docs name it (shown) and why no
    tier tests it; the names it may not use; what each of its files must import one of; what its files define
    (holds); the parts it may use as types only; whether it calls none of its own parameters; the patterns its public
    classes match; and the parts that alone may build its classes."""
    name: str
    pattern: tuple[str, ...]
    may_import: tuple[Target, ...]
    role: str = ""
    litmus: str = ""
    shown: str = ""
    untested: str = ""
    forbidden: tuple[tuple[str, ...], ...] = ()
    must_import: tuple[Target, ...] = ()
    holds: str = ""
    types_only: tuple[str, ...] = ()
    no_callbacks: bool = False
    names: tuple[str, ...] = ()
    built_by: tuple[str, ...] = ()


@dataclass(frozen=True)
class GuardsView:
    """The guards a profile switches on, None or False when off: the package-only parts, scenario coverage, no
    comments, stand-ins, the closed tree, the fewest statements of a duplicate, the fewest fields of a twin, dead code
    (and with it the files no test of their tier reaches), the parts whose forwarding methods are listed, and private
    imports."""
    package_only: tuple[str, ...] = ()
    scenarios: ScenarioCoverage | None = None
    no_comments: bool = False
    stand_ins: StandIns | None = None
    closed_tree: bool = False
    no_duplicates: int | None = None
    no_twins: int | None = None
    dead_code: bool = False
    untested: bool = False
    pass_through: tuple[str, ...] = ()
    private_imports: bool = False


@dataclass(frozen=True)
class ProfileView:
    """A profile as the checks read it, everything they need already worked out: its parts in order; every folder of
    the layout as a pattern; its tiers in order; the outside packages each part may import (None: unchecked); its
    repeating folders; the guards switched on; the fakes and the test framework (None: none); the excluded folders;
    the project's own advice for a rule, by rule id; the language of the app; and the standard-library modules a
    part imports only when its libraries list them, each with why."""
    parts: tuple[PartView, ...]
    folders: tuple[tuple[str, ...], ...] = ()
    tiers: tuple[TierView, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    repeats: tuple[Repeat, ...] = ()
    guards: GuardsView = GuardsView()
    fakes: Fakes | None = None
    framework: Framework | None = None
    excluded: tuple[Excluded, ...] = ()
    hints: dict[str, str] = field(default_factory=dict)
    language: LanguageView = LanguageView()
    reserved: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ChooseApp:
    """Choose the app folder to work on: given (from --app), else the one the project around the folder start
    records, else the default one."""
    start: Path
    given: Path | None = None


@dataclass(frozen=True)
class AppChosen:
    app: Path


@dataclass(frozen=True)
class SelectProfile:
    """Choose the architecture for an app folder, whose project's pyproject.toml may configure it: override is an
    explicit choice (from --profile), tests an explicit tests root (from --tests)."""
    app: Path
    override: str | None = None
    tests: Path | None = None


@dataclass(frozen=True)
class ProfileSelected:
    """The architecture in force, as a bundled name or a path, and the tests root chosen: the one asked for, else the
    one configured, else tests/ beside the app folder when there is one (None: none)."""
    name: str
    tests: Path | None = None


@dataclass(frozen=True)
class ProfileRefused:
    """A refusal; reason is safe to show the user as-is."""
    reason: str


@dataclass(frozen=True)
class NoProfileChosen:
    """No profile was asked for and the project configures none, so none is in force; known: the bundled profiles,
    one of which may be asked for."""
    known: tuple[str, ...]


FilesResult = ProjectFiles | ProfileRefused
OriginResult = Origin | ProfileRefused
SelectResult = ProfileSelected | NoProfileChosen | ProfileRefused
ChooseAppResult = AppChosen | ProfileRefused


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
    """The whole format: version, the keys as a tree (shape), the symbols, and the smallest valid profile (as text)."""
    version: int
    shape: tuple[Shown, ...]
    symbols: tuple[Symbol, ...]
    smallest: str


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


ViewResult = ProfileViewed | NoProfileChosen | ProfileRefused


@dataclass(frozen=True)
class CheckProfile:
    """Validate a profile without an app: target as for ViewProfile."""
    app: Path
    target: str | None = None


LOAD, EXAMPLES = "load", "examples"
"""The checks a Problem names: the loader, which finds every problem at once, and the examples' imports."""


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
    origin: Origin | None

    @property
    def ok(self) -> bool:
        return not self.problems


CheckResult = ProfileChecked | NoProfileChosen | ProfileRefused


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
