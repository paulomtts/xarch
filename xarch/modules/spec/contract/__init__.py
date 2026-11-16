"""What the spec module publishes, each command with the Results it answers: which app folder and which profile are in
force; a profile's skeleton as flat lists of entries, its docs, the files `init` writes, the profile as the checks read
it and where it comes from; and what explaining, viewing, checking, migrating and copying a profile found."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from xarch.modules.spec.domain.published import (
    DEFAULT_APP,
    DEFAULT_TESTS,
    LITMUS,
    DocFile,
    Entry,
    Loosened,
    Origin,
    ProjectFile,
)
from xarch.profile_values.capabilities import Shortfall, Supply
from xarch.profile_values.checks import WrittenCheck
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns
from xarch.profile_values.tiers import CheckedTier

__all__ = ["DEFAULT_APP", "DEFAULT_TESTS", "Entry", "Repeating", "Skeleton", "DocFile", "Docs", "ProjectFile", "ProjectFiles",
           "FilesResult", "SkeletonResult", "ProfileResult", "DocsResult", "OriginResult", "PartView",
           "GuardsView", "ProfileView", "ChooseApp", "AppChosen", "ChooseAppResult",
           "SelectProfile", "ProfileSelected", "ProfileRefused",
           "NoProfileChosen", "SelectResult", "MigrateProfile", "MigratedFile", "Origin", "Loosened", "LITMUS",
           "Migrated", "FilesTaken", "MigrationRefused",
           "MigrateResult", "Shown", "Symbol", "Explain", "FormatExplained", "KeyExplained", "UnknownKey",
           "ExplainResult", "Need", "ViewProfile", "ProfileViewed", "ViewResult", "CheckProfile", "LOAD", "EXAMPLES",
           "Problem", "ProfileChecked",
           "CheckResult", "KnownProfiles", "NewProfile", "ProfileCreated", "NewResult", "Supply", "Shortfall"]


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
    repeating folders in the order of the profile; and what the layout and the scaffold read of the language of the
    app: how a message names it (title), the file it has stand for each folder, which a folder of the layout holds
    (package_file), how a name private to its folder starts (private), the words no name may be (reserved) and what a
    name may be in it (names, a regular expression); "" for any of them: the language does not say."""
    top_level: tuple[Entry, ...]
    repeating: tuple[Repeating, ...]
    title: str = ""
    package_file: str = ""
    private: str = ""
    reserved: frozenset[str] = frozenset()
    names: str = ""


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
    classes match; the parts that alone may build its classes; for a part there to be shared, the fewest users
    each of its public names must have; and whether every class it defines, but an exception, is an immutable
    record."""
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
    shared: int | None = None
    immutable: bool = False


@dataclass(frozen=True)
class GuardsView:
    """The guards a profile switches on, None or False when off: the package-only parts, scenario coverage, no
    comments, stand-ins, the closed tree, the fewest statements of a duplicate, the fewest fields of a twin (and of a
    renamed copy and of a partial one, and the parts whose files translate a pair, which is then no twin), dead code
    (and with it the files no test of their tier reaches), the parts whose forwarding methods are listed, and private
    imports."""
    package_only: tuple[str, ...] = ()
    scenarios: ScenarioCoverage | None = None
    no_comments: bool = False
    stand_ins: StandIns | None = None
    closed_tree: bool = False
    no_duplicates: int | None = None
    no_twins: int | None = None
    no_twins_renamed: int | None = None
    no_twins_subset: int | None = None
    no_twins_translated: tuple[str, ...] = ()
    dead_code: bool = False
    untested: bool = False
    tests_only: bool = False
    pass_through: tuple[str, ...] = ()
    private_imports: bool = False


@dataclass(frozen=True)
class ProfileView:
    """A profile as the checks read it, everything they need already worked out: its parts in order; every folder of
    the layout as a pattern; its tiers in order; the outside packages each part may import (None: unchecked); its
    repeating folders; the guards switched on; the fakes and the test framework (None: none); the excluded folders;
    the project's own advice for a rule, by rule id; the language of the app; the standard-library modules a part
    imports only when its libraries list them, each with why; the keys whose check reads a fact the language
    supplies only partly; and the checks the profile writes itself, by id, each as its slots are read (the words of
    the vocabulary in them are the rules module's to read)."""
    parts: tuple[PartView, ...]
    folders: tuple[tuple[str, ...], ...] = ()
    tiers: tuple[CheckedTier, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    repeats: tuple[Repeat, ...] = ()
    guards: GuardsView = GuardsView()
    fakes: Fakes | None = None
    framework: Framework | None = None
    excluded: tuple[Excluded, ...] = ()
    hints: dict[str, str] = field(default_factory=dict)
    language: CheckedLanguage = CheckedLanguage()
    reserved: dict[str, str] = field(default_factory=dict)
    approximate: tuple[Shortfall, ...] = ()
    checks: dict[str, WrittenCheck] = field(default_factory=dict)


@dataclass(frozen=True)
class ChooseApp:
    """Choose the app folder to work on: the one the caller gives, read from the folder start when relative, else the
    one the project around start records, else the default one in start."""
    start: Path
    given: Path | None = None


@dataclass(frozen=True)
class AppChosen:
    app: Path


@dataclass(frozen=True)
class SelectProfile:
    """Choose the architecture for an app folder, given in full, whose project's pyproject.toml may configure it:
    override is a choice the caller makes, tests a tests root the caller gives."""
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
SkeletonResult = Skeleton | ProfileRefused
ProfileResult = ProfileView | ProfileRefused
DocsResult = Docs | ProfileRefused
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
    """A file the conversion copied beside the converted profile: where it goes, the file next to the old profile it is
    read from, and how many `{{example:...}}` placeholders of a template it rewrote (placeholders)."""
    destination: str
    source: str
    placeholders: int


@dataclass(frozen=True)
class Migrated:
    """The conversion: the folder, the converted profile in it, the files copied beside it in the order written, what
    now means something else (changes), what has no form in format 2 and is to be written by hand (by_hand), and
    whether nothing was written because it was a dry run."""
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


@dataclass(frozen=True)
class FilesTaken:
    """A profile that would be written over files that exist, which are named, in the order written: nothing was
    written."""
    taken: tuple[Path, ...]


MigrateResult = Migrated | FilesTaken | MigrationRefused


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
class Need:
    """A fact of the source a key's check reads: its name, what it is, and how the default language's reader supplies
    it (None: it does not supply it, or, when the key is not graded, its data file does not say)."""
    fact: str
    meaning: str
    supply: Supply | None = None


@dataclass(frozen=True)
class KeyExplained:
    """One key: its address as typed, the scope it sits in, what it means and accepts, whether the profile needs it,
    whether `check` enforces it and through which rule ids, an example, what it may be set to from a list xarch ships
    (choices), the keys it holds, the facts of the source its check reads and the language they were graded for, and
    whether that language's data file grades the facts its reader supplies (graded); its own name, what holds it when
    it is set on each of a kind of thing (part or tier, "" for neither), and the facts it needs that the language
    supplies partly or not at all (short)."""
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
    needs: tuple[Need, ...] = ()
    language: str = ""
    graded: bool = False
    name: str = ""
    holder: str = ""
    short: tuple[Shortfall, ...] = ()


@dataclass(frozen=True)
class UnknownKey:
    """A key the format does not have, with the nearest ones that exist."""
    key: str
    nearest: tuple[str, ...]


ExplainResult = FormatExplained | KeyExplained | UnknownKey | ProfileRefused


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
    includes the files it points to) or examples (an example imports what its part may not). The checks the profile
    writes itself are held to their examples by the module that knows what their words mean."""
    check: str
    text: str


@dataclass(frozen=True)
class ProfileChecked:
    """What validating a profile found, its own checks aside: its problems (none: valid), how many files it points to
    (when it loads), and, when it loads, its origin: how it differs from the bundled profile it is based on, as
    information."""
    location: str
    problems: tuple[Problem, ...]
    files: int
    origin: Origin | None

    @property
    def ok(self) -> bool:
        return not self.problems


CheckResult = ProfileChecked | NoProfileChosen | ProfileRefused


@dataclass(frozen=True)
class KnownProfiles:
    """The profiles a project knows: the one in force for it (None: none is, or its settings cannot be read or it does
    not load), and the bundled ones."""
    in_force: str | None
    bundled: tuple[str, ...]


@dataclass(frozen=True)
class NewProfile:
    """Write a custom profile named name as a copy of the bundled profile source, with every file it points to, in
    folder out (default: architecture/<name>/ beside app, the app folder); nothing is overwritten. cwd is the working
    folder, in full, that a relative app or out is read from."""
    name: str
    source: str
    app: Path
    cwd: Path
    out: Path | None = None


@dataclass(frozen=True)
class ProfileCreated:
    """The copy: its folder, its profile file, every file written (the profile first, paths relative to the folder),
    and the profile file as the project's settings record it, to put it in force."""
    folder: Path
    profile: Path
    files: tuple[str, ...]
    location: str


NewResult = ProfileCreated | FilesTaken | ProfileRefused
