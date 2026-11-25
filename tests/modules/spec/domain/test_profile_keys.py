"""The table of retired names as xarch ships it: each entry has a scope of the format (or the scope of rule ids), a
name and one line of fixed text, once, and names nothing the format still has; it holds the part key tier, renamed
tests, the old names of never and its keys, those keys written outside uses, and the rule id rules, renamed
may-import, the settings of holds written on the part or under a kind that does not take them, and holds written as
one word, an entry of a value. The table of keys holds holds as a map of kinds, each with its settings, and the facts
each needs."""
from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.key_table import KEYS, NEEDS, SLOTS
from xarch.modules.spec.domain.profile_keys import (
    CHOICE_PRESETS,
    DECLARED,
    HELD,
    MOCK_SPECS,
    MOCKS,
    PART,
    PART_HOLDS,
    PART_HOLDS_CLASSES,
    PART_HOLDS_EXCEPTIONS,
    PART_HOLDS_FUNCTIONS,
    PART_HOLDS_RECORDS,
    PART_IMPORTS,
    PART_IMPORTS_MAY,
    PROFILE,
    RETIRED,
    RULE_ID,
    SCOPES,
    TESTING,
    TIER,
    TIER_IMPORTS,
    Retired,
)


def test_every_entry_has_a_scope_a_name_and_one_line_of_text():
    scopes = {*SCOPES, *HELD, RULE_ID}
    assert [entry for entry in RETIRED if entry.scope not in scopes or not entry.name or not entry.text.strip()
            or "\n" in entry.text] == []


def test_no_two_entries_share_a_scope_a_name_and_a_value():
    assert len({(entry.scope, entry.name, entry.value) for entry in RETIRED}) == len(RETIRED)


def test_no_entry_of_a_key_names_a_key_its_scope_still_has_nor_a_rule_id_xarch_checks():
    known = {(key.scope, key.name) for key in (*KEYS, *SLOTS)} | {(RULE_ID, rule) for rule in RULES}
    assert [entry for entry in RETIRED if not entry.value and (entry.scope, entry.name) in known] == []


def test_an_entry_of_a_value_names_a_key_its_scope_still_has():
    known = {(key.scope, key.name) for key in KEYS}
    assert [(entry.scope, entry.name, entry.value) for entry in RETIRED if entry.value] == [
        (PART, "holds", "functions"), (PART, "holds", "classes")]
    assert all((entry.scope, entry.name) in known for entry in RETIRED if entry.value)


def test_the_names_retired_are_tier_the_old_names_of_never_and_its_keys_written_outside_uses_and_the_rule_id_rules():
    assert RETIRED == (
        Retired(PART, "tier", "renamed in 0.3.0: write tests"),
        Retired(PART, "forbidden", "moved in 0.3.0: write uses: {never: <list>}"),
        Retired(PART, "path", "moved in 0.3.0: a part is the folder or file it is written as under parts: drop it"),
        Retired(PART, "folders", "moved in 0.3.0: write each folder below the part as a key ending in /, with its note "
                                 "as its value"),
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
                                    "[{ports: types_only}]"),
        Retired(PART_IMPORTS, "never", "a key of uses, beside imports: write uses: {never: <list>}"),
        Retired(PART_IMPORTS, "types_only", "write it as the mode of its entry in imports.may, such as "
                                            "[{ports: types_only}]"),
        Retired(TIER, "may_import", "moved in 0.3.0: write imports: {may: [...]}"),
        Retired(TIER, "may_also_import", "moved in 0.3.0: write imports: {also: [...]}"),
        Retired(TIER, "must_import", "moved in 0.3.0: write imports: {must: [...]}"),
        Retired(TIER, "types_only", "moved in 0.3.0: write imports: {types_only: [<part>, ...]}"),
        Retired(TESTING, "table", "moved in 0.3.0: write tables, a list of forms (xarch profile explain testing.tables)"),
        Retired(TESTING, "functions", 'moved in 0.3.0: write declared: [{function: "<pattern>"}]'),
        Retired(MOCKS, "spec_keywords", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"),
        Retired(MOCKS, "spec_position", "moved in 0.3.0: write specs: [{keyword: spec}, {position: 0}]"))


