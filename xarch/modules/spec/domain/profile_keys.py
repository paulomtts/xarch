"""The keys of a profile file (format version 2), in one table: the loader reads it for the keys each mapping accepts
and the ones it needs, and what explains a profile reads it for what each key means.

A key sits in a scope, a kind of mapping, such as a part, written as its address in the file (`parts.<part>`). It has a
meaning in one line, says whether the profile needs it, and whether it is enforced (changes what `xarch check` does)
or documentary (only fills the generated docs or reports).
"""
from __future__ import annotations

from dataclasses import dataclass

PROFILE = "profile"
PART = "part"
TIER = "tier"
TIER_DOCS = "tier.docs"
TESTING = "testing"
TABLE = "testing.table"
MOCKS = "testing.mocks"
FIXTURE = "testing.fixture"
FAKES = "fakes"
SCENARIO_COVERAGE = "guard.scenario-coverage"
NO_DUPLICATES = "guard.no-duplicates"
PASS_THROUGH = "guard.pass-through"
DOCS = "docs"
PAGE = "docs.page"
NAMING = "docs.naming"
FILE = "file"

SCOPES = {
    PROFILE: "the file",
    PART: "parts.<part>",
    TIER: "tiers.<tier>",
    TIER_DOCS: "tiers.<tier>.docs",
    TESTING: "testing",
    TABLE: "testing.table",
    MOCKS: "testing.mocks",
    FIXTURE: "testing.mocks.fixtures.<parameter>",
    FAKES: "fakes",
    SCENARIO_COVERAGE: "guards.scenario-coverage",
    NO_DUPLICATES: "guards.no-duplicates",
    PASS_THROUGH: "guards.pass-through",
    DOCS: "docs",
    PAGE: "docs.pages.<path>",
    NAMING: "docs.naming[]",
    FILE: "files.<path>",
}
"""Each scope's address in the file."""


@dataclass(frozen=True)
class Key:
    """One key: where it sits, what it means, whether the profile needs it, and whether `check` enforces it.

    scope: one of SCOPES
    meaning: one line, what to write and what it does
    required: the profile is refused without it
    enforced: it changes what `xarch check` does; False: it only feeds the generated docs or a report
    """
    scope: str
    name: str
    meaning: str
    required: bool = False
    enforced: bool = True

    @property
    def where(self) -> str:
        return SCOPES[self.scope]

    @property
    def address(self) -> str:
        return self.name if self.scope == PROFILE else f"{self.where}.{self.name}"


def _k(scope: str, name: str, meaning: str, required: bool = False, enforced: bool = True) -> Key:
    return Key(scope, name, meaning, required, enforced)


