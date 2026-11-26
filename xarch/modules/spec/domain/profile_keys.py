"""The kinds of value the keys of a profile file are described by: a key of the table, the text
`xarch profile explain` says for it, and the catalogue of those texts.

A key sits in a scope, a kind of mapping, such as a part, written as its address in the file (`parts.<part>`). The table
of keys says whether the profile needs one, whether it is enforced (changes what `xarch check` does, through the rule ids
it lists) or documentary (only fills the generated docs or reports), or read by another command than `check` only,
and the scope a key that holds keys opens. Its text, read from a data file shipped with xarch, says its meaning in a
few words, what it accepts, and a short example: a fragment of a profile that loads once merged into the smallest one.
"""
from __future__ import annotations

from dataclasses import dataclass, field

PROFILE = "profile"
PART = "part"
PART_USES = "part.uses"
PART_LITMUS = "part.litmus"
PART_IMPORTS = "part.imports"
PART_IMPORTS_MAY = "part.imports.may"
PART_HOLDS = "part.holds"
PART_HOLDS_CLASSES = "part.holds.classes"
PART_HOLDS_FUNCTIONS = "part.holds.functions"
PART_HOLDS_RECORDS = "part.holds.records"
PART_HOLDS_EXCEPTIONS = "part.holds.exceptions"
LAYER = "layer"
TIER = "tier"
TIER_DOCS = "tier.docs"
TIER_LITMUS = "tier.litmus"
TIER_USES = "tier.uses"
TIER_IMPORTS = "tier.imports"
TESTING = "testing"
TABLES = "testing.tables"
DECLARED = "testing.declared"
MOCKS = "testing.mocks"
MOCK_SPECS = "testing.mocks.specs"
FIXTURE = "testing.fixture"
FAKES = "fakes"
STRUCTURE = "structure"
COUNTERPARTS = "counterparts"
COUNTERPART = "counterparts.<id>"
GUARD = "guard"
SCENARIO_COVERAGE = "guard.scenario-coverage"
NO_DUPLICATES = "guard.no-duplicates"
NO_TWINS = "guard.no-twins"
DEAD_CODE = "guard.dead-code"
PASS_THROUGH = "guard.pass-through"
NO_CALLBACKS = "guard.no-callbacks"
DOCS = "docs"
PAGE = "docs.page"
NAMING = "docs.naming"
FILE = "file"
REVIEW = "review"
EVALS = "evals"
PLACEMENT = "evals.placement"
EVAL = "evals.<id>"

SCOPES = {
    PROFILE: "the file",
    PART: "parts.<part>",
    PART_USES: "parts.<part>.uses",
    PART_LITMUS: "parts.<part>.litmus[]",
    PART_IMPORTS: "parts.<part>.imports",
    PART_IMPORTS_MAY: "parts.<part>.imports.may",
    PART_HOLDS: "parts.<part>.holds",
    PART_HOLDS_CLASSES: "parts.<part>.holds.classes",
    PART_HOLDS_FUNCTIONS: "parts.<part>.holds.functions",
    PART_HOLDS_RECORDS: "parts.<part>.holds.records",
    PART_HOLDS_EXCEPTIONS: "parts.<part>.holds.exceptions",
    LAYER: "layers.<layer>",
    TIER: "tiers.<tier>",
    TIER_DOCS: "tiers.<tier>.docs",
    TIER_LITMUS: "tiers.<tier>.litmus[]",
    TIER_USES: "tiers.<tier>.uses",
    TIER_IMPORTS: "tiers.<tier>.imports",
    TESTING: "testing",
    TABLES: "testing.tables[]",
    DECLARED: "testing.declared[]",
    MOCKS: "testing.mocks",
    MOCK_SPECS: "testing.mocks.specs[]",
    FIXTURE: "testing.mocks.fixtures.<parameter>",
    FAKES: "fakes",
    STRUCTURE: "structure",
    COUNTERPARTS: "counterparts",
    GUARD: "guards",
    SCENARIO_COVERAGE: "guards.scenario-coverage",
    NO_DUPLICATES: "guards.no-duplicates",
    NO_TWINS: "guards.no-twins",
    DEAD_CODE: "guards.dead-code",
    PASS_THROUGH: "guards.pass-through",
    NO_CALLBACKS: "guards.no-callbacks",
    DOCS: "docs",
    PAGE: "docs.pages.<path>",
    NAMING: "docs.naming[]",
    FILE: "files.<path>",
    REVIEW: "review",
    EVALS: "evals",
    PLACEMENT: "evals.placement",
}
"""Each scope's address in the file."""
HELD = {EVAL: EVALS, COUNTERPART: COUNTERPARTS}
"""The scopes of an entry of a map the profile names by ids of its own, which no key opens (its address is the
scope's own), each with the scope of the map that holds it: its slots are listed with the keys of that map."""
RULE_ID = "rule-id"
"""The scope of a rule id written as a key of `hints`: not a key of the format, so it has no address."""