def test_holds_opens_a_scope_of_kinds_each_opening_a_scope_of_the_settings_it_takes():
    def held(scope: str) -> list[tuple[str, str, tuple[str, ...]]]:
        return [(key.name, key.opens, key.rules) for key in KEYS if key.scope == scope]
    holds = next(key for key in KEYS if (key.scope, key.name) == (PART, "holds"))
    assert (holds.opens, holds.rules) == (PART_HOLDS, ("holds",))
    assert held(PART_HOLDS) == [("classes", PART_HOLDS_CLASSES, ("holds",)), ("functions", PART_HOLDS_FUNCTIONS, ("holds",)),
                                ("records", PART_HOLDS_RECORDS, ("holds",)), ("exceptions", PART_HOLDS_EXCEPTIONS, ("holds",))]
    assert held(PART_HOLDS_CLASSES) == [("names", "", ("names",)), ("immutable", "", ("immutable",)),
                                        ("built_by", "", ("built-by",))]
    assert held(PART_HOLDS_FUNCTIONS) == [("names", "", ("names",))]
    assert held(PART_HOLDS_RECORDS) == [("names", "", ("names",)), ("immutable", "", ("immutable",))]
    assert held(PART_HOLDS_EXCEPTIONS) == [("names", "", ("names",))]
    assert [key.name for key in KEYS if key.scope == PART and key.name in ("names", "immutable", "built_by")] == []


def test_each_scope_of_holds_has_its_address_in_the_file():
    assert [SCOPES[scope] for scope in (PART_HOLDS, PART_HOLDS_CLASSES, PART_HOLDS_FUNCTIONS, PART_HOLDS_RECORDS,
                                        PART_HOLDS_EXCEPTIONS)] == [
        "parts.<part>.holds", "parts.<part>.holds.classes", "parts.<part>.holds.functions",
        "parts.<part>.holds.records", "parts.<part>.holds.exceptions"]


def test_each_kind_and_setting_needs_the_facts_its_check_reads():
    assert {address: facts for address, facts in NEEDS.items() if ".holds" in address} == {
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
    }
    assert [address for address in NEEDS if address.endswith((".names", ".immutable", ".built_by"))
            and ".holds." not in address] == []


def test_holds_alone_reads_function_top_level_only_when_the_language_supplies_it():
    assert [(key.address, key.when_supplied, key.without) for key in KEYS if key.when_supplied] == [
        ("parts.<part>.holds", ("function.top_level",), "holds reads no top-level functions")]


def test_imports_opens_a_scope_of_may_must_and_libraries_and_may_opens_the_scope_of_its_mark():
    def names(scope):
        return [key.name for key in KEYS if key.scope == scope]

    imports = next(key for key in KEYS if key.scope == PART and key.name == "imports")
    may = next(key for key in KEYS if key.scope == PART_IMPORTS and key.name == "may")
    assert imports.opens == PART_IMPORTS and imports.rules == ("may-import", "must-import", "libraries")
    assert names(PART_IMPORTS) == ["may", "must", "libraries"]
    assert may.opens == PART_IMPORTS_MAY and names(PART_IMPORTS_MAY) == ["types_only"]
    assert SCOPES[PART_IMPORTS] == "parts.<part>.imports" and SCOPES[PART_IMPORTS_MAY] == "parts.<part>.imports.may"
    assert not {"may_import", "must_import", "libraries", "types_only"} & set(names(PART))
    assert not {"may_import", "must_import", "types_only", "may_also_import"} & set(names(TIER))


def test_the_part_import_keys_need_what_the_keys_they_replace_needed():
    imports = ("import", "import.relative")
    assert NEEDS["parts.<part>.imports.may"] == imports
    assert NEEDS["parts.<part>.imports.must"] == (*imports, "import.standard", "function.statements", "file",
                                                   "file.package")
    assert NEEDS["parts.<part>.imports.libraries"] == (*imports, "import.standard")
    assert NEEDS["parts.<part>.imports.may.types_only"] == ("call", "use", "module_functions", "import.resolved")
    assert "parts.<part>.imports" not in NEEDS
    assert not [address for address in NEEDS if address.startswith("parts.<part>.") and address.count(".") == 2
                and address.rsplit(".", 1)[1] in ("may_import", "must_import", "libraries", "types_only")]


