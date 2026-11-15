"""Values of the spec module."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from xarch.kernel.logic.origin import Origin
from xarch.kernel.logic.placement import (
    EACH,
    EVERYTHING,
    Excluded,
    Marks,
    Place,
    Repeat,
    Scope,
    Target,
    place_of,
    repeat_of,
    with_itself,
)
from xarch.kernel.logic.testing import Fakes, Framework, ScenarioCoverage, StandIns


@dataclass(frozen=True)
class Configured:
    """A profile name as a project configured it, and the file it came from."""
    name: str
    source: Path


VERSION = 2
"""The one format version of a profile this xarch reads and writes."""
PROFILE_SUFFIX = ".yaml"
"""The suffix of every bundled profile file, and of each one xarch writes."""

Layout = dict[str, "Layout | None"]
"""A layout tree: a dict is a folder, None a file; the key "*" is a repeating folder, one per instance."""


__all__ = ["EACH", "EVERYTHING", "Place", "Repeat", "Scope", "Target"]


@dataclass(frozen=True)
class Part:
    """Where code sits: a named path in the layout, with what goes there and how to tell.

    path: in the layout; EACH stands for the name of a repeating folder, e.g. ("src", "*", "api")
    role: one line; also the part's note in the docs' tree
    entry: the entry point, which drives the rest; at most one part is
    untested: why no tier tests it, e.g. "reached through the adapters that use it"
    must_import: the targets each of its files must import one of (or an outside package); empty: no such rule
    holds: what its files define at module level, "classes" or "functions"; empty: either
    types_only: the parts its files may import and use as types, but never call
    no_callbacks: no function of it calls one of its own parameters
    names: the patterns one of which every public class of it matches (`*` for any text); empty: any name
    built_by: the only parts whose code may call the constructor of a class of it; empty: any part
    """
    name: str
    path: tuple[str, ...]
    role: str
    litmus: str = ""
    entry: bool = False
    untested: str = ""
    must_import: tuple[Target, ...] = ()
    holds: str = ""
    types_only: tuple[str, ...] = ()
    no_callbacks: bool = False
    names: tuple[str, ...] = ()
    built_by: tuple[str, ...] = ()

    @property
    def in_instance(self) -> bool:
        return EACH in self.path


@dataclass(frozen=True)
class Doc:
    """A file or folder of the project docs the architecture declares.

    path: below the docs folder, e.g. ("adrs", "0000-template.md")
    source: the template the file is filled from, relative to the architecture file; None for a folder
    note: shown after its line in the docs tree
    """
    path: tuple[str, ...]
    source: str | None
    note: str = ""

    @property
    def is_folder(self) -> bool:
        return self.source is None


@dataclass(frozen=True)
class FileEntry:
    """A file `init` writes beside the app folder, in the folder holding it.

    path: below the folder holding the app, e.g. ("tests", "architecture", "test_rules<ending>")
    source: the template the file is written from, relative to the architecture file; for a folder entry, the folder
    pinned: the project keeps it as `init` writes it; `check` reports it when it differs
    folder: the entry is a folder: every file under source is copied below path, keeping its relative path
    fill: `{{app}}` in the text is replaced by the app folder's name; off, the bytes are copied unchanged
    path may hold the placeholder `{{app}}` in a step, for a target inside the app folder.
    """
    path: tuple[str, ...]
    source: str
    pinned: bool = False
    folder: bool = False
    fill: bool = True


@dataclass(frozen=True)
class Example:
    """One file of the docs' example project: the part it illustrates, where it would live, and the file holding it.

    name: how the docs template refers to it: its path in its project, written with `/`
    part: the part it illustrates; empty for what no part claims, such as test code
    path: where the example would live in an app, e.g. ("src", "billing", "service", "charge<ending>")
    file: the file holding its code, relative to the architecture file
    note: shown after its path on its header line in the docs
    """
    name: str
    part: str
    path: tuple[str, ...]
    file: str
    note: str = ""


@dataclass(frozen=True)
class Naming:
    """One row of the docs' naming table: what a kind of thing is called, and where it lives.

    kind: e.g. "adapter"
    where: the folders it lives in, as the docs show them, e.g. ("adapters/",)
    pattern: markdown, e.g. "`<System><PortName>`"
    example: names, e.g. ("DbDocumentRepo", "ModerationContentReview")
    """
    kind: str
    where: tuple[str, ...]
    pattern: str
    example: tuple[str, ...]


@dataclass(frozen=True)
class Subject:
    """What a tier tests: a part, or only a path below it.

    sub: e.g. ("jobs",) for bootstrap/jobs
    """
    part: str
    sub: tuple[str, ...] = ()


@dataclass(frozen=True)
class TierExample:
    """A tier's example test: where it would live in a project, and the file holding it.

    path: e.g. ("tests", "modules", "documents", "domain", "test_document<ending>")
    file: the file holding its code, relative to the architecture file
    note: plain text, shown after its path on its header line in parentheses
    """
    path: tuple[str, ...]
    file: str
    note: str = ""


@dataclass(frozen=True)
class Tier:
    """One kind of test: what it tests, what it proves and may touch, and how to tell a test belongs to it.

    name: e.g. "use case"
    subject: the parts it tests; every part is in some tier's subject or is `untested`
    litmus: its placement litmus test; the docs show it as one paragraph, whatever its line breaks
    subject_text: the Subject cell as written, in place of the subject's parts
    data: where its test data comes from
    helpers: files its tests share (builders, a fixture), shown with {{tier_helpers}}
    types_only: parts its tests may import and use as types, but never call
    forbidden: its tests are held to the `forbidden` list of the part they mirror
    folder: the folder below the tests folder where its tests live when they mirror no part, e.g. ("architecture",);
        the example only shows a place, it never decides one
    may_import: what the tests in its own folder may import of the app, as targets; None for a tier with no folder,
        whose tests import what the part their folder mirrors may
    must_import: the parts one of which each of its test files reaches, directly or through test code that is no
        test; empty: no such rule
    """
    name: str
    subject: tuple[Subject, ...]
    proves: str
    may_touch: str
    litmus: str
    subject_text: str = ""
    one_file_per: str = ""
    cases_from: str = ""
    data: str = ""
    example: TierExample | None = None
    helpers: tuple[TierExample, ...] = ()
    types_only: tuple[str, ...] = ()
    forbidden: bool = False
    folder: tuple[str, ...] | None = None
    may_import: tuple[Target, ...] | None = None
    must_import: tuple[str, ...] = ()


@dataclass(frozen=True)
class PackageOnly:
    """The guard package-only: these parts are imported only as a package from outside them."""
    parts: tuple[str, ...]


NAME = "{name}"
"""Stands, in the file name a guard expects, for the name of the use case in snake_case."""


@dataclass(frozen=True)
class NoComments:
    """The guard no-comments."""


@dataclass(frozen=True)
class ClosedTree:
    """The guard closed-tree."""


@dataclass(frozen=True)
class NoDuplicates:
    """The guard no-duplicates: the fewest statements a function needs to count as a duplicate of another."""
    min_statements: int = 4


@dataclass(frozen=True)
class NoTwins:
    """The guard no-twins: the fewest fields a class needs to count as a twin of another."""
    min_fields: int = 3


@dataclass(frozen=True)
class DeadCode:
    """The guard dead-code: the ports and fakes come from `fakes`; untested: also list each file of a part with a
    tier that no test of that tier reaches."""
    untested: bool = False


@dataclass(frozen=True)
class PrivateImports:
    """The guard private-imports: no name starting with `_` is imported from another file."""


@dataclass(frozen=True)
class PassThrough:
    """The guard pass-through: the parts whose methods that only forward are listed."""
    parts: tuple[str, ...]


Guard = (PackageOnly | ScenarioCoverage | NoComments | StandIns | ClosedTree | NoDuplicates | NoTwins | DeadCode
         | PassThrough | PrivateImports)


@dataclass(frozen=True)
class Language:
    """What is true of the language of the app as a whole, read from the data file of its preset (and from the runtime
    for the names only it knows).

    title: how a message names the language
    extension: the ending of a source file's name
    package_file: the name of the file that stands for the folder holding it
    interface: the dotted names that mark a class as an interface
    dynamic: the dotted names of what imports by a name worked out when the code runs
    namespace: the namespace of the names bound without an import
    standard: where the names of the standard library are known from
    cache: the folder in which its tools keep what they compile; empty: none
    standard_names: the top-level names of the standard library
    builtin_names: the names bound without an import
    reserved_names: the words no name may be
    """
    name: str = ""
    title: str = ""
    extension: str = ""
    package_file: str = ""
    interface: tuple[tuple[str, ...], ...] = ()
    dynamic: tuple[tuple[str, ...], ...] = ()
    namespace: str = ""
    standard: str = ""
    cache: str = ""
    standard_names: frozenset[str] = frozenset()
    builtin_names: frozenset[str] = frozenset()
    reserved_names: frozenset[str] = frozenset()

    @property
    def marks(self) -> Marks:
        return Marks(self.extension, self.package_file)

    @property
    def interface_name(self) -> str:
        """What an interface is called in the language: the last step of the first name that marks one."""
        return self.interface[0][-1] if self.interface else ""


@dataclass(frozen=True)
class Architecture:
    """An architecture as described in an architecture file (format version 1).

    rules: every part, in the order of parts, with what it may import besides itself (which a part may always
        import, and no row says); a part with no row may import only itself
    docs: the project docs, in order: the files `init` writes and the folders it gives a note
    examples: by name, in the order of the file
    notes: by layout path: a folder that is not a part
    layers: named chains of parts, from the inside out
    placement: every part once: the order the litmus tests run in
    tiers: in the order their litmus tests run
    libraries: the outside packages each part may import; None: unchecked
    guards: the pre-built checks in use
    fakes: where the test fakes live; None: no test may import them
    repeats: the repeating folders of the layout, in the order of the profile: each its word, as the docs show one
        instance, and the folder it repeats in
    framework: how the test framework names test files and functions; None when no tier or guard needs them
    files: the project files `init` writes besides the docs, in order
    forbidden: the dotted names and modules a part may not use, and the methods it may not call on anything, each as
        ("", "<name>()"), by part; a part not listed has none
    excluded: the folders below the app that are not its source, in the order of the file
    hints: the project's own advice for a rule id, shown after the built-in fix of a violation of that rule
    based_on: the bundled profile it says it was copied from; empty when it does not say
    language: the language of the app
    reserved: the standard-library modules only the parts whose `libraries` list them may import, each with why
    """
    name: str
    layout: Layout
    parts: dict[str, Part]
    rules: dict[str, tuple[Target, ...]]
    docs: tuple[Doc, ...] = ()
    examples: dict[str, Example] = field(default_factory=dict)
    notes: dict[tuple[str, ...], str] = field(default_factory=dict)
    layers: dict[str, tuple[str, ...]] = field(default_factory=dict)
    placement: tuple[str, ...] = ()
    naming: tuple[Naming, ...] = ()
    tiers: tuple[Tier, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    guards: tuple[Guard, ...] = ()
    fakes: Fakes | None = None
    repeats: tuple[Repeat, ...] = ()
    files: tuple[FileEntry, ...] = ()
    framework: Framework | None = None
    forbidden: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
    excluded: tuple[Excluded, ...] = ()
    hints: dict[str, str] = field(default_factory=dict)
    based_on: str = ""
    language: Language = Language()
    reserved: dict[str, str] = field(default_factory=dict)

    @property
    def entry(self) -> Part | None:
        """The entry point: the part marked `entry: true`, if any."""
        return next((part for part in self.parts.values() if part.entry), None)

    def shown(self, part: Part) -> str:
        """A part as the docs name it: its path below its instance for an instance's part, ending in / for a folder."""
        repeat = repeat_of(self.repeats, part.path)
        path = part.path[len(repeat.root) + 1:] if repeat is not None else part.path
        return "/".join(path) + ("" if self.is_file(part.path) else "/")

    def is_file(self, path: tuple[str, ...]) -> bool:
        """Whether a path of the layout, such as a part's, is a file rather than a folder."""
        here: Layout | None = self.layout
        for step in path:
            if here is None or step not in here:
                return False
            here = here[step]
        return here is None

    def targets_of(self, part: str) -> tuple[Target, ...]:
        """What a part may import: itself (its own instance, for a part in a repeating folder), then its row."""
        return with_itself(part, self.parts[part].path, self.rules.get(part, ())) if part in self.parts else ()

    def place_of(self, path: tuple[str, ...]) -> Place:
        """Where a path below the app root sits, written as a file or as the language names it without the file's
        ending: the part whose pattern it lies in, the deepest when parts nest, with `*` capturing the module; a path no
        part claims is structure."""
        return place_of(self.patterns(), path, self.language.marks)

    def patterns(self) -> dict[str, tuple[str, ...]]:
        """Every part's path pattern, by name."""
        return {name: part.path for name, part in self.parts.items()}

    def words(self) -> dict[str, str]:
        """The word of the repeating folder each part lies in; a part outside every one has none."""
        return {name: repeat.word for name, part in self.parts.items()
                if (repeat := repeat_of(self.repeats, part.path)) is not None}

    def instance_tree(self, repeat: Repeat) -> Layout:
        """What every instance of a repeating folder holds."""
        folder = self.layout
        for name in repeat.root:
            folder = folder[name] or {}
        return folder[EACH] or {}

    def top_level_tree(self) -> Layout:
        """The layout below the app root, with every repeating folder empty."""
        return _without_each(self.layout)


