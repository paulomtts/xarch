"""The keys of a profile file (format version 2), in one table: the loader reads it for the keys each mapping accepts
and the ones it needs, and `xarch profile explain` reads it for what each key means, accepts and shows as an example.

A key sits in a scope, a kind of mapping, such as a part, written as its address in the file (`parts.<part>`). It has a
meaning in a few words, says what it accepts, whether the profile needs it, whether it is enforced (changes what
`xarch check` does, through the rule ids it lists) or documentary (only fills the generated docs or reports), and a
short example: a fragment of a profile that loads once merged into the smallest one. A key that holds keys names the
scope they sit in.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from textwrap import indent

from xarch.modules.spec.domain.guards import GUARDS

PROFILE = "profile"
PART = "part"
TIER = "tier"
TIER_DOCS = "tier.docs"
TESTING = "testing"
TABLE = "testing.table"
MOCKS = "testing.mocks"
FIXTURE = "testing.fixture"
FAKES = "fakes"
GUARD = "guard"
SCENARIO_COVERAGE = "guard.scenario-coverage"
NO_DUPLICATES = "guard.no-duplicates"
DEAD_CODE = "guard.dead-code"
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
    GUARD: "guards",
    SCENARIO_COVERAGE: "guards.scenario-coverage",
    NO_DUPLICATES: "guards.no-duplicates",
    DEAD_CODE: "guards.dead-code",
    PASS_THROUGH: "guards.pass-through",
    DOCS: "docs",
    PAGE: "docs.pages.<path>",
    NAMING: "docs.naming[]",
    FILE: "files.<path>",
}
"""Each scope's address in the file."""

CHOICE_BUNDLED = "bundled"
CHOICE_PRESETS = "presets"
"""What a key may name from a list xarch ships: the bundled profiles, or the `testing` presets."""

SMALLEST = """\
xarch: 2
name: documents-app
parts:
  documents:
    path: documents
    role: the documents
"""
"""The smallest valid profile: one part, no rule, no test."""

SYMBOLS: tuple[tuple[str, str], ...] = (
    ("<word>", "in a path: a repeating folder, one per name, as in units/<unit>/store; there may be several"),
    ("store", "in may_import, a bare name: that part, in the importer's own instance of its repeating folder"),
    ("store@any", "that part in any instance; the only way to name a part of another repeating folder"),
    ("store/schema", "only what lies below that path of the part"),
    ("store:*Id", "in may_import, after `:`: only the names that match the pattern, `*` for any text"),
    ("everything", "in may_import or libraries: no limit"),
    ("a path ending in .py", "a last path step with a dot: the part is one file, not a folder"),
)
"""The symbols a profile writes in paths and imports, each with what it means."""

_PART = "parts:\n  documents:\n    path: documents\n    role: the documents\n"
_TWO = ("parts:\n  core:\n    path: core\n    role: the rules of the documents\n  documents:\n    path: documents\n"
        "    role: the documents\n    may_import: [core]\n")
_TESTING = 'testing:\n  files: [check_*.py]\n  functions: "check_*"\n'
_FAKES = "fakes:\n  folder: fakes\n  for: [core]\n  prefix: Fake\n"
_MOCKS = "    calls: [doubles.make]\n    spec_keywords: [spec]\n"


def _in_part(extra: str) -> str:
    return _PART + indent(extra, "    ")


def _in_two(extra: str) -> str:
    return _TWO + indent(extra, "    ")


def _tiered(tier: str) -> str:
    return (_TESTING + "tiers:\n  unit:\n" + indent(tier, "    ")
            + "parts:\n  documents:\n    path: documents\n    role: the documents\n    tier: unit\n")


def _tier_folder(tier: str) -> str:
    return (_TESTING + "tiers:\n  unit: {}\n  guard:\n    folder: architecture\n" + indent(tier, "    ")
            + "parts:\n  documents:\n    path: documents\n    role: the documents\n    tier: unit\n")


def _tests(extra: str) -> str:
    return _TESTING + indent(extra, "  ")


def _docs(extra: str) -> str:
    return "docs:\n" + indent(extra, "  ")


def _guarded(extra: str, before: str = "") -> str:
    return before + "guards:\n" + indent(extra, "  ")