def test_a_tier_s_imports_opens_a_scope_of_may_also_must_and_types_only():
    def held(scope):
        return [(key.name, key.rules) for key in KEYS if key.scope == scope]

    imports = next(key for key in KEYS if (key.scope, key.name) == (TIER, "imports"))
    assert (imports.opens, imports.rules) == (TIER_IMPORTS, ("tiers", "must-import", "types-only"))
    assert held(TIER_IMPORTS) == [("may", ("tiers",)), ("also", ("tiers",)), ("must", ("must-import",)),
                                  ("types_only", ("types-only",))]
    assert SCOPES[TIER_IMPORTS] == "tiers.<tier>.imports"
    assert [key.name for key in KEYS if key.scope == TIER] == ["proves", "litmus", "uses", "plain_tables", "folder",
                                                               "imports", "docs"]


def test_the_tier_import_keys_need_what_the_keys_they_replace_needed():
    imports = ("import", "import.relative")
    assert {address: facts for address, facts in NEEDS.items() if address.startswith("tiers.<tier>.imports")} == {
        "tiers.<tier>.imports.types_only": ("call", "use", "module_functions", "import.resolved"),
        "tiers.<tier>.imports.must": (*imports, "function.statements", "file"),
        "tiers.<tier>.imports.may": imports,
        "tiers.<tier>.imports.also": imports}
    assert not [address for address in NEEDS if address.startswith("tiers.<tier>.") and address.count(".") == 2
                and address.rsplit(".", 1)[1] in ("may_import", "may_also_import", "must_import", "types_only")]


def test_the_forms_that_declare_a_test_are_a_list_scope_of_function_call_title_and_body_and_functions_is_no_key():
    assert SCOPES[DECLARED] == "testing.declared[]"
    assert [key.name for key in KEYS if key.scope == DECLARED] == ["function", "call", "title", "body"]
    assert [key.name for key in KEYS if key.scope == TESTING] == ["preset", "beside", "files", "declared", "globals",
                                                                  "skips", "tables", "mocks"]
    assert [(key.required, key.opens) for key in KEYS if (key.scope, key.name) == (TESTING, "declared")] == [
        (True, DECLARED)]


def test_the_ways_a_mock_names_its_spec_are_a_required_list_scope_of_keyword_position_and_type_argument():
    assert SCOPES[MOCK_SPECS] == "testing.mocks.specs[]"
    assert [key.name for key in KEYS if key.scope == MOCKS] == ["calls", "autospec", "specs", "fixtures"]
    assert [key.name for key in KEYS if key.scope == MOCK_SPECS] == ["keyword", "position", "type_argument"]
    assert [(key.required, key.opens, key.rules) for key in KEYS if (key.scope, key.name) == (MOCKS, "specs")] == [
        (True, MOCK_SPECS, ("stand-ins",))]
    assert {key.name: key.rules for key in KEYS if key.scope == MOCK_SPECS} == dict.fromkeys(
        ("keyword", "position", "type_argument"), ("stand-ins",))
    assert NEEDS["testing.mocks.specs[].type_argument"] == ("call.type_arguments",)


def test_testing_names_its_preset_by_a_key_that_is_not_required_and_offers_the_presets():
    held = {key.name: key for key in KEYS if key.scope == TESTING}
    assert (held["preset"].required, held["preset"].choices, held["preset"].rules) == (
        False, CHOICE_PRESETS, ("tiers", "test-tree"))
    assert (held["files"].required, held["declared"].required) == (True, True)


def test_beside_is_a_setting_of_testing_that_is_not_required_offers_nothing_and_needs_no_fact():
    held = {key.name: key for key in KEYS if key.scope == TESTING}
    assert (held["beside"].required, held["beside"].choices, held["beside"].rules, held["beside"].needs,
            held["beside"].opens) == (False, "", ("tiers", "test-tree"), (), "")