CHOICE_BUNDLED = "bundled"
CHOICE_PRESETS = "presets"
CHOICE_LANGUAGES = "languages"
"""What a key may name from a list xarch ships: the bundled profiles, the `testing` presets or the languages."""
READ_BY_REVIEW = "review"
"""The command other than `check` that reads a key: `xarch review`, which reads what it may send and how it reads
what it asks."""


@dataclass(frozen=True)
class Key:
    """One key: where it sits, whether the profile needs it, and whether `check` enforces it.

    scope: one of SCOPES
    required: the profile is refused without it
    enforced: it changes what `xarch check` does; False: it only feeds the generated docs or a report
    rules: the rule ids of `check` the key feeds; none for a key the loader alone enforces
    opens: the scope of the keys its value holds
    choices: CHOICE_BUNDLED, CHOICE_PRESETS or CHOICE_LANGUAGES when it names something from a list xarch ships;
        `<bundled>`, `<preset>` and `<language>` in the example of its text stand for the first of that list
    needs: the facts of the source (see capabilities) the check it configures reads: a profile that sets it is
        refused when its language's reader does not supply one of them
    read_by: READ_BY_REVIEW for a key that `check` never reads and another command does; "" for every other
    when_supplied: the facts of needs its check reads only when the language supplies them: a profile that sets the
        key is not refused for one the language does not supply, and the check then reads less, which without says
        in a few words
    """
    scope: str
    name: str
    required: bool = False
    enforced: bool = True
    rules: tuple[str, ...] = ()
    opens: str = ""
    choices: str = ""
    needs: tuple[str, ...] = ()
    read_by: str = ""
    when_supplied: tuple[str, ...] = ()
    without: str = ""

    @property
    def where(self) -> str:
        return SCOPES.get(self.scope, self.scope)

    @property
    def address(self) -> str:
        return self.name if self.scope == PROFILE else f"{self.where}.{self.name}"


@dataclass(frozen=True)
class KeyText:
    """What `xarch profile explain` says for one key, before the words of a language are put in.

    meaning: a few words, what the key is for
    accepts: what to write, and what it does
    example: a fragment of a profile that uses the key; merged into the smallest profile it loads
    """
    meaning: str
    accepts: str
    example: str


@dataclass(frozen=True)
class Catalogue:
    """The texts of the format: each key's, by its address; the symbols a profile writes in paths and imports, each with
    what it means; the smallest valid profile (one part, no rule, no test), as text; and each slot's of an eval of
    the profile's own, by its address."""
    texts: dict[str, KeyText]
    symbols: tuple[tuple[str, str], ...]
    smallest: str
    slots: dict[str, KeyText] = field(default_factory=dict)

    def text(self, address: str) -> KeyText:
        """The text of the key, or of the slot, at the address."""
        return self.texts[address] if address in self.texts else self.slots[address]