_TABLE_BLOCK = "  table:\n    decorator: checks.cases\n    row: checks.case\n    id: id\n"
_COVERAGE = (_TESTING + _TABLE_BLOCK + "tiers:\n  integration:\n    proves: a use case\n"
             "parts:\n  documents:\n    path: units/<unit>/documents\n    role: the documents\n    tier: integration\n"
             "  results:\n    path: units/<unit>/results\n    role: the result unions\n    tier: integration\n")
_COVERAGE_GUARD = _COVERAGE + (
    "guards:\n  scenario-coverage:\n    results: results\n    tier: integration\n    suffix: Result\n"
    "    columns: [given, when, then]\n    file: check_{name}.py\n")
_STAND_INS = (_TESTING + "  mocks:\n" + _MOCKS + _TWO + _FAKES)
_PAGES = _docs("pages:\n  statement.md:\n    from: docs/statement.md\n    note: the problem the documents solve\n")


@dataclass(frozen=True)
class Key:
    """One key: where it sits, what it means and accepts, whether the profile needs it, and whether `check` enforces it.

    scope: one of SCOPES
    meaning: a few words, what the key is for
    accepts: what to write, and what it does
    example: a fragment of a profile that uses the key; merged into the smallest profile it loads
    required: the profile is refused without it
    enforced: it changes what `xarch check` does; False: it only feeds the generated docs or a report
    rules: the rule ids of `check` the key feeds; none for a key the loader alone enforces
    opens: the scope of the keys its value holds
    choices: CHOICE_BUNDLED or CHOICE_PRESETS when it names something from a list xarch ships; `<bundled>` and
        `<preset>` in the example stand for the first of that list
    """
    scope: str
    name: str
    meaning: str
    accepts: str
    example: str
    required: bool = False
    enforced: bool = True
    rules: tuple[str, ...] = ()
    opens: str = ""
    choices: str = ""

    @property
    def where(self) -> str:
        return SCOPES[self.scope]

    @property
    def address(self) -> str:
        return self.name if self.scope == PROFILE else f"{self.where}.{self.name}"


_PLACEHOLDER = re.compile(r"\.?<[^>]*>|\[\]")


def plain(address: str) -> str:
    """The address as a person types it: without the placeholder steps and `[]`, parts.<part>.may_import being
    parts.may_import."""
    return _PLACEHOLDER.sub("", address)


def _k(scope: str, name: str, meaning: str, accepts: str, example: str, required: bool = False, enforced: bool = True,
       rules: tuple[str, ...] = (), opens: str = "", choices: str = "") -> Key:
    return Key(scope, name, meaning, accepts, example, required, enforced, rules, opens, choices)


def _guard(name: str, meaning: str, example: str) -> Key:
    return Key(GUARD, name, meaning, GUARDS[name], example, False, True, (name,), _GUARD_SCOPES.get(name, ""))


_GUARD_SCOPES = {"scenario-coverage": SCENARIO_COVERAGE, "no-duplicates": NO_DUPLICATES, "dead-code": DEAD_CODE,
                 "pass-through": PASS_THROUGH}


