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
    DOCS,
    EVAL,
    EVALS,
    FAKES,
    FILE,
    FIXTURE,
    GUARD,
    MOCKS,
    NAMING,
    NO_DUPLICATES,
    NO_TWINS,
    PAGE,
    PART,
    PART_USES,
    PASS_THROUGH,
    PLACEMENT,
    PROFILE,
    READ_BY_REVIEW,
    REVIEW,
    SCENARIO_COVERAGE,
    TABLE,
    TESTING,
    TIER,
    TIER_DOCS,
    TIER_USES,
    Key,
)

_GUARD_SCOPES = {"scenario-coverage": SCENARIO_COVERAGE, "no-duplicates": NO_DUPLICATES, "no-twins": NO_TWINS,
                 "dead-code": DEAD_CODE, "pass-through": PASS_THROUGH}


def _guard(name: str) -> Key:
    return Key(GUARD, name, False, True, (name,), _GUARD_SCOPES.get(name, ""))


_KEYS: tuple[Key, ...] = (
    Key(PROFILE, "name", True, False),
    Key(PROFILE, "based_on", False, False, choices=CHOICE_BUNDLED),
    Key(PROFILE, "language", choices=CHOICE_LANGUAGES),
    Key(PROFILE, "testing", rules=("tiers", "test-tree"), opens=TESTING, choices=CHOICE_PRESETS),
    Key(PROFILE, "parts", True, rules=("structure", "rules"), opens=PART),
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

    Key(PART, "path", True, rules=("structure", "rules")),
    Key(PART, "role", True, False),
    Key(PART, "litmus", False, False),
    Key(PART, "may_import", rules=("rules",)),
    Key(PART, "must_import", rules=("must-import",)),
    Key(PART, "types_only", rules=("types-only",)),
    Key(PART, "holds", rules=("holds",)),
    Key(PART, "immutable", rules=("immutable",)),
    Key(PART, "no_callbacks", rules=("no-callbacks",)),
    Key(PART, "names", rules=("names",)),
    Key(PART, "built_by", rules=("built-by",)),
    Key(PART, "shared", rules=("shared",)),
    Key(PART, "libraries", rules=("libraries",)),
    Key(PART, "uses", opens=PART_USES),
    Key(PART, "tests", rules=("tiers",)),
    Key(PART, "untested"),
    Key(PART, "package_only", rules=("package-only",)),
    Key(PART, "folders", rules=("structure",)),

    Key(PART_USES, "never", rules=("never-use",)),

    Key(TIER, "proves", False, False),
    Key(TIER, "litmus", False, False),
    Key(TIER, "uses", opens=TIER_USES),
    Key(TIER, "plain_tables", rules=("scenario-coverage",)),
    Key(TIER, "types_only", rules=("types-only",)),
    Key(TIER, "must_import", rules=("must-import",)),
    Key(TIER, "folder", rules=("tiers", "test-tree")),
    Key(TIER, "may_import", rules=("tiers",)),
    Key(TIER, "may_also_import", rules=("tiers",)),
    Key(TIER, "docs", False, False, opens=TIER_DOCS),

    Key(TIER_DOCS, "subject", False, False),
    Key(TIER_DOCS, "may_touch", False, False),
    Key(TIER_DOCS, "one_file_per", False, False),
    Key(TIER_DOCS, "cases_from", False, False),
    Key(TIER_DOCS, "data", False, False),
    Key(TIER_DOCS, "example", False, False),
    Key(TIER_DOCS, "helpers", False, False),

    Key(TIER_USES, "apply_never", rules=("never-use",)),

    Key(TESTING, "files", True, rules=("tiers", "test-tree")),
    Key(TESTING, "functions", True, rules=("scenario-coverage", "stand-ins")),
    Key(TESTING, "skips"),
    Key(TESTING, "table", rules=("scenario-coverage",), opens=TABLE),
    Key(TESTING, "mocks", rules=("stand-ins",), opens=MOCKS),

    Key(TABLE, "decorator", True, rules=("scenario-coverage",)),
    Key(TABLE, "row", True, rules=("scenario-coverage",)),
    Key(TABLE, "id", True, rules=("scenario-coverage",)),
    Key(TABLE, "keywords", rules=("scenario-coverage",)),

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
    _guard("private-imports"),

    Key(SCENARIO_COVERAGE, "results", True, rules=("scenario-coverage",)),
    Key(SCENARIO_COVERAGE, "tier", True, rules=("scenario-coverage",)),
    Key(SCENARIO_COVERAGE, "suffix", True, rules=("scenario-coverage",)),
    Key(SCENARIO_COVERAGE, "columns", True, rules=("scenario-coverage",)),
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
_FORBIDDEN = (*_IMPORTS, "use", "method_call")
_TYPES_ONLY = ("call", "use", "module_functions")
NEEDS: dict[str, tuple[str, ...]] = {
    "parts.<part>.may_import": _IMPORTS,
    "parts.<part>.must_import": (*_IMPORTS, "import.standard", "function.statements", "file"),
    "parts.<part>.types_only": _TYPES_ONLY,
    "parts.<part>.holds": ("class", "class.methods", "class.exception", "function", "function.returns"),
    "parts.<part>.no_callbacks": ("callback",),
    "parts.<part>.immutable": ("class", "class.exception", "class.immutable"),
    "parts.<part>.names": ("class",),
    "parts.<part>.built_by": ("class", "call"),
    "parts.<part>.shared": (*_IMPORTS, "import.mentioned", "use", "class", "class.named", "function", "function.named",
                            "module_functions", "constant"),
    "parts.<part>.libraries": (*_IMPORTS, "import.standard"),
    "parts.<part>.uses.never": _FORBIDDEN,
    "parts.<part>.package_only": _IMPORTS,
    "reserved": (*_IMPORTS, "import.standard"),
    "tiers": (*_IMPORTS, "file"),
    "tiers.<tier>.uses.apply_never": _FORBIDDEN,
    "tiers.<tier>.types_only": _TYPES_ONLY,
    "tiers.<tier>.must_import": (*_IMPORTS, "function.statements", "file"),
    "tiers.<tier>.plain_tables": ("function.tables", "function.blocks", "function.expressions"),
    "tiers.<tier>.may_import": _IMPORTS,
    "tiers.<tier>.may_also_import": _IMPORTS,
    "testing.skips": ("use",),
    "testing.table": ("function.tables",),
    "testing.mocks": ("call", "parameter_call"),
    "guards.scenario-coverage": ("union", "function.tables", "function.blocks", "function.expressions",
                                 "function.asserts", "function.mentions"),
    "guards.no-comments": ("comment",),
    "guards.stand-ins": ("class", "class.methods", "class.attributes", "call", "parameter_call"),
    "guards.closed-tree": ("file",),
    "guards.no-duplicates": ("function", "function.statements", "function.shape"),
    "guards.no-twins": ("class", "class.fields"),
    "guards.no-twins.min_renamed": ("class", "class.fields", "class.types"),
    "guards.no-twins.translated": ("class", "class.fields", "call", "function", "function.named", *_IMPORTS),
    "guards.dead-code": ("class", "named"),
    "guards.dead-code.untested": (*_IMPORTS, "function.statements", "class", "class.exception", "function", "file"),
    "guards.dead-code.tests_only": ("class", "class.exception", "function", "named"),
    "guards.dead-code.known": ("class", "class.exception", "function", "function.named", "constant", "named", *_IMPORTS),
    "guards.pass-through": ("function", "function.forwards"),
    "guards.private-imports": _IMPORTS,
}
"""The facts of the source each key that configures a check needs, by its address."""

KEYS: tuple[Key, ...] = tuple(replace(key, needs=NEEDS.get(key.address, ())) for key in _KEYS)
"""Every key of every scope, in the order a file writes them."""

SLOTS: tuple[Key, ...] = tuple(
    Key(EVAL, slot, slot in ("ask", "answer", "reads", "message", "fix", "examples"), False, read_by=READ_BY_REVIEW)
    for slot in ("ask", "answer", "yes", "no", "reads", "in", "keep", "line", "message", "fix", "examples"))
"""The slots of an eval of the profile's own, under an id of its own (see HELD), in the order a file writes them."""
