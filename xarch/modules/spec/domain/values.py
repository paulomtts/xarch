"""Values of the spec module."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from xarch.kernel.logic.placement import EACH, EVERYTHING, Place, Scope, Target, place_of, with_itself


@dataclass(frozen=True)
class Configured:
    """A profile name as a project configured it, and the file it came from."""
    name: str
    source: Path


Layout = dict[str, "Layout | None"]
"""A layout tree: a dict is a folder, None a file; the key "*" is the `each` folder, one per instance."""


__all__ = ["EACH", "EVERYTHING", "Place", "Scope", "Target"]


@dataclass(frozen=True)
class Part:
    """Where code sits: a named path in the layout, with what goes there and how to tell.

    path: in the layout; EACH stands for the name of an `each` folder, e.g. ("src", "*", "api")
    role: one line; also the part's note in the docs' tree
    entry: the entry point, which drives the rest; at most one part is
    untested: why no tier tests it, e.g. "reached through the adapters that use it"
    """
    name: str
    path: tuple[str, ...]
    role: str
    litmus: str = ""
    entry: bool = False
    untested: str = ""

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
class ProjectFile:
    """A file `init` writes beside the app folder, in the folder holding it.

    path: below the folder holding the app, e.g. ("tests", "architecture", "test_rules.py")
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

    name: how the docs template refers to it, e.g. "charge"
    part: the part it illustrates
    path: where the example would live in an app, e.g. ("src", "billing", "service", "charge.py")
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

    path: e.g. ("tests", "modules", "documents", "domain", "test_document.py")
    file: the file holding its code, relative to the architecture file
    note: shown right after its path on its header line, as written
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


@dataclass(frozen=True)
class Excluded:
    """A folder below the app that is not its source, and why: no check reads it.

    path: below the app folder, e.g. ("architectures", "examples")
    reason: one line, shown in the enforcement section
    """
    path: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class Fakes:
    """Where the test fakes live, below the tests root, the parts they stand in for, and how a fake's name starts
    (the fake of port X is <prefix>X; empty when the file does not say)."""
    path: tuple[str, ...]
    stand_in_for: tuple[str, ...]
    prefix: str = ""


@dataclass(frozen=True)
class PackageOnly:
    """The guard package-only: these parts are imported only as a package from outside them."""
    parts: tuple[str, ...]


NAME = "{name}"
"""Stands, in the file name a guard expects, for the name of the use case in snake_case."""


@dataclass(frozen=True)
class Framework:
    """How the project's test framework names things: the patterns of a test file's name (matched against the file
    name alone, `*` for any text) and of a test function's, and the dotted names of what skips a test or expects it
    to fail (a marker or a call; empty: none is counted)."""
    files: tuple[str, ...]
    functions: str
    skips: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class CaseTable:
    """How a test function holds a table of cases: the dotted name of its decorator and of its row, the keyword that
    gives a row its id, and (None: positional only) the keywords its two arguments, the parameter names and the rows,
    may be given by."""
    decorator: tuple[str, ...]
    row: tuple[str, ...]
    id: str
    keywords: tuple[str, str] | None = None


@dataclass(frozen=True)
class ScenarioCoverage:
    """The guard scenario-coverage: the part holding the result unions, the tier holding their tables, how a union's
    name ends, the names of the three parameters of a table (its state, its command and its result), how the table
    is written, and the name of a use case's test file, `{name}` standing for the use case in snake_case."""
    results: str
    tier: str
    suffix: str
    columns: tuple[str, str, str]
    table: CaseTable
    file: str


@dataclass(frozen=True)
class NoComments:
    """The guard no-comments."""


@dataclass(frozen=True)
class Fixture:
    """A parameter of a test function that hands over a mock builder, and the names of its methods: those that build
    a mock, and those that build one from a spec given as an argument (autospec)."""
    name: str
    mocks: tuple[str, ...]
    autospec: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandIns:
    """The guard stand-ins: the dotted names of the calls that build a mock, of those that build a mock from a spec
    given as an argument (autospec), and the keywords a mock is given its spec by; the first keyword is the one an
    autospec call takes; and the fixtures, whose methods build mocks the same way. The other parameters are those of
    `fakes`."""
    mocks: tuple[tuple[str, ...], ...]
    autospec: tuple[tuple[str, ...], ...]
    spec: tuple[str, ...]
    fixtures: tuple[Fixture, ...] = ()


@dataclass(frozen=True)
class ClosedTree:
    """The guard closed-tree."""


Guard = PackageOnly | ScenarioCoverage | NoComments | StandIns | ClosedTree


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
    singular: the name of one instance of the `each` folder, as the docs show it; empty if the layout has no `each`
    framework: how the test framework names test files and functions; None when no tier or guard needs them
    files: the project files `init` writes besides the docs, in order
    forbidden: the dotted names and modules a part may not use, by part; a part not listed has none
    excluded: the folders below the app that are not its source, in the order of the file
    hints: the project's own advice for a rule id, shown after the built-in fix of a violation of that rule
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
    singular: str = ""
    files: tuple[ProjectFile, ...] = ()
    framework: Framework | None = None
    forbidden: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
    excluded: tuple[Excluded, ...] = ()
    hints: dict[str, str] = field(default_factory=dict)

    @property
    def entry(self) -> Part | None:
        """The entry point: the part marked `entry: true`, if any."""
        return next((part for part in self.parts.values() if part.entry), None)

    def shown(self, part: Part) -> str:
        """A part as the docs name it: its path below its instance for an instance's part, ending in / for a folder."""
        root = self.instance_root()
        path = part.path[len(root) + 1:] if part.in_instance and root is not None else part.path
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
        """What a part may import: itself (its own instance, for a part in the `each` folder), then its row."""
        return with_itself(part, self.parts[part].path, self.rules.get(part, ())) if part in self.parts else ()

    def place_of(self, path: tuple[str, ...]) -> Place:
        """Where a path below the app root sits, e.g. ("modules", "billing", "domain", "invoice.py") or the dotted
        module ("modules", "billing", "domain", "invoice"): the part whose pattern it lies in, the deepest when parts
        nest, with `*` capturing the module; a path no part claims is structure."""
        return place_of(self.patterns(), path)

    def patterns(self) -> dict[str, tuple[str, ...]]:
        """Every part's path pattern, by name."""
        return {name: part.path for name, part in self.parts.items()}

    def instance_root(self) -> tuple[str, ...] | None:
        """The folder holding the modules, e.g. ("modules",), or None if the layout has no `each`."""
        return _find_each(self.layout, ())

    def instance_tree(self) -> Layout:
        """What every module holds."""
        root = self.instance_root()
        if root is None:
            return {}
        folder = self.layout
        for name in root:
            folder = folder[name] or {}
        return folder[EACH] or {}

    def top_level_tree(self) -> Layout:
        """The layout below the app root, with the modules folder empty."""
        return _without_each(self.layout)


def _find_each(tree: Layout, prefix: tuple[str, ...]) -> tuple[str, ...] | None:
    for name, sub in tree.items():
        if name == EACH:
            return prefix
        if sub:
            found = _find_each(sub, prefix + (name,))
            if found is not None:
                return found
    return None


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