KEYS: tuple[Key, ...] = (
    _k(PROFILE, "xarch", "the format version", "the number 2", "xarch: 2", True, False),
    _k(PROFILE, "name", "what the profile is called", "a non-empty string", "name: documents-app", True, False),
    _k(PROFILE, "based_on", "the bundled profile this was copied from",
       "the name of a bundled profile: `profile check` reports how this one is looser than it", "based_on: <bundled>",
       False, False, choices=CHOICE_BUNDLED),
    _k(PROFILE, "language", "the language of the app", "python: the default, and the only one", "language: python"),
    _k(PROFILE, "testing", "how the test framework names things",
       "a preset name, or a map {files, functions, skips, table, mocks}; needed with `tiers` and the guards "
       "scenario-coverage and stand-ins. Dotted names are what an absolute import binds; what stays Python is "
       "`typing.Protocol` as the mark of a port, `__init__.py`, the syntax tree, import resolution and the standard "
       "library's names", 'testing:\n  files: [check_*.py]\n  functions: "check_*"',
       rules=("tiers", "test-tree"), opens=TESTING, choices=CHOICE_PRESETS),
    _k(PROFILE, "parts", "where code sits, in the order their litmus tests run",
       "a map {<part>: {path, role, ...}}: each part is a folder or a file below the app; the layout is made of "
       "their paths and `folders`", _TWO, True, rules=("structure", "rules"), opens=PART),
    _k(PROFILE, "forbidden", "named lists of names a part may not use",
       "a map {<list>: [<dotted name>, ...]}; a part points to one list with `forbidden: <list>`. An entry is a dotted "
       "name as an absolute import binds it (`datetime.datetime.now`; a builtin as `builtins.open`, a bare `open` is "
       "refused) or a whole package (`socket`). A file may not import a listed package or anything below it, nor use "
       "a listed name, called or not, as the file writes it (through the import that binds it, or a builtin by its "
       "bare name where nothing shadows it). Silent on a name reached through a variable or `getattr`, a method of an "
       "object, an annotation, and what a helper in another file does: a ban list, not a proof of purity",
       "forbidden:\n  pure: [time.time, socket]\n" + _in_part("forbidden: pure\n"), rules=("forbidden",)),
    _k(PROFILE, "layers", "chains of parts from the inside out",
       "a map {<name>: [<part>, ...]}: no part imports one after it in its chain; refused at load when a "
       "`may_import` breaks a chain", "layers:\n  stack: [core, documents]\n" + _TWO),
    _k(PROFILE, "tiers", "the kinds of test, in the order their litmus tests run",
       "a map {<tier>: {...}}; with tiers, every part names its `tier` or says why it is `untested`; needs `testing`. "
       "Tests mirror the app: tests/<path> for the app's <path>, and a test file has the tier of the part its folder "
       "mirrors (a folder that mirrors no part belongs to the tier whose `folder` holds it). A test imports only the "
       "part its folder mirrors and what that may import, a bare name meaning the instance it mirrors, and other test "
       "code only from its own folder; a test in no tier is a violation. Every folder below tests/<a repeating "
       "folder>/ mirrors a folder of the app",
       _tiered("proves: a rule of the documents\n"), rules=("tiers", "test-tree"), opens=TIER),
    _k(PROFILE, "fakes", "the folder of the test fakes, and what they stand in for",
       "a map {folder, for, prefix}", _TWO + _FAKES, rules=("stand-ins", "dead-code"), opens=FAKES),
    _k(PROFILE, "guards", "the pre-built checks in use",
       "a map {<guard>: {...}}: a guard left out is off; `xarch profile explain guards.<guard>` says what one checks",
       "guards:\n  no-comments: {}\n  no-duplicates: {min_statements: 6}\n", opens=GUARD),
    _k(PROFILE, "excluded", "folders below the app that are not its source",
       "a map {<folder>: <reason>}: a path below the app, never a folder of the layout; no check reads a Python file "
       "below one (`closed-tree` and the `ungoverned` list leave it out); `check` lists each under `enforcement` and "
       "`where` says so; not a finding for `--strict`",
       "excluded:\n  generated: written by a tool, not by hand\n", rules=()),
    _k(PROFILE, "hints", "your own advice for a rule",
       "a map {<rule id>: <text>}: shown after the built-in fix of a violation of that rule, as a `hint:` line in the "
       "text output and `hint` in the JSON; an id that is no rule of `check` is refused when the profile loads",
       "hints:\n  rules: Ask the maintainer before adding an import.\n", False, False),
    _k(PROFILE, "files", "the files `init` writes besides the docs",
       "a map {<path>: <from> or {from, pinned, fill}}: `from` is a file or folder next to the profile",
       "files:\n  AGENTS.md: agents.md\n", opens=FILE),
    _k(PROFILE, "docs", "everything that only fills the generated docs",
       "a map {entry, pages, naming, examples, example_notes}", "docs:\n  entry: documents\n", False, False,
       opens=DOCS),

    _k(PART, "path", "where the part lives below the app",
       "a folder, or a file when its last step holds a dot; a step written `<word>` is a repeating folder, one "
       "per name: a profile may have several, each with a word of its own and one parent, and a path holds one",
       "parts:\n  store:\n    path: units/<unit>/store\n    role: saves the documents of one unit\n",
       True, rules=("structure", "rules")),
    _k(PART, "role", "what the part is for, in one line", "one line of text: the note of its folder in the docs tree",
       _in_part("role: saves and loads documents\n"), True, False),
    _k(PART, "litmus", "the question that tells code belongs here", "text, ideally a yes-or-no question",
       _in_part("litmus: Does it save or load a document?\n"), False, False),
    _k(PART, "may_import", "what the part may import besides itself",
       "[<part>, <part>@any, <part>/<path>, <part>:<pattern>, ...] or everything: a bare name is that part in the "
       "importer's own instance (a part of another repeating folder has none: write `@any`), `@any` any instance, "
       "`/<path>` only what lies below it, `:<pattern>` only the names that match the pattern (`*` for any text, "
       "such as `core/ids:*Id`): `from <there> import <name>` for each name, never the file as a whole, and a "
       "file of the tests is not narrowed; a part may always import itself, so a target that only says so is refused",
       _TWO, rules=("rules",)),
    _k(PART, "must_import", "what each file of the part has to reach",
       "[<target>, ...] written as `may_import` writes them, each one the part may import: each file imports one "
       "of them, or an outside package (top-level, neither standard library nor the app's own, whatever `libraries` "
       "says), or imports a file of its own part that does, however far the chain; files that only import each other "
       "meet nothing. Exempt: `__init__.py` and a file with no function or method holding a real statement (types, "
       "constants, Protocol stubs). A failing file is reported once, as a whole", _in_two("must_import: [core]\n"),
       rules=("must-import",)),
    _k(PART, "types_only", "the parts its files may use only as types",
       "[<part>, ...], each one `may_import` allows: a file of the part may import them to annotate, and for "
       "`isinstance` and exception matching, but never call what it imports from them (`X(...)`, `m.X(...)`, "
       "`X.build(...)`) nor reference one of their top-level functions at all; read through absolute imports "
       "only, as `tiers.<tier>.types_only` reads a test", _in_two("types_only: [core]\n"), rules=("types-only",)),
    _k(PART, "holds", "what the files of the part define at the top level",
       "classes or functions. classes: no file of the part defines a public function at the top level (a name that "
       "does not start with `_`). functions: no file of the part defines a public class at the top level, but for an "
       "exception class (one that derives from a builtin exception, directly or through classes of the app) and a "
       "record (a class with no method of its own, dunder methods aside) that a top-level function of the same "
       "file names in its return annotation. A package file (`__init__.py`) is exempt. Each one is listed as "
       "`weak` in the enforcement section, and fails `check --strict` only", _in_part("holds: classes\n"),
       rules=("holds",)),
    _k(PART, "no_callbacks", "its code calls none of its own parameters",
       "true: no function, method or nested function of the part calls, by its bare name, a parameter of a function "
       "it lies in that is annotated as a callable (`Callable` of typing or collections.abc, alone, subscripted, in "
       "a union or `Optional`), as in `check(path)` for `check: Callable[[str], bool]`. Not read: the first "
       "parameter of a method (`self`, `cls`; a staticmethod has none), a parameter with no such annotation, one "
       "passed on (`sorted(rows, key=key)`), one whose method is called (`p.read()`), and one the body rebinds",
       _in_part("no_callbacks: true\n"), rules=("no-callbacks",)),
    _k(PART, "names", "how the classes of the part are named",
       "a pattern, or a list of them, with `*` for any text: every public class (a name that does not start with "
       "`_`) defined at the top level in a file of the part matches one of them", _in_part('names: "*Store"\n'),
       rules=("names",)),
    _k(PART, "built_by", "the only parts that may build its classes",
       "[<part>, ...]: only code of those parts calls the constructor of a class defined at the top level in a file "
       "of this part, `X(...)` or `m.X(...)`, read through absolute imports; code of this part counts as any other, "
       "and tests are not read. Silent on a class reached through a package file that re-exports it, built in its "
       "own file, or built through a variable or a parameter", _in_two("built_by: [core]\n"), rules=("built-by",)),
    _k(PART, "libraries", "the outside packages the part may import",
       "[<package>, ...] by top-level name, or everything; none by default; the standard library is always allowed and "
       "tests are not checked", _in_part("libraries: [yaml]\n"),
       rules=("libraries",)),
    _k(PART, "forbidden", "the list of names the part may not use",
       "the name of a top-level `forbidden` list", "forbidden:\n  pure: [time.time, socket]\n"
       + _in_part("forbidden: pure\n"), rules=("forbidden",)),
    _k(PART, "tier", "the tier whose tests cover the part",
       "the name of a tier; one tier per part; with `tiers`, a part names its `tier` or is `untested`",
       _tiered("{}\n").replace("  unit:\n    {}\n", "  unit: {}\n"), rules=("tiers",)),
    _k(PART, "untested", "why no tier tests the part", "one line of text", _in_part("untested: it only wires the app\n"),
       rules=()),
    _k(PART, "package_only", "the part is imported only as a package",
       "true: from outside the part, import the package, never one of its files", _in_part("package_only: true\n"),
       rules=("package-only",)),
    _k(PART, "folders", "the folders below the part that the layout shows",
       "{<folder>: <note>} or [<folder>, ...]", _in_part("folders:\n  schemas: the table definitions\n"),
       rules=("structure",)),

    _k(TIER, "proves", "what its tests prove, in one line", "one line of text", _tiered("proves: a rule of the documents\n"),
       False, False),
    _k(TIER, "litmus", "the question that tells a test belongs to the tier", "text, ideally a yes-or-no question",
       _tiered("litmus: Does it call one rule directly and check its answer?\n"), False, False),
    _k(TIER, "apply_forbidden", "its tests keep to the forbidden list of the part they mirror",
       "true or false", _tiered("apply_forbidden: true\n"), rules=("forbidden",)),
    _k(TIER, "types_only", "the parts its tests may import only as types",
       "[<part>, ...]: a test may import them to annotate, never to call: `def build(c: Controller)` is fine, "
       "`Controller(...)` is not; a plain function of such a part may not be referenced at all, while "
       "`isinstance`, exception matching and enum members stay allowed", _tiered("types_only: [documents]\n"),
       rules=("types-only",)),
    _k(TIER, "must_import", "what each of its test files has to reach",
       "[<part>, ...]: each test file of the tier (a file whose name `testing.files` matches) imports from one of "
       "those parts, in any instance, or imports test code that is no test file and does, however far the chain "
       "goes; a test file with no function holding a real statement is exempt, and a file failing is reported once, "
       "as a whole. Silent on what a test is handed without importing it, such as a fixture",
       _tiered("must_import: [documents]\n"), rules=("must-import",)),
    _k(TIER, "folder", "a folder of tests that mirror no part",
       "a folder below the tests folder, for a tier whose tests mirror no part of the app",
       _tier_folder(""), rules=("tiers", "test-tree")),
    _k(TIER, "may_import", "what the tests in its folder may import of the app",
       "as a part's `may_import`; only for a tier with a `folder`", _tier_folder("may_import: everything\n"),
       rules=("tiers",)),
    _k(TIER, "docs", "what only fills the generated docs",
       "a map {subject, may_touch, one_file_per, cases_from, data, example, helpers}",
       _tiered("docs:\n  may_touch: temporary folders\n"), False, False, opens=TIER_DOCS),

    _k(TIER_DOCS, "subject", "the Subject cell, in place of the parts of the tier", "one line of text",
       _tiered("docs:\n  subject: the documents\n"), False, False),
    _k(TIER_DOCS, "may_touch", "what its tests may touch", "one line of text",
       _tiered("docs:\n  may_touch: temporary folders\n"), False, False),
    _k(TIER_DOCS, "one_file_per", "what one test file covers", "one line of text",
       _tiered("docs:\n  one_file_per: use case\n"), False, False),
    _k(TIER_DOCS, "cases_from", "where its cases come from", "one line of text",
       _tiered("docs:\n  cases_from: the rule's branches\n"), False, False),
    _k(TIER_DOCS, "data", "where its test data comes from", "one line of text",
       _tiered("docs:\n  data: built in the test\n"), False, False),
    _k(TIER_DOCS, "example", "its example test", "a path in an example project listed in `docs.examples`",
       "docs:\n  examples: [examples]\n" + _tiered("docs:\n  example: tests/documents/check_documents.py\n"), False, False),
    _k(TIER_DOCS, "helpers", "the files its tests share", "[<path in an example project>, ...]",
       "docs:\n  examples: [examples]\n" + _tiered("docs:\n  helpers: [tests/documents/builders.py]\n"), False, False),

    _k(TESTING, "files", "patterns of a test file's name", "a list of .py names with `*` for any text",
       _tests(""), True, rules=("tiers", "test-tree")),
    _k(TESTING, "functions", "the pattern of a test function's name", "a name with `*` for any text",
       _tests(""), True, rules=("scenario-coverage", "stand-ins")),
    _k(TESTING, "skips", "what skips a test or expects it to fail",
       "dotted names: `check` counts each use under `enforcement`", _tests("skips: [checks.skip, checks.expect_fail]\n"),
       rules=()),
    _k(TESTING, "table", "how a test function holds a table of cases", "a map {decorator, row, id, keywords}",
       _TESTING + _TABLE_BLOCK, rules=("scenario-coverage",), opens=TABLE),
    _k(TESTING, "mocks", "how a mock is built", "a map {calls, autospec, spec_keywords, fixtures}",
       _TESTING + "  mocks:\n" + _MOCKS, rules=("stand-ins",), opens=MOCKS),

    _k(TABLE, "decorator", "the decorator that holds the rows", "a dotted name", _TESTING + _TABLE_BLOCK, True,
       rules=("scenario-coverage",)),
    _k(TABLE, "row", "a row of the table", "a dotted name", _TESTING + _TABLE_BLOCK, True, rules=("scenario-coverage",)),
    _k(TABLE, "id", "the keyword that gives a row its id", "a keyword name", _TESTING + _TABLE_BLOCK, True,
       rules=("scenario-coverage",)),
    _k(TABLE, "keywords", "the two keywords of the decorator's arguments", "[<cases name>, <rows name>]",
       _TESTING + _TABLE_BLOCK + "    keywords: [names, rows]\n", rules=("scenario-coverage",)),

    _k(MOCKS, "calls", "the calls that build a mock", "a list of dotted names", _TESTING + "  mocks:\n" + _MOCKS, True,
       rules=("stand-ins",)),
    _k(MOCKS, "autospec", "the calls that build a mock from a spec argument", "a list of dotted names",
       _TESTING + "  mocks:\n" + _MOCKS + "    autospec: [doubles.make_from]\n", rules=("stand-ins",)),
    _k(MOCKS, "spec_keywords", "the keywords a mock is given its spec by", "a list of keyword names",
       _TESTING + "  mocks:\n" + _MOCKS, True, rules=("stand-ins",)),
    _k(MOCKS, "fixtures", "test parameters whose methods build mocks", "a map {<parameter>: {calls, autospec}}",
       _TESTING + "  mocks:\n" + _MOCKS + "    fixtures:\n      maker:\n        calls: [build]\n", rules=("stand-ins",),
       opens=FIXTURE),

    _k(FIXTURE, "calls", "the methods that build a mock", "a list of method names",
       _TESTING + "  mocks:\n" + _MOCKS + "    fixtures:\n      maker:\n        calls: [build]\n", True,
       rules=("stand-ins",)),
    _k(FIXTURE, "autospec", "the methods that build a mock from a spec argument", "a list of method names",
       _TESTING + "  mocks:\n" + _MOCKS + "    fixtures:\n      maker:\n        calls: [build]\n"
       "        autospec: [build_from]\n", rules=("stand-ins",)),

    _k(FAKES, "folder", "the folder of the fakes", "a folder below the tests folder", _TWO + _FAKES, True,
       rules=("stand-ins", "dead-code")),
    _k(FAKES, "for", "the parts whose Protocols the fakes stand in for", "[<part>, ...]", _TWO + _FAKES, True,
       rules=("stand-ins", "dead-code")),
    _k(FAKES, "prefix", "how a fake's name starts", "the start of a class name: the fake of DocumentRepo is "
       "FakeDocumentRepo", _TWO + _FAKES, rules=("stand-ins", "dead-code")),

    _guard("scenario-coverage", "every result of a use case has a row", _COVERAGE_GUARD),
    _guard("no-comments", "no `#` comments in the app or its tests", _guarded("no-comments: {}\n")),
    _guard("stand-ins", "a Protocol is faked, or mocked with a spec", _STAND_INS + _guarded("stand-ins: {}\n")),
    _guard("closed-tree", "every file lies in a part", _guarded("closed-tree: {}\n")),
    _guard("no-duplicates", "no two functions with the same code", _guarded("no-duplicates: {min_statements: 6}\n")),
    _guard("dead-code", "no Protocol nothing names, no fake no test uses", _TWO + _FAKES + _guarded("dead-code: {}\n")),
    _guard("pass-through", "a method that only forwards is listed", _TWO + _guarded("pass-through:\n  parts: [documents]\n")),
    _guard("private-imports", "no name starting with `_` is imported from another file",
           _guarded("private-imports: {}\n")),

    _k(SCENARIO_COVERAGE, "results", "the part holding the result unions", "the name of a part", _COVERAGE_GUARD, True,
       rules=("scenario-coverage",)),
    _k(SCENARIO_COVERAGE, "tier", "the tier whose test files hold the tables", "the name of a tier", _COVERAGE_GUARD, True,
       rules=("scenario-coverage",)),
    _k(SCENARIO_COVERAGE, "suffix", "how a union's name ends", "text, such as Result", _COVERAGE_GUARD, True,
       rules=("scenario-coverage",)),
    _k(SCENARIO_COVERAGE, "columns", "the three parameter names of a table", "[<state>, <command>, <result>]",
       _COVERAGE_GUARD, True, rules=("scenario-coverage",)),
    _k(SCENARIO_COVERAGE, "file", "the name of a use case's test file", "a name holding {name} once, for the use case",
       _COVERAGE_GUARD, True, rules=("scenario-coverage",)),

    _k(NO_DUPLICATES, "min_statements", "the fewest statements that count", "a whole number, 4 when left out",
       _guarded("no-duplicates: {min_statements: 6}\n"), rules=("no-duplicates",)),

    _k(DEAD_CODE, "untested", "also list the files no test of their tier reaches",
       "true or false: every file of a part that has a `tier`, which no test code of that tier (a file below the "
       "tests folder that the tier holds, test or not) imports, directly or through files of parts of that same tier "
       "that it reaches, is listed as `weak` in the enforcement section and fails `check --strict` only. Exempt: a "
       "package file, and a file with no function or method holding a real statement (types, constants, Protocol "
       "stubs). Read only with a tests folder", _TWO + _FAKES + _guarded("dead-code: {untested: true}\n"),
       rules=("dead-code",)),

    _k(PASS_THROUGH, "parts", "the parts whose forwarding methods are listed", "[<part>, ...]",
       _TWO + _guarded("pass-through:\n  parts: [documents]\n"), True, rules=("pass-through",)),

    _k(DOCS, "entry", "the part that is the entry point", "the name of a part", _docs("entry: documents\n"), False, False),
    _k(DOCS, "pages", "the project docs `init` writes below docs/project/",
       "a map {<path>: <from> or {from, note}}", _PAGES, False, False, opens=PAGE),
    _k(DOCS, "naming", "the naming table of the docs", "a list of {kind, where, pattern, example}",
       _docs("naming:\n  - kind: store\n    where: [store]\n    pattern: <Thing>Store\n    example: [DocumentStore]\n"),
       False, False, opens=NAMING),
    _k(DOCS, "examples", "folders next to the profile, each an example project",
       "[<folder>, ...]: a template quotes one of its files by its path with {{example:<path>}}",
       _docs("examples: [examples]\n"), False, False),
    _k(DOCS, "example_notes", "a note for an example", "a map {<path>: <note>}, shown after the example's path",
       _docs("examples: [examples]\nexample_notes:\n  src/documents.py: the documents\n"), False, False),

    _k(PAGE, "from", "the template file, next to the profile", "a path", _PAGES, False, False),
    _k(PAGE, "note", "shown after its line in the docs tree", "one line of text", _PAGES, False, False),

    _k(NAMING, "kind", "what is named", "text, such as store", _docs(
        "naming:\n  - kind: store\n    where: [store]\n    pattern: <Thing>Store\n    example: [DocumentStore]\n"),
       True, False),
    _k(NAMING, "where", "the folders it lives in", "text or a list of text", _docs(
        "naming:\n  - kind: store\n    where: [store]\n    pattern: <Thing>Store\n    example: [DocumentStore]\n"),
       True, False),
    _k(NAMING, "pattern", "how it is named", "text", _docs(
        "naming:\n  - kind: store\n    where: [store]\n    pattern: <Thing>Store\n    example: [DocumentStore]\n"),
       True, False),
    _k(NAMING, "example", "names that follow the pattern", "text or a list of text", _docs(
        "naming:\n  - kind: store\n    where: [store]\n    pattern: <Thing>Store\n    example: [DocumentStore]\n"),
       True, False),

    _k(FILE, "from", "the template file, or the folder of a path ending in /",
       "a path next to the profile: a file, or a folder when the key ends in /",
       "files:\n  tests/rules.py:\n    from: guard.py\n", True),
    _k(FILE, "pinned", "`check` reports the file when it differs",
       "true: the project keeps the file as `init` writes it", "files:\n  tests/rules.py:\n    from: guard.py\n    pinned: true\n"),
    _k(FILE, "fill", "whether {{app}} is filled in", "false: the bytes are copied unchanged",
       "files:\n  tests/rules.py:\n    from: guard.py\n    fill: false\n"),
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
