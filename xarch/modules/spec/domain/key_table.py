"""The table of every key of a profile file: the loader reads it for the keys each mapping accepts
and the ones it needs, and `xarch profile explain` reads it for where each key sits, whether it is enforced and through
which rules, and the texts of the format's data file (see key_catalogue) for what each means, accepts and shows."""
from __future__ import annotations

from dataclasses import replace

from xarch.modules.spec.domain.profile_keys import (
    CHOICE_BUNDLED,
    CHOICE_LANGUAGES,
    CHOICE_PRESETS,
    DEAD_CODE,
    DECLARED,
    DOCS,
    EVAL,
    EVALS,
    FAKES,
    FILE,
    FIXTURE,
    GUARD,
    MOCKS,
    NAMING,
    NO_CALLBACKS,
    NO_DUPLICATES,
    NO_TWINS,
    PAGE,
    PART,
    PART_HOLDS,
    PART_HOLDS_CLASSES,
    PART_HOLDS_EXCEPTIONS,
    PART_HOLDS_FUNCTIONS,
    PART_HOLDS_RECORDS,
    PART_IMPORTS,
    PART_IMPORTS_MAY,
    PART_USES,
    PASS_THROUGH,
    PLACEMENT,
    PROFILE,
    READ_BY_REVIEW,
    REVIEW,
    SCENARIO_COVERAGE,
    TABLES,
    TESTING,
    TIER,
    TIER_DOCS,
    TIER_IMPORTS,
    TIER_USES,
    Key,
)

_GUARD_SCOPES = {"scenario-coverage": SCENARIO_COVERAGE, "no-duplicates": NO_DUPLICATES, "no-twins": NO_TWINS,
                 "dead-code": DEAD_CODE, "pass-through": PASS_THROUGH, "no-callbacks": NO_CALLBACKS}


def _guard(name: str) -> Key:
    return Key(GUARD, name, False, True, (name,), _GUARD_SCOPES.get(name, ""))


