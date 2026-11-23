"""Values of the spec module."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from xarch.kernel.logic.placement import place_of, repeat_of, with_itself
from xarch.kernel.placement import EACH, Place
from xarch.modules.spec.domain.published import Eval, Held
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.checks import WrittenCheck
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns


@dataclass(frozen=True)
class Configured:
    """A profile name as a project configured it, and the file it came from."""
    name: str
    source: Path


PROFILE_SUFFIX = ".yaml"
"""The suffix of every bundled profile file, and of each one xarch writes."""
LANGUAGES = "presets/language"
"""Where the data files of the languages are, below the bundled folder: one YAML file each, named for the language."""
INTERPRETER = "interpreter"
"""The `standard` of a language's data file that says its standard library, its reserved words and the names it binds
without an import are known from the interpreter running xarch, as its runtime says them."""
FORMAT = "presets/format"
"""Where the data files of the profile format are, below the bundled folder."""
FORMAT_KEYS = f"{FORMAT}/keys.yaml"
"""The data file of the texts `xarch profile explain` says for the keys of the format (see key_catalogue)."""
FILE_TYPES = f"{FORMAT}/file_types.yaml"
"""The data file of the kinds of file the docs quote besides the language of the app (see file_types)."""

SLOTS = ("read", "in", "keep", "may_not", "may_only", "must_reach", "must_be_reached", "except", "mode", "message",
         "fix", "once_per", "cases", "examples")
"""Every slot of a check a profile writes under `checks`, in the order a check is written: spec reads them, and writes
a check with them."""
SCOPE_SLOTS = ("files", "part", "tier", "where")
"""The slots of a scope (`in`, and `from` of must_be_reached)."""
REACH_SLOTS = {"must_reach": ("targets", "through", "through_only"),
               "must_be_reached": ("from", "through", "through_only", "then_through", "by_another_file")}
"""The slots of a quantifier of reach, in the order they are written."""
CASE_SLOTS = ("when", "message", "fix", "once_per")
"""The slots of a case."""
EXAMPLE_SLOTS = ("flagged", "clean")
"""The slots of a check's examples: the code it must find something in, then the code it must find nothing in."""
STRUCTURE_WORD = "structure"
"""How a scope's part names the structure (profile_values' STRUCTURE): the folders of the layout no part claims."""

Layout = dict[str, "Layout | None"]
"""A layout tree: a dict is a folder, None a file; the key "*" is a repeating folder, one per instance."""


@dataclass(frozen=True)
class FileType:
    """A kind of file the docs quote, by what its data file says of it.

    fence: the word that names the language of a fenced block of such files; empty: the ending of their name, without
        its dot
    comment: the marker of a line comment in them; empty: the one of the language of the app
    """
    fence: str = ""
    comment: str = ""