KEYS: tuple[Key, ...] = (
    _k(PROFILE, "xarch", "the format version: 2", True, False),
    _k(PROFILE, "name", "what the profile is called", True, False),
    _k(PROFILE, "based_on", "the bundled profile this one was copied from; a report compares with it", False, False),
    _k(PROFILE, "language", "the language of the app: python, the default and the only one", False),
    _k(PROFILE, "testing", "how the test framework names things: a preset name, or the map {files, functions, ...}"),
    _k(PROFILE, "parts", "where code sits, in the order their litmus tests run: {<part>: {path, role, ...}}", True),
    _k(PROFILE, "forbidden", "named lists of names a part may not use: {<list>: [<dotted name>, ...]}"),
    _k(PROFILE, "layers", "chains of parts from the inside out; no part imports one after it: {<name>: [<part>, ...]}"),
    _k(PROFILE, "tiers", "the kinds of test, in the order their litmus tests run: {<tier>: {...}}"),
    _k(PROFILE, "fakes", "the folder of the test fakes and the parts they stand in for: {folder, for, prefix}"),
    _k(PROFILE, "guards", "the pre-built checks in use: {<guard>: {...}}; left out means off"),
    _k(PROFILE, "excluded", "folders below the app that are not its source: {<folder>: <reason>}"),
    _k(PROFILE, "hints", "your own advice for a rule, shown after its built-in fix: {<rule id>: <text>}", False, False),
    _k(PROFILE, "files", "the files `init` writes besides the docs: {<path>: <from> or {from, pinned, fill}}"),
    _k(PROFILE, "docs", "everything that only fills the generated docs", False, False),

    _k(PART, "path", "where the part lives below the app: a folder, or a file when its last step holds a dot; "
                     "a `<name>` step stands for the repeating folder", True),
    _k(PART, "role", "what the part is for, in one line; the docs' tree note of it", True, False),
    _k(PART, "litmus", "the question that tells code belongs here", False, False),
    _k(PART, "may_import", "what the part may import besides itself: [<part>, <part>@any, <part>/<path>, ...] "
                           "or everything"),
    _k(PART, "must_import", "each source file of the part imports one of these targets (as `may_import` writes them, each "
                            "one the part may import) or an outside package, or reaches one through a file of the "
                            "part: [<part>, <part>@any, ...]"),
    _k(PART, "libraries", "the outside packages the part may import by top-level name, or everything; none by default"),
    _k(PART, "forbidden", "the name of a top-level `forbidden` list the part may not use"),
    _k(PART, "tier", "the tier whose tests cover the part; one tier per part"),
    _k(PART, "untested", "why no tier tests the part, in one line"),
    _k(PART, "package_only", "true: the part is imported only as a package from outside it"),
    _k(PART, "folders", "the folders below the part the layout shows: {<folder>: <note>} or [<folder>, ...]"),

    _k(TIER, "proves", "what its tests prove, in one line", False, False),
    _k(TIER, "litmus", "the question that tells a test belongs to the tier", False, False),
    _k(TIER, "apply_forbidden", "true: its tests are held to the `forbidden` list of the part they mirror"),
    _k(TIER, "types_only", "the parts its tests may import and use as types, never call"),
    _k(TIER, "folder", "a folder below the tests folder where its tests live when they mirror no part"),
    _k(TIER, "may_import", "what the tests in its folder may import of the app, as a part's may_import does"),
    _k(TIER, "docs", "what only fills the generated docs", False, False),

    _k(TIER_DOCS, "subject", "the Subject cell as written, in place of the parts of the tier", False, False),
    _k(TIER_DOCS, "may_touch", "what its tests may touch, in one line", False, False),
    _k(TIER_DOCS, "one_file_per", "what one test file covers", False, False),
    _k(TIER_DOCS, "cases_from", "where its cases come from", False, False),
    _k(TIER_DOCS, "data", "where its test data comes from", False, False),
    _k(TIER_DOCS, "example", "its example test: a path in an example project", False, False),
    _k(TIER_DOCS, "helpers", "the files its tests share: [<path in an example project>, ...]", False, False),

    _k(TESTING, "files", "patterns of a test file's name, `*` for any text", True),
    _k(TESTING, "functions", "the pattern of a test function's name, `*` for any text", True),
    _k(TESTING, "skips", "dotted names of what skips a test or expects it to fail, which `check` counts"),
    _k(TESTING, "table", "how a test function holds a table of cases: {decorator, row, id, keywords}"),
    _k(TESTING, "mocks", "how a mock is built: {calls, autospec, spec_keywords, fixtures}"),

    _k(TABLE, "decorator", "the dotted name of the decorator that holds the rows", True),
    _k(TABLE, "row", "the dotted name of a row", True),
    _k(TABLE, "id", "the keyword that gives a row its id", True),
    _k(TABLE, "keywords", "the two keywords the decorator's arguments may be given by"),

    _k(MOCKS, "calls", "dotted names of the calls that build a mock", True),
    _k(MOCKS, "autospec", "dotted names of the calls that build a mock from a spec given as an argument"),
    _k(MOCKS, "spec_keywords", "the keywords a mock is given its spec by", True),
    _k(MOCKS, "fixtures", "test function parameters whose methods build mocks: {<parameter>: {calls, autospec}}"),

    _k(FIXTURE, "calls", "the methods that build a mock", True),
    _k(FIXTURE, "autospec", "the methods that build a mock from a spec given as an argument"),

    _k(FAKES, "folder", "the folder of the fakes, below the tests folder", True),
    _k(FAKES, "for", "the parts whose Protocols the fakes stand in for", True),
    _k(FAKES, "prefix", "how a fake's name starts: the fake of DocumentRepo is FakeDocumentRepo"),

    _k(SCENARIO_COVERAGE, "results", "the part holding the result unions", True),
    _k(SCENARIO_COVERAGE, "tier", "the tier whose test files hold their tables", True),
    _k(SCENARIO_COVERAGE, "suffix", "how a union's name ends", True),
    _k(SCENARIO_COVERAGE, "columns", "the three parameter names of a table: its state, its command, its result", True),
    _k(SCENARIO_COVERAGE, "file", "the name of a use case's test file, {name} for the use case", True),

    _k(NO_DUPLICATES, "min_statements", "the fewest statements a function needs to count as a duplicate; 4 when left "
                                        "out"),

    _k(PASS_THROUGH, "parts", "the parts whose methods are listed when their whole body only forwards to one call: "
                              "[<part>, ...]", True),

    _k(DOCS, "entry", "the part that is the entry point, which drives the rest", False, False),
    _k(DOCS, "pages", "the project docs `init` writes below docs/project/: {<path>: <from> or {from, note}}", False,
       False),
    _k(DOCS, "naming", "the naming table: [{kind, where, pattern, example}, ...]", False, False),
    _k(DOCS, "examples", "folders next to the profile, each an example project: a template quotes one of its files "
                         "by its path with {{example:<path>}}", False, False),
    _k(DOCS, "example_notes", "a note for an example, shown after its path: {<path>: <note>}", False, False),

    _k(PAGE, "from", "the template file, next to the profile", False, False),
    _k(PAGE, "note", "shown after its line in the docs tree, in one line", False, False),

    _k(NAMING, "kind", "what is named, such as adapter", True, False),
    _k(NAMING, "where", "the folders it lives in", True, False),
    _k(NAMING, "pattern", "how it is named", True, False),
    _k(NAMING, "example", "names that follow the pattern", True, False),

    _k(FILE, "from", "the template file, or the folder of a path ending in /, next to the profile", True),
    _k(FILE, "pinned", "true: `check` reports the file when it differs from what `init` writes"),
    _k(FILE, "fill", "whether {{app}} is filled in; off, the bytes are copied unchanged"),
)
"""Every key of every scope, in the order a file writes them."""

MOVED = {
    "layout": "delete it: the layout comes from each part's `path` and `folders`",
    "notes": "write the note of a folder under `folders` on the part that holds it",
    "rules": "write each part's targets as `may_import` on the part",
    "placement": "delete it: the order of `parts` is the order the litmus tests run",
    "naming": "move it to `docs.naming`",
    "tests": "write `testing`: a preset name, or the map {files, functions, ...}",
    "examples": "move it to `docs.examples`",
    "libraries": "write each part's packages as `libraries` on the part",
}
"""A key of version 1 that has moved, with what to write instead."""


def keys_of(scope: str) -> tuple[Key, ...]:
    return tuple(key for key in KEYS if key.scope == scope)


def names_of(scope: str) -> set[str]:
    return {key.name for key in keys_of(scope)}


def required_of(scope: str) -> tuple[str, ...]:
    return tuple(key.name for key in keys_of(scope) if key.required)