@dataclass(frozen=True)
class Retired:
    """A name xarch no longer reads, or a value it no longer reads under a key it still has, and what a profile writes
    instead.

    scope: one of SCOPES or HELD (GUARD for a guard's name), or RULE_ID for a rule id written under `hints`
    name: the name as a profile writes it
    text: the whole hint, fixed and one line, said after the name (after the value, for an entry of a value) in the
        refusal, such as "renamed in 0.3.0: write tests"
    value: for an entry of a value, the value the key no longer takes, such as `functions` under holds; "" for an entry
        of a name
    """
    scope: str
    name: str
    text: str
    value: str = ""


RETIRED: tuple[Retired, ...] = (
    Retired(PART, "tier", "renamed in 0.3.0: write tests"),
    Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}"),
    Retired(PART, "path", "moved in 0.3.0: a part is the folder or file it is written as under parts: drop it"),
    Retired(PART, "folders", "moved in 0.3.0: write each folder below the part as a key ending in /, with its note as "
                             "its value"),
    Retired(TIER, "apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}"),
    Retired(PROFILE, "forbidden", "renamed in 0.3.0: write never"),
    Retired(RULE_ID, "forbidden", "renamed in 0.3.0: write never-use"),
    Retired(PART, "never", "a key of uses: write uses: {never: <list>}"),
    Retired(TIER, "apply_never", "a key of uses: write uses: {apply_never: true}"),
    Retired(RULE_ID, "rules", "renamed in 0.3.0: write may-import"),
    Retired(PART, "no_callbacks", "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}"),
    Retired(PART, "immutable", "moved in 0.3.0: write it under the kind it applies to, such as holds: {records: "
                               "{immutable: true}}"),
    Retired(PART, "names", 'moved in 0.3.0: write it under the kind it names, such as holds: {classes: {names: '
                           '"*Service"}}'),
    Retired(PART, "built_by", "moved in 0.3.0: write holds: {classes: {built_by: [<part>, ...]}}"),
    Retired(PART_HOLDS_FUNCTIONS, "immutable", "a setting of classes and records"),
    Retired(PART_HOLDS_FUNCTIONS, "built_by", "a setting of classes"),
    Retired(PART_HOLDS_RECORDS, "built_by", "a setting of classes"),
    Retired(PART_HOLDS_EXCEPTIONS, "immutable", "a setting of classes and records"),
    Retired(PART_HOLDS_EXCEPTIONS, "built_by", "a setting of classes"),
    Retired(PART, "holds", "holds as one word was removed in 0.3.0: write holds: {functions: {}, records: {}, "
                           "exceptions: {}}, which allows what holds: functions allowed", "functions"),
    Retired(PART, "holds", "holds as one word was removed in 0.3.0: write holds: {classes: {}}", "classes"),
    Retired(PART, "may_import", "moved in 0.3.0: write imports: {may: [...]}"),
    Retired(PART, "must_import", "moved in 0.3.0: write imports: {must: [...]}"),
    Retired(PART, "libraries", "moved in 0.3.0: write imports: {libraries: [...]}"),
    Retired(PART, "types_only", "moved in 0.3.0: write it as the mode of its entry in imports.may, such as "
                                "[{parts.ports: types_only}]"),
    Retired(PART_IMPORTS, "never", "a key of uses, beside imports: write uses: {never: <list>}"),
    Retired(PART_IMPORTS, "types_only", "write it as the mode of its entry in imports.may, such as "
                                        "[{parts.ports: types_only}]"),
    Retired(TIER, "may_import", "moved in 0.3.0: write imports: {may: [...]}"),
    Retired(TIER, "may_also_import", "moved in 0.3.0: write imports: {also: [...]}"),
    Retired(TIER, "must_import", "moved in 0.3.0: write imports: {must: [...]}"),
    Retired(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [parts.<part>, ...]}"),
    Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"),
    Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'),
    Retired(MOCKS, "spec_keywords", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"),
    Retired(MOCKS, "spec_position", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"),
)
"""Every key, guard and rule id xarch has retired, and every value a key it still has no longer takes: a profile
writing one is refused with the entry's text."""