def _without_each(tree: Layout) -> Layout:
    return {name: None if sub is None else _without_each(sub) for name, sub in tree.items() if name != EACH}


@dataclass(frozen=True)
class ArchitectureSource:
    """Where an architecture file is: one bundled with xarch, by name, or a path.

    location: a bundled name, e.g. "cli", or a path to a .yaml, .yml or .json file
    """
    location: str
    bundled: bool


@dataclass(frozen=True)
class ArchitectureDocument:
    """An architecture file as parsed, not yet validated.

    source: how problems name the file, e.g. "cli.yaml" or "docs/layered.yaml"
    document: whatever the YAML or JSON parser returned
    """
    source: str
    document: Any


@dataclass(frozen=True)
class Unloadable:
    """A profile checked that does not load: its location, and every problem the loader found, the files it points
    to included."""
    location: str
    problems: tuple[str, ...]


@dataclass(frozen=True)
class Loadable:
    """A profile checked that loads: its location, what its examples import that their part may not, how many files
    it points to, and where it comes from."""
    location: str
    example_problems: tuple[str, ...]
    files: int
    origin: Origin


Review = Unloadable | Loadable
"""What checking a profile found."""


@dataclass(frozen=True)
class LoadedProfile:
    """A profile chosen and loaded: its location as selected, its architecture, and whether it is bundled."""
    location: str
    architecture: Architecture
    bundled: bool


@dataclass(frozen=True)
class ProfileCopy:
    """A bundled profile copied into the project: the folder written, the name of the profile file in it, every file
    the bundled profile points to, copied beside it by its path in the folder, and the profile file as pyproject.toml
    records it."""
    folder: Path
    profile: str
    pointed: tuple[str, ...]
    location: str


@dataclass(frozen=True)
class Quotes:
    """The texts a profile's docs quote from its files: each example's file, by the example's name, and each tier's
    example test and helper, by the tier's name or the helper's file."""
    examples: Mapping[str, str]
    tier_examples: Mapping[str, str]