_KEYS: tuple[Key, ...] = (
    Key(PROFILE, "name", True, False),
    Key(PROFILE, "based_on", False, False, choices=CHOICE_BUNDLED),
    Key(PROFILE, "language", choices=CHOICE_LANGUAGES),
    Key(PROFILE, "testing", rules=("tiers", "test-tree"), opens=TESTING, choices=CHOICE_PRESETS),
    Key(PROFILE, "parts", True, rules=("structure", "may-import"), opens=PART),
    Key(PROFILE, "never", rules=("never-use",)),
    Key(PROFILE, "reserved", rules=("libraries",)),
    Key(PROFILE, "layers"),
    Key(PROFILE, "tiers", rules=("tiers", "test-tree"), opens=TIER),
    Key(PROFILE, "fakes", rules=("stand-ins", "dead-code"), opens=FAKES),
    Key(PROFILE, "guards", opens=GUARD),
    Key(PROFILE, "excluded"),
    Key(PROFILE, "hints", False, False),
    Key(PROFILE, "checks"),
    Key(PROFILE, "files", opens=FILE),
    Key(PROFILE, "docs", False, False, opens=DOCS),
    Key(PROFILE, "review", False, False, opens=REVIEW, read_by=READ_BY_REVIEW),
    Key(PROFILE, "evals", False, False, opens=EVALS, read_by=READ_BY_REVIEW),

    Key(PART, "path", True, rules=("structure", "may-import")),
    Key(PART, "role", True, False),
    Key(PART, "litmus", False, False),
    Key(PART, "imports", rules=("may-import", "must-import", "libraries"), opens=PART_IMPORTS),
    Key(PART, "holds", rules=("holds",), opens=PART_HOLDS, when_supplied=("function.top_level",),
        without="holds reads no top-level functions"),
    Key(PART, "shared", rules=("shared",)),
    Key(PART, "uses", opens=PART_USES),
    Key(PART, "tests", rules=("tiers",)),
    Key(PART, "untested"),
    Key(PART, "package_only", rules=("package-only",)),
    Key(PART, "folders", rules=("structure",)),

    Key(PART_IMPORTS, "may", rules=("may-import",), opens=PART_IMPORTS_MAY),
    Key(PART_IMPORTS, "must", rules=("must-import",)),
    Key(PART_IMPORTS, "libraries", rules=("libraries",)),

    Key(PART_IMPORTS_MAY, "types_only", rules=("types-only",)),

    Key(PART_USES, "never", rules=("never-use",)),

    Key(PART_HOLDS, "classes", rules=("holds",), opens=PART_HOLDS_CLASSES),
    Key(PART_HOLDS, "functions", rules=("holds",), opens=PART_HOLDS_FUNCTIONS),
    Key(PART_HOLDS, "records", rules=("holds",), opens=PART_HOLDS_RECORDS),
    Key(PART_HOLDS, "exceptions", rules=("holds",), opens=PART_HOLDS_EXCEPTIONS),

    Key(PART_HOLDS_CLASSES, "names", rules=("names",)),
    Key(PART_HOLDS_CLASSES, "immutable", rules=("immutable",)),
    Key(PART_HOLDS_CLASSES, "built_by", rules=("built-by",)),

    Key(PART_HOLDS_FUNCTIONS, "names", rules=("names",)),

    Key(PART_HOLDS_RECORDS, "names", rules=("names",)),
    Key(PART_HOLDS_RECORDS, "immutable", rules=("immutable",)),

    Key(PART_HOLDS_EXCEPTIONS, "names", rules=("names",)),

    Key(TIER, "proves", False, False),
    Key(TIER, "litmus", False, False),
    Key(TIER, "uses", opens=TIER_USES),
    Key(TIER, "plain_tables", rules=("scenario-coverage",)),
    Key(TIER, "folder", rules=("tiers", "test-tree")),
    Key(TIER, "imports", rules=("tiers", "must-import", "types-only"), opens=TIER_IMPORTS),
    Key(TIER, "docs", False, False, opens=TIER_DOCS),

    Key(TIER_DOCS, "subject", False, False),
    Key(TIER_DOCS, "may_touch", False, False),
    Key(TIER_DOCS, "one_file_per", False, False),
    Key(TIER_DOCS, "cases_from", False, False),
    Key(TIER_DOCS, "data", False, False),
    Key(TIER_DOCS, "example", False, False),
    Key(TIER_DOCS, "helpers", False, False),

    Key(TIER_USES, "apply_never", rules=("never-use",)),

    Key(TIER_IMPORTS, "may", rules=("tiers",)),
    Key(TIER_IMPORTS, "also", rules=("tiers",)),
    Key(TIER_IMPORTS, "must", rules=("must-import",)),
    Key(TIER_IMPORTS, "types_only", rules=("types-only",)),

    Key(TESTING, "preset", rules=("tiers", "test-tree"), choices=CHOICE_PRESETS),
    Key(TESTING, "files", True, rules=("tiers", "test-tree")),
    Key(TESTING, "declared", True, rules=("scenario-coverage", "stand-ins"), opens=DECLARED),
    Key(TESTING, "globals", rules=("scenario-coverage", "stand-ins")),
    Key(TESTING, "skips"),
    Key(TESTING, "tables", rules=("scenario-coverage",), opens=TABLES),
    Key(TESTING, "mocks", rules=("stand-ins",), opens=MOCKS),

    Key(DECLARED, "function", rules=("scenario-coverage",)),
    Key(DECLARED, "call", rules=("scenario-coverage",)),
    Key(DECLARED, "title", rules=("scenario-coverage",)),
    Key(DECLARED, "body", rules=("scenario-coverage",)),

    Key(TABLES, "decorator", rules=("scenario-coverage",)),
    Key(TABLES, "call", rules=("scenario-coverage",)),
    Key(TABLES, "loop", rules=("scenario-coverage",)),
    Key(TABLES, "columns_from", True, rules=("scenario-coverage",)),
    Key(TABLES, "rows", rules=("scenario-coverage",)),
    Key(TABLES, "row", True, rules=("scenario-coverage",)),
    Key(TABLES, "id", True, rules=("scenario-coverage",)),

    Key(MOCKS, "calls", True, rules=("stand-ins",)),
    Key(MOCKS, "autospec", rules=("stand-ins",)),
    Key(MOCKS, "spec_keywords", True, rules=("stand-ins",)),
    Key(MOCKS, "spec_position", rules=("stand-ins",)),
    Key(MOCKS, "fixtures", rules=("stand-ins",), opens=FIXTURE),

    Key(FIXTURE, "calls", True, rules=("stand-ins",)),
    Key(FIXTURE, "autospec", rules=("stand-ins",)),

    Key(FAKES, "folder", True, rules=("stand-ins", "dead-code")),
    Key(FAKES, "for", True, rules=("stand-ins", "dead-code")),
    Key(FAKES, "prefix", rules=("stand-ins", "dead-code")),

    _guard("scenario-coverage"),
    _guard("no-comments"),
    _guard("stand-ins"),
    _guard("closed-tree"),
    _guard("no-duplicates"),
    _guard("no-twins"),
    _guard("dead-code"),
    _guard("pass-through"),
    _guard("no-callbacks"),
    _guard("private-imports"),

    Key(SCENARIO_COVERAGE, "results", True, rules=("scenario-coverage",)),
    Key(SCENARIO_COVERAGE, "tier", True, rules=("scenario-coverage",)),
    Key(SCENARIO_COVERAGE, "suffix", True, rules=("scenario-coverage",)),
    Key(SCENARIO_COVERAGE, "columns", rules=("scenario-coverage",)),
    Key(SCENARIO_COVERAGE, "file", True, rules=("scenario-coverage",)),

    Key(NO_DUPLICATES, "min_statements", rules=("no-duplicates",)),

    Key(NO_TWINS, "min_fields", rules=("no-twins",)),
    Key(NO_TWINS, "min_renamed", rules=("no-twins",)),
    Key(NO_TWINS, "min_subset", rules=("no-twins",)),
    Key(NO_TWINS, "translated", rules=("no-twins",)),

    Key(DEAD_CODE, "untested", rules=("dead-code",)),
    Key(DEAD_CODE, "tests_only", rules=("dead-code",)),
    Key(DEAD_CODE, "known", rules=("dead-code",)),

    Key(PASS_THROUGH, "parts", True, rules=("pass-through",)),

    Key(NO_CALLBACKS, "parts", True, rules=("no-callbacks",)),

    Key(DOCS, "entry", False, False),
    Key(DOCS, "pages", False, False, opens=PAGE),
    Key(DOCS, "naming", False, False, opens=NAMING),
    Key(DOCS, "examples", False, False),
    Key(DOCS, "example_notes", False, False),

    Key(PAGE, "from", False, False),
    Key(PAGE, "note", False, False),

    Key(NAMING, "kind", True, False),
    Key(NAMING, "where", True, False),
    Key(NAMING, "pattern", True, False),
    Key(NAMING, "example", True, False),

    Key(FILE, "from", True),
    Key(FILE, "pinned"),
    Key(FILE, "fill"),

    Key(REVIEW, "never", False, False, read_by=READ_BY_REVIEW),
    Key(REVIEW, "mask", False, False, read_by=READ_BY_REVIEW),

    Key(EVALS, "placement", False, False, opens=PLACEMENT, read_by=READ_BY_REVIEW),
    Key(PLACEMENT, "lines", False, False, read_by=READ_BY_REVIEW),
    Key(PLACEMENT, "alike", False, False, read_by=READ_BY_REVIEW),
    Key(PLACEMENT, "examples", False, False, read_by=READ_BY_REVIEW),
)

