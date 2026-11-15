"""What the spec module publishes: the skeleton of a profile as flat lists of entries, and which profile is in force."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from xarch.kernel.logic.placement import Repeat, Target

__all__ = ["Entry", "Repeating", "Skeleton", "DocFile", "Docs", "ProjectFile", "PartView", "TierView", "TableView",
           "ScenariosView", "FixtureView", "StandInsView", "GuardsView", "FakesView", "FrameworkView", "ExcludedView",
           "LanguageView", "ProfileView", "Loosened", "ProfileOrigin", "ChooseApp", "AppChosen", "ChooseAppResult",
           "SelectProfile", "ProfileSelected", "ProfileRefused",
           "NoProfileChosen", "SelectResult", "MigrateProfile", "MigratedFile", "Migrated", "MigrationRefused",
           "MigrateResult", "Shown", "Symbol", "Explain", "FormatExplained", "KeyExplained", "UnknownKey",
           "ExplainResult", "ViewProfile", "ProfileViewed", "ViewResult", "CheckProfile", "Problem", "ProfileChecked",
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
class ProjectFile:
    """A file `init` writes beside the app folder, in the folder holding it.

    path: below the folder holding the app, e.g. ("tests", "architecture", "test_rules<ending>"); a file inside the app
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
class TierView:
    """One kind of test as a check reads it: its name; the parts it tests, each as a target (in its own instance for a
    part of a repeating folder); the folder below the tests root of tests that mirror no part; the parts its tests may
    use as types only; whether its tests keep to their part's forbidden list; its words (proves, may_touch, litmus,
    one_file_per); what the tests of its folder may import (None: no folder); and the parts one of which each of its
    test files must reach."""
    name: str
    subject: tuple[Target, ...]
    folder: tuple[str, ...] | None = None
    types_only: tuple[str, ...] = ()
    forbidden: bool = False
    proves: str = ""
    may_touch: str = ""
    litmus: str = ""
    one_file_per: str = ""
    may_import: tuple[Target, ...] | None = None
    must_import: tuple[str, ...] = ()


@dataclass(frozen=True)
class TableView:
    """How a test function holds a table of cases: the dotted names of its decorator and of a row, the keyword that
    gives a row its id, and the keywords of its two arguments (None: positional only)."""
    decorator: tuple[str, ...]
    row: tuple[str, ...]
    id: str
    keywords: tuple[str, str] | None = None


@dataclass(frozen=True)
class ScenariosView:
    """The scenario-coverage guard: the part holding the Results, the tier of their tests, how a union's name ends,
    the three columns of a table, how a table is written, and the file name of a use case's test."""
    results: str
    tier: str
    suffix: str
    columns: tuple[str, str, str]
    table: TableView
    file: str


@dataclass(frozen=True)
class FixtureView:
    """A fixture whose methods build mocks: its name, the methods that build a mock, and those that take a spec."""
    name: str
    mocks: tuple[str, ...]
    autospec: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandInsView:
    """The stand-ins guard: what builds a mock, what builds one from a spec, the keywords a spec is given by, and the
    fixtures that build them."""
    mocks: tuple[tuple[str, ...], ...]
    autospec: tuple[tuple[str, ...], ...]
    spec: tuple[str, ...]
    fixtures: tuple[FixtureView, ...] = ()


@dataclass(frozen=True)
class GuardsView:
    """The guards a profile switches on, None or False when off: the package-only parts, scenario coverage, no
    comments, stand-ins, the closed tree, the fewest statements of a duplicate, dead code (and with it the files no
    test of their tier reaches), the parts whose forwarding methods are listed, and private imports."""
    package_only: tuple[str, ...] = ()
    scenarios: ScenariosView | None = None
    no_comments: bool = False
    stand_ins: StandInsView | None = None
    closed_tree: bool = False
    no_duplicates: int | None = None
    dead_code: bool = False
    untested: bool = False
    pass_through: tuple[str, ...] = ()
    private_imports: bool = False


@dataclass(frozen=True)
class FakesView:
    """Where the test fakes live below the tests root, the parts they stand in for, and how a fake's name starts."""
    folder: tuple[str, ...]
    stand_in_for: tuple[str, ...]
    prefix: str = ""


@dataclass(frozen=True)
class FrameworkView:
    """How the test framework names things: the patterns of a test file's name, that of a test function's, and the
    dotted names of what skips a test."""
    files: tuple[str, ...]
    functions: str
    skips: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class ExcludedView:
    """A folder below the app that is not its source, and why."""
    path: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class LanguageView:
    """The language of the app as a check reads it: how a message names it, the ending of a source file's name, the
    file that stands for the folder holding it, the dotted names that mark a class as an interface, and those of what
    imports by a name worked out when the code runs."""
    title: str = ""
    extension: str = ""
    package_file: str = ""
    interface: tuple[tuple[str, ...], ...] = ()
    dynamic: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class ProfileView:
    """A profile as the checks read it, everything they need already worked out: its parts in order; every folder of
    the layout as a pattern; its tiers in order; the outside packages each part may import (None: unchecked); its
    repeating folders; the guards switched on; the fakes and the test framework (None: none); the excluded folders;
    the project's own advice for a rule, by rule id; and the language of the app."""
    parts: tuple[PartView, ...]
    folders: tuple[tuple[str, ...], ...] = ()
    tiers: tuple[TierView, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    repeats: tuple[Repeat, ...] = ()
    guards: GuardsView = GuardsView()
    fakes: FakesView | None = None
    framework: FrameworkView | None = None
    excluded: tuple[ExcludedView, ...] = ()
    hints: dict[str, str] = field(default_factory=dict)
    language: LanguageView = LanguageView()


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

    sentence says it, naming the key of the profile that does.
    """
    key: str
    part: str
    what: str = ""
    sentence: str = ""


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