@dataclass(frozen=True)
class Part:
    """Where code sits: a named path in the layout, with what goes there and how to tell.

    path: in the layout; EACH stands for the name of a repeating folder, e.g. ("src", "*", "api")
    role: one line; also the part's note in the docs' tree
    entry: the entry point, which drives the rest; at most one part is
    untested: why no tier tests it, e.g. "reached through the adapters that use it"
    must_import: the targets each of its files must import one of (or an outside package); empty: no such rule
    holds: the kinds its files may define at the top level, each with its settings (the patterns their names match,
        whether its classes are immutable records, as the language's data file says one is made, and the only parts
        whose code may build them), in the order of KINDS whatever the order written; empty: every kind
    types_only: the parts its files may import and use as types, but never call
    shared: the fewest users each public name it defines must have, being there to be shared; None: not shared
    """
    name: str
    path: tuple[str, ...]
    role: str
    litmus: str = ""
    entry: bool = False
    untested: str = ""
    must_import: tuple[Target, ...] = ()
    holds: tuple[Held, ...] = ()
    types_only: tuple[str, ...] = ()
    shared: int | None = None

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
    apply_never: its tests are held to the `uses.never` list of the part they mirror
    folder: the folder below the tests folder where its tests live when they mirror no part, e.g. ("architecture",);
        the example only shows a place, it never decides one
    may_import: what the tests in its own folder may import of the app, as targets; None for a tier with no folder,
        whose tests import what the part their folder mirrors may
    must_import: the parts one of which each of its test files reaches, directly or through test code that is no
        test; empty: no such rule
    plain_tables: every table test of it holds no branch in its body
    may_also_import: what each of its tests may import of the app besides what the part it mirrors may (or its own
        folder's allowance), as targets; a bare name of a part in the repeating folder is the instance the test mirrors
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
    apply_never: bool = False
    folder: tuple[str, ...] | None = None
    may_import: tuple[Target, ...] | None = None
    must_import: tuple[str, ...] = ()
    plain_tables: bool = False
    may_also_import: tuple[Target, ...] = ()


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
    """The guard no-twins: the fewest fields a class needs to count as a twin of another; the fewest a renamed copy
    needs, and the fewest a copy of part of another's fields needs (None: that case is off); and the parts whose files
    translate a value of one part into a value of another, so that a pair one of them translates is no twin."""
    min_fields: int = 3
    min_renamed: int | None = None
    min_subset: int | None = None
    translated: tuple[str, ...] = ()


@dataclass(frozen=True)
class DeadCode:
    """The guard dead-code: the ports and fakes come from `fakes`; untested: also list each file of a part with a
    tier that no test of that tier reaches; tests_only: also list each public name of the app no other file of the app
    names, so that only the tests, or nothing, use it; known: the public names tests_only accepts as only the tests',
    each `<file below the app>:<name>` as written."""
    untested: bool = False
    tests_only: bool = False
    known: tuple[str, ...] = ()


@dataclass(frozen=True)
class PrivateImports:
    """The guard private-imports: no name another file keeps private is imported from it."""


@dataclass(frozen=True)
class PassThrough:
    """The guard pass-through: the parts whose methods that only forward are listed."""
    parts: tuple[str, ...]


@dataclass(frozen=True)
class NoCallbacks:
    """The guard no-callbacks: the parts whose functions call none of their own parameters annotated as callables."""
    parts: tuple[str, ...]


Guard = (PackageOnly | ScenarioCoverage | NoComments | StandIns | ClosedTree | NoDuplicates | NoTwins | DeadCode
         | PassThrough | NoCallbacks | PrivateImports)


@dataclass(frozen=True)
class StandardLists:
    """What a language's data file lists as its `standard`, each in the order written: modules, the top-level modules
    of its standard library; reserved, the words no name may be; builtins, the names it binds without an import."""
    modules: tuple[str, ...] = ()
    reserved: tuple[str, ...] = ()
    builtins: tuple[str, ...] = ()


@dataclass(frozen=True)
class Language:
    """What is true of the language of the app as a whole, read from the data file of its preset (and from the runtime
    for the names only it knows, when the data file says INTERPRETER).

    name: how a profile names it
    checked: the language as the checks read it, which spec builds and the checking module reads in full
    namespace: the namespace of the names bound without an import
    standard: where the names of the standard library are known from: INTERPRETER, the runtime, or the lists the data
        file gives (StandardLists)
    cache: the folder in which its tools keep what they compile; empty: none
    names: a regular expression, what a name may be (empty: the language does not say)
    standard_names: the top-level names of the standard library
    builtin_names: the names bound without an import
    reserved_names: the words no name may be
    """
    name: str = ""
    checked: CheckedLanguage = CheckedLanguage()
    namespace: str = ""
    standard: str | StandardLists = ""
    cache: str = ""
    names: str = ""
    standard_names: frozenset[str] = frozenset()
    builtin_names: frozenset[str] = frozenset()
    reserved_names: frozenset[str] = frozenset()

    @property
    def interface_name(self) -> str:
        """What an interface is called in the language: the last step of the first mark's base, or its keyword; ""
        when nothing marks one."""
        if not self.checked.interface:
            return ""
        first = self.checked.interface[0]
        return first.base[-1] if first.base else first.keyword

    def compiled(self, path: str) -> bool:
        """Whether a path, written with `/`, lies in the folder in which the language's tools keep what they compile."""
        return bool(self.cache) and self.cache in path.split("/")


@dataclass(frozen=True)
class Architecture:
    """An architecture as described in an architecture file.

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
    uses_never: the dotted names and modules a part may not use, and the methods it may not call on anything, each as
        ("", "<name>()"), by part; a part not listed has none
    excluded: the folders below the app that are not its source, in the order of the file
    hints: the project's own advice for a rule id, shown after the built-in fix of a violation of that rule
    based_on: the bundled profile it says it was copied from; empty when it does not say
    language: the language of the app
    reserved: the standard-library modules only the parts whose `libraries` list them may import, each with why
    approximate: the keys whose check reads a fact the language supplies only partly, with the reader's note
    checks: the checks the profile writes itself, by id, each as the format writes it (see written_checks): what the
        words in them mean is the rules module's
    never: the path patterns below the app of the files review never sends (`review.never`), as written
    mask: the text patterns review hides before it sends (`review.mask`), as written
    lines: the line of each part the profile writes one for (`evals.placement.lines`), by part: below it a file reads
        as doubtful there in review
    evals: the evals of the profile's own, by id, in the order of the file, which review asks
    placed: the examples placement is held to besides the docs' (`evals.placement.examples`): the flagged ones (each
        lying in a part it does not belong in) and the clean ones, each by its path below the app with its code
    alike: the groups of parts one file cannot tell apart (`evals.placement.alike`), in the order of the file, each its
        parts by name in the order written: review reads a file of one on the sum of the group's probabilities
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
    uses_never: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
    excluded: tuple[Excluded, ...] = ()
    hints: dict[str, str] = field(default_factory=dict)
    based_on: str = ""
    language: Language = Language()
    reserved: dict[str, str] = field(default_factory=dict)
    approximate: tuple[Shortfall, ...] = ()
    checks: dict[str, WrittenCheck] = field(default_factory=dict)
    never: tuple[str, ...] = ()
    mask: tuple[str, ...] = ()
    lines: dict[str, float] = field(default_factory=dict)
    evals: dict[str, Eval] = field(default_factory=dict)
    placed: tuple[tuple[tuple[str, str], ...], tuple[tuple[str, str], ...]] = ((), ())
    alike: tuple[tuple[str, ...], ...] = ()

    @property
    def entry(self) -> Part | None:
        """The entry point: the part marked `entry: true`, if any."""
        return next((part for part in self.parts.values() if part.entry), None)

    def targets_of(self, part: str) -> tuple[Target, ...]:
        """What a part may import: itself (its own instance, for a part in a repeating folder), then its row."""
        return with_itself(part, self.parts[part].path, self.rules.get(part, ())) if part in self.parts else ()

    def place_of(self, path: tuple[str, ...]) -> Place:
        """Where a path below the app root sits, written as a file or as the language names it without the file's
        ending: the part whose pattern it lies in, the deepest when parts nest, with `*` capturing the module; a path no
        part claims is structure."""
        return place_of(self.patterns(), path, self.language.checked.marks)

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

    @staticmethod
    def names_a_file(location: str | Path) -> bool:
        """Whether a location names a file rather than a bundled architecture: it is a path, or has a folder or a
        suffix."""
        path = Path(location)
        return isinstance(location, Path) or len(path.parts) != 1 or bool(path.suffix)


@dataclass(frozen=True)
class ArchitectureDocument:
    """An architecture file as parsed, not yet validated.

    source: how problems name the file, e.g. "cli.yaml" or "docs/layered.yaml"
    document: whatever the YAML or JSON parser returned
    """
    source: str
    document: Any