_IMPORTS = ("import", "import.relative")
_NEVER_USE = (*_IMPORTS, "use", "method_call", "import.resolved")
_TYPES_ONLY = ("call", "use", "module_functions", "import.resolved")
NEEDS: dict[str, tuple[str, ...]] = {
    "fakes": ("class", "class.interface"),
    "parts.<part>.imports.may": _IMPORTS,
    "parts.<part>.imports.must": (*_IMPORTS, "import.standard", "function.statements", "file", "file.package"),
    "parts.<part>.imports.may.types_only": _TYPES_ONLY,
    "parts.<part>.holds": ("class", "class.exception", "class.record", "function", "function.top_level", "public"),
    "parts.<part>.holds.classes": ("class", "public"),
    "parts.<part>.holds.classes.names": ("class", "public"),
    "parts.<part>.holds.classes.immutable": ("class", "class.exception", "class.immutable"),
    "parts.<part>.holds.classes.built_by": ("class", "call", "import.resolved"),
    "parts.<part>.holds.functions": ("function", "function.top_level", "public"),
    "parts.<part>.holds.functions.names": ("function", "function.top_level", "public"),
    "parts.<part>.holds.records": ("class", "class.record", "function.top_level"),
    "parts.<part>.holds.records.names": ("class", "class.exception", "class.record", "public"),
    "parts.<part>.holds.records.immutable": ("class", "class.exception", "class.record", "class.immutable"),
    "parts.<part>.holds.exceptions": ("class", "class.exception"),
    "parts.<part>.holds.exceptions.names": ("class", "class.exception", "public"),
    "parts.<part>.shared": (*_IMPORTS, "import.mentioned", "use", "class", "class.named", "function", "function.named",
                            "module_functions", "constant", "import.resolved", "public"),
    "parts.<part>.imports.libraries": (*_IMPORTS, "import.standard"),
    "parts.<part>.uses.never": _NEVER_USE,
    "parts.<part>.package_only": (*_IMPORTS, "file.package"),
    "reserved": (*_IMPORTS, "import.standard"),
    "tiers": (*_IMPORTS, "file"),
    "tiers.<tier>.uses.apply_never": _NEVER_USE,
    "tiers.<tier>.imports.types_only": _TYPES_ONLY,
    "tiers.<tier>.imports.must": (*_IMPORTS, "function.statements", "file"),
    "tiers.<tier>.plain_tables": ("function.blocks", "function.expressions"),
    "tiers.<tier>.imports.may": _IMPORTS,
    "tiers.<tier>.imports.also": _IMPORTS,
    "testing.skips": ("use", "import.resolved"),
    "testing.tables[].decorator": ("function.tables.decorator",),
    "testing.tables[].call": ("function.tables.call",),
    "testing.tables[].loop": ("function.tables.loop",),
    "testing.declared[].function": ("test.function",),
    "testing.declared[].call": ("test.call",),
    "testing.mocks": ("call", "parameter_call", "import.resolved"),
    "guards.scenario-coverage": ("union", "function.blocks", "function.expressions", "function.asserts",
                                 "function.mentions"),
    "guards.no-comments": ("comment", "comment.doc"),
    "guards.stand-ins": ("class", "class.methods", "class.attributes", "class.interface", "call", "parameter_call",
                         "import.resolved"),
    "guards.closed-tree": ("file",),
    "guards.no-duplicates": ("function", "function.statements", "function.shape"),
    "guards.no-twins": ("class", "class.fields", "public"),
    "guards.no-twins.min_renamed": ("class", "class.fields", "class.types", "public"),
    "guards.no-twins.translated": ("class", "class.fields", "call", "function", "function.named", *_IMPORTS,
                                   "import.resolved", "public"),
    "guards.dead-code": ("class", "class.interface", "named"),
    "guards.dead-code.untested": (*_IMPORTS, "function.statements", "class", "class.exception", "function", "file",
                                  "file.package"),
    "guards.dead-code.tests_only": ("class", "class.exception", "function", "function.top_level", "named", "public"),
    "guards.dead-code.known": ("class", "class.exception", "function", "function.named", "constant", "named", *_IMPORTS,
                               "public"),
    "guards.pass-through": ("function", "function.forwards"),
    "guards.no-callbacks": ("callback",),
    "guards.private-imports": (*_IMPORTS, "public"),
}
"""The facts of the source each key that configures a check needs, by its address."""

KEYS: tuple[Key, ...] = tuple(replace(key, needs=NEEDS.get(key.address, ())) for key in _KEYS)
"""Every key of every scope, in the order a file writes them."""

SLOTS: tuple[Key, ...] = tuple(
    Key(EVAL, slot, slot in ("ask", "answer", "reads", "message", "fix", "examples"), False, read_by=READ_BY_REVIEW)
    for slot in ("ask", "answer", "yes", "no", "reads", "in", "keep", "line", "message", "fix", "examples"))
"""The slots of an eval of the profile's own, under an id of its own (see HELD), in the order a file writes them."""
