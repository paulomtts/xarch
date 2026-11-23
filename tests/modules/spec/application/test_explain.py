"""Use case: explain the format of a profile, the whole of it or one key, with the names xarch ships as choices."""
import pytest

from tests.modules.spec.application.builders import spec_controller
from xarch.modules.spec.contract import (
    Explain,
    FormatExplained,
    KeyExplained,
    Need,
    ProfileRefused,
    Shown,
    Symbol,
    UnknownKey,
)
from xarch.profile_values.capabilities import EXACT, FACTS, Shortfall, Supply

BUNDLED = {"bundled": {"base": {}, "other": {}}}
BROKEN = {"bundled": {"base": {}}, "languages": {"python": "not a mapping"}}
UNTOLD = {"bundled": {"base": {}}, "keys": {"fragments": {}, "smallest": "name: n\n", "symbols": []}}
SAID = (
    Symbol("<word>", "in a path: a repeating folder, one per name, as in units/<unit>/store; there may be several"),
    Symbol("store", "in imports.may, a bare name: that part, in the importer's own instance of its repeating folder"),
    Symbol("store@any", "that part in any instance; the only way to name a part of another repeating folder"),
    Symbol("store/schema", "only what lies below that path of the part"),
    Symbol("store:*Id", "in imports.may, after `:`: only the names that match the pattern, `*` for any text"),
    Symbol("everything", "in imports.may or imports.libraries: no limit"),
    Symbol("a path ending in .py", "a last path step with a dot: the part is one file, not a folder"),
)
"""The symbols as the format says them for the default language, its extension in place of %extension%."""
SMALLEST = "name: documents-app\nparts:\n  documents:\n    path: documents\n    role: the documents\n"
"""The smallest valid profile, as the format shows it."""


def explained(key: str):
    return spec_controller(**BUNDLED)[0].explain(Explain(key))


BASED_ON = explained("based_on")
FORMAT = spec_controller(**BUNDLED)[0].explain(Explain())
SHAPE = (
    Shown('name', 0, 'what the profile is called', True, False),
    Shown('based_on', 0, 'the bundled profile this was copied from', False, False),
    Shown('language', 0, 'the language of the app', False, True),
    Shown('testing', 0, 'how the test framework names things', False, True),
    Shown('testing.files', 1, "patterns of a test file's name", True, True),
    Shown('testing.functions', 1, "the pattern of a test function's name", True, True),
    Shown('testing.skips', 1, 'what skips a test or expects it to fail', False, True),
    Shown('testing.table', 1, 'how a test function holds a table of cases', False, True),
    Shown('testing.mocks', 1, 'how a mock is built', False, True),
    Shown('parts', 0, 'where code sits, in the order their litmus tests run', True, True),
    Shown('parts.path', 1, 'where the part lives below the app', True, True),
    Shown('parts.role', 1, 'what the part is for, in one line', True, False),
    Shown('parts.litmus', 1, 'the question that tells code belongs here', False, False),
    Shown('parts.imports', 1, 'what the part may and must import, and its outside packages', False, True),
    Shown('parts.holds', 1, 'what the files of the part define at the top level', False, True),
    Shown('parts.shared', 1, 'the part is there to be shared, by at least this many users', False, True),
    Shown('parts.uses', 1, "what the part's code uses", False, True),
    Shown('parts.tests', 1, 'the tier whose tests cover the part', False, True),
    Shown('parts.untested', 1, 'why no tier tests the part', False, True),
    Shown('parts.package_only', 1, 'the part is imported only as a package', False, True),
    Shown('parts.folders', 1, 'the folders below the part that the layout shows', False, True),
    Shown('never', 0, 'named lists of names a part never uses', False, True),
    Shown('reserved', 0, 'standard-library names only some parts may import', False, True),
    Shown('layers', 0, 'chains of parts from the inside out', False, True),
    Shown('tiers', 0, 'the kinds of test, in the order their litmus tests run', False, True),
    Shown('tiers.proves', 1, 'what its tests prove, in one line', False, False),
    Shown('tiers.litmus', 1, 'the question that tells a test belongs to the tier', False, False),
    Shown('tiers.uses', 1, 'what its tests keep to of the part they mirror', False, True),
    Shown('tiers.plain_tables', 1, 'its table tests hold no branch', False, True),
    Shown('tiers.types_only', 1, 'the parts its tests may import only as types', False, True),
    Shown('tiers.must_import', 1, 'what each of its test files has to reach', False, True),
    Shown('tiers.folder', 1, 'a folder of tests that mirror no part', False, True),
    Shown('tiers.may_import', 1, 'what the tests in its folder may import of the app', False, True),
    Shown('tiers.may_also_import', 1, 'what its tests may also import of the app', False, True),
    Shown('tiers.docs', 1, 'what only fills the generated docs', False, False),
    Shown('fakes', 0, 'the folder of the test fakes, and what they stand in for', False, True),
    Shown('fakes.folder', 1, 'the folder of the fakes', True, True),
    Shown('fakes.for', 1, 'the parts whose Protocols the fakes stand in for', True, True),
    Shown('fakes.prefix', 1, "how a fake's name starts", False, True),
    Shown('guards', 0, 'the pre-built checks in use', False, True),
    Shown('guards.scenario-coverage', 1, 'every result of a use case has a row', False, True),
    Shown('guards.no-comments', 1, 'no `#` comments in the app or its tests', False, True),
    Shown('guards.stand-ins', 1, 'a Protocol is faked, or mocked with a spec', False, True),
    Shown('guards.closed-tree', 1, 'every file lies in a part', False, True),
    Shown('guards.no-duplicates', 1, 'no two functions with the same code', False, True),
    Shown('guards.no-twins', 1, 'no two classes in different parts with the same fields', False, True),
    Shown('guards.dead-code', 1, 'no Protocol nothing names, no fake no test uses', False, True),
    Shown('guards.pass-through', 1, 'a method that only forwards is listed', False, True),
    Shown('guards.no-callbacks', 1, 'no function of the parts calls a parameter annotated as a callable', False, True),
    Shown('guards.private-imports', 1, 'no name another file keeps private is imported from it', False, True),
    Shown('excluded', 0, 'folders below the app that are not its source', False, True),
    Shown('hints', 0, 'your own advice for a rule', False, False),
    Shown('checks', 0, 'checks of your own, beside the keys', False, True),
    Shown('files', 0, 'the files `init` writes besides the docs', False, True),
    Shown('files.from', 1, 'the template file, or the folder of a path ending in /', True, True),
    Shown('files.pinned', 1, '`check` reports the file when it differs', False, True),
    Shown('files.fill', 1, 'whether {{app}} is filled in', False, True),
    Shown('docs', 0, 'everything that only fills the generated docs', False, False),
    Shown('docs.entry', 1, 'the part that is the entry point', False, False),
    Shown('docs.pages', 1, 'the project docs `init` writes below docs/project/', False, False),
    Shown('docs.naming', 1, 'the naming table of the docs', False, False),
    Shown('docs.examples', 1, 'folders next to the profile, each an example project', False, False),
    Shown('docs.example_notes', 1, 'a note for an example', False, False),
    Shown('review', 0, 'what `xarch review` may send: never, mask', False, False, 'review'),
    Shown('evals', 0, 'what `xarch review` asks: placement, and evals of your own', False, False, 'review'),
)
"""The keys of the file, each followed by the keys it holds, as the table of keys lists them; the keys of what review
may send and of how it reads what it asks are left to the explanation of `review` and of `evals`."""


@pytest.mark.parametrize("given, when, then", [
    pytest.param(BUNDLED, Explain(), FormatExplained(SHAPE, SAID, SMALLEST),
                 id="with no key the whole format is explained"),
    pytest.param(BUNDLED, Explain("based_on"),
                 KeyExplained("based_on", "the file", "the bundled profile this was copied from",
                              "the name of a bundled profile: `profile check` reports how this one is looser than it",
                              False, False, (), "based_on: base", ("base", "other"), (), name="based_on"),
                 id="a key that names a bundled profile offers the ones xarch ships"),
    pytest.param(BUNDLED, Explain("parts.may_imports"),
                 UnknownKey("parts.may_imports", ("parts.imports", "tiers.may_import", "parts.imports.may")),
                 id="a key the format does not have is refused with the nearest keys"),
    pytest.param(BROKEN, Explain(), ProfileRefused("presets/language/python.yaml: must be a mapping of keys, such as title, "
                                                   "extensions and package_files"),
                 id="the format is refused with why when the data file of a language does not load"),
    pytest.param(UNTOLD, Explain("based_on"), ProfileRefused("presets/format/keys.yaml: missing `keys`\n"
                                                             "presets/format/keys.yaml: missing `slots`\n"
                                                             "presets/format/keys.yaml: symbols: must be a mapping of names "
                                                             "to text"),
                 id="a key is refused with why when the data file of the format's texts does not load"),
])
def test_explain(given, when, then):
    spec, _ = spec_controller(**given)
    assert spec.explain(when) == then


def test_the_whole_format_is_the_keys_of_the_file_their_symbols_and_the_smallest_profile():
    assert FORMAT.smallest == SMALLEST
    assert FORMAT.symbols == SAID
    assert FORMAT.shape[0] == Shown("name", 0, "what the profile is called", True, False)
    assert Shown("parts.imports", 1, "what the part may and must import, and its outside packages", False, True) in FORMAT.shape


def test_a_key_says_what_it_accepts_whether_check_enforces_it_through_which_rule_and_what_it_holds():
    key = explained("parts.imports.may")
    assert (key.key, key.where, key.required, key.enforced, key.rules) == (
        "parts.imports.may", "parts.<part>.imports", False, True, ("may-import",))
    assert "@any" in key.accepts and "may: [core]" in key.example
    assert [held_key.key for held_key in key.keys] == ["parts.imports.may.types_only"]
    assert [(held_key.key, held_key.required) for held_key in explained("fakes").keys] == [
        ("fakes.folder", True), ("fakes.for", True), ("fakes.prefix", False)]


def test_the_choices_are_the_bundled_profiles_the_testing_presets_and_the_languages_the_files_hold():
    assert BASED_ON.choices == ("base", "other") and "based_on: base" in BASED_ON.example
    assert explained("language").choices == ("python",) and explained("language").example == "language: python"
    assert explained("testing").choices == ("pytest",)
    assert explained("parts").choices == ()


def test_a_key_that_configures_a_check_names_the_facts_it_reads_as_the_default_language_supplies_them():
    found = explained("guards.no-callbacks")
    assert (found.needs, found.language) == (
        (Need("callback", FACTS["callback"], Supply("callback", EXACT)),), "Python")
    assert (BASED_ON.needs, BASED_ON.language) == ((), "")


def test_a_fact_the_default_language_does_not_grade_is_said_to_be_absent():
    toy = {"title": "Toy", "extensions": [".toy"], "package_files": ["pkg.toy"], "namespace": "core",
           "standard": "interpreter", "supplies": {"class": {"partial": "nested classes are not read"}}}
    spec, _ = spec_controller(**BUNDLED, languages={"toy": toy})
    found = spec.explain(Explain("parts.holds.classes.names"))
    assert (found.needs, found.graded) == (
        (Need("class", FACTS["class"], Supply("class", "partial", "nested classes are not read")),
         Need("public", FACTS["public"])), True)
    assert (found.short, found.holder, found.name) == (
        (Shortfall("parts.holds.classes.names", "class", "nested classes are not read"),
         Shortfall("parts.holds.classes.names", "public", None)), "", "names")
    assert spec.explain(Explain("guards.no-callbacks")).needs == (Need("callback", FACTS["callback"]),)


def test_the_part_key_of_the_tier_that_covers_it_is_tests_and_its_example_writes_it():
    spec, _ = spec_controller(**BUNDLED)
    found = spec.explain(Explain("parts.<part>.tests"))
    assert isinstance(found, KeyExplained)
    assert (found.key, found.name, found.meaning, found.rules) == (
        "parts.tests", "tests", "the tier whose tests cover the part", ("tiers",))
    assert "`tests`" in found.accepts and "`tier`" not in found.accepts
    assert found.example.endswith("    role: the documents\n    tests: unit\n") and "tier:" not in found.example


def test_the_part_key_xarch_renamed_is_refused_with_the_fixed_text_however_it_is_typed():
    spec, _ = spec_controller(**BUNDLED)
    for address in ("parts.tier", "parts.<part>.tier"):
        found = spec.explain(Explain(address))
        assert isinstance(found, UnknownKey)
        assert (found.key, found.retired) == ("parts.tier", "renamed in 0.3.0: write tests")


def test_the_guard_no_callbacks_and_its_parts_are_keys_of_the_format_and_the_guard_needs_callback():
    guard, listed = explained("guards.no-callbacks"), explained("guards.no-callbacks.parts")
    assert (guard.key, guard.where, guard.meaning, guard.required, guard.rules) == (
        "guards.no-callbacks", "guards", "no function of the parts calls a parameter annotated as a callable", False,
        ("no-callbacks",))
    assert guard.needs == (Need("callback", FACTS["callback"], Supply("callback", EXACT)),)
    assert [shown.key for shown in guard.keys] == ["guards.no-callbacks.parts"]
    assert "parts: [documents]" in guard.example
    assert (listed.key, listed.where, listed.required, listed.rules, listed.needs) == (
        "guards.no-callbacks.parts", "guards.no-callbacks", True, ("no-callbacks",), ())


def test_the_part_key_no_callbacks_is_refused_with_the_fixed_text_and_points_to_the_guard():
    for address in ("parts.no_callbacks", "parts.<part>.no_callbacks"):
        found = explained(address)
        assert isinstance(found, UnknownKey)
        assert (found.key, found.retired) == (
            "parts.no_callbacks", "moved in 0.3.0: write guards: {no-callbacks: {parts: [<part>, ...]}}")
        assert "guards.no-callbacks" in found.nearest
    bare = explained("no_callbacks")
    assert isinstance(bare, UnknownKey) and "guards.no-callbacks" in bare.nearest


def test_the_tier_of_scenario_coverage_is_still_a_key_of_the_format():
    spec, _ = spec_controller(**BUNDLED)
    found = spec.explain(Explain("guards.scenario-coverage.tier"))
    assert isinstance(found, KeyExplained) and found.key == "guards.scenario-coverage.tier"


def test_the_lists_a_part_never_uses_are_the_top_level_never_and_the_key_never_of_its_uses():
    block, group, held = (explained(address) for address in ("never", "parts.uses", "parts.<part>.uses.never"))
    assert (block.key, block.meaning) == ("never", "named lists of names a part never uses")
    assert "`uses: {never: <list>}`" in block.accepts and block.example.endswith("    uses: {never: published}\n")
    assert (group.key, group.where, [shown.key for shown in group.keys]) == (
        "parts.uses", "parts.<part>", ["parts.uses.never"])
    assert (held.key, held.where, held.meaning) == (
        "parts.uses.never", "parts.<part>.uses", "the list of names the part never uses")
    assert "the built-in form of a check `may_not` over names used" in held.accepts


def test_a_tier_s_uses_holds_the_switch_that_applies_the_part_s_never_list_to_its_tests():
    group, switch = (explained(address) for address in ("tiers.uses", "tiers.<tier>.uses.apply_never"))
    assert (group.key, [shown.key for shown in group.keys]) == ("tiers.uses", ["tiers.uses.apply_never"])
    assert (switch.key, switch.where, switch.meaning) == (
        "tiers.uses.apply_never", "tiers.<tier>.uses", "its tests keep to the never list of the part they mirror")
    assert switch.accepts.startswith("true or false, a switch and not a list") and '"never apply"' in switch.accepts
    assert "uses: {apply_never: true}" in switch.example


def test_review_never_and_the_top_level_never_each_name_the_other_as_another_list():
    assert "`review.never`" in explained("never").accepts
    assert "the top-level `never`" in explained("review.never").accepts


def test_the_keys_of_never_feed_the_rule_never_use():
    assert [explained(address).rules for address in ("never", "parts.uses.never", "tiers.uses.apply_never")] == [
        ("never-use",)] * 3


@pytest.mark.parametrize("address, key, text", [
    pytest.param("forbidden", "forbidden", "renamed in 0.3.0: write never", id="the old block"),
    pytest.param("parts.forbidden", "parts.forbidden", "moved in 0.3.0: write uses: {never: <list>}",
                 id="the old part key"),
    pytest.param("parts.<part>.forbidden", "parts.forbidden", "moved in 0.3.0: write uses: {never: <list>}",
                 id="the old part key with its placeholder"),
    pytest.param("tiers.apply_forbidden", "tiers.apply_forbidden", "moved in 0.3.0: write uses: {apply_never: true}",
                 id="the old tier key"),
    pytest.param("tiers.<tier>.apply_forbidden", "tiers.apply_forbidden",
                 "moved in 0.3.0: write uses: {apply_never: true}", id="the old tier key with its placeholder"),
    pytest.param("parts.never", "parts.never", "a key of uses: write uses: {never: <list>}", id="never on a part"),
    pytest.param("tiers.apply_never", "tiers.apply_never", "a key of uses: write uses: {apply_never: true}",
                 id="apply_never on a tier"),
])
def test_an_old_or_misplaced_name_of_never_is_refused_with_its_fixed_text(address, key, text):
    found = explained(address)
    assert (type(found), found.key, found.retired) == (UnknownKey, key, text)


TOY = {"title": "Toy", "extensions": [".toy"], "package_files": ["pkg.toy"], "namespace": "core",
       "standard": "interpreter", "supplies": {"class": {"partial": "nested classes are not read"}}}
"""A language whose reader supplies no top-level function, nor much else."""


def test_holds_holds_the_kinds_each_holding_the_settings_it_takes():
    holds = explained("parts.holds")
    assert (holds.key, holds.where, holds.rules) == ("parts.holds", "parts.<part>", ("holds",))
    assert [shown.key for shown in holds.keys] == [
        "parts.holds.classes", "parts.holds.functions", "parts.holds.records", "parts.holds.exceptions"]
    assert [shown.key for shown in explained("parts.holds.classes").keys] == [
        "parts.holds.classes.names", "parts.holds.classes.immutable", "parts.holds.classes.built_by"]
    assert [shown.key for shown in explained("parts.holds.functions").keys] == ["parts.holds.functions.names"]
    assert [shown.key for shown in explained("parts.holds.records").keys] == [
        "parts.holds.records.names", "parts.holds.records.immutable"]
    assert [shown.key for shown in explained("parts.<part>.holds.exceptions").keys] == ["parts.holds.exceptions.names"]


@pytest.mark.parametrize("address, where, rules", [
    pytest.param("parts.holds.functions", "parts.<part>.holds", ("holds",), id="a kind"),
    pytest.param("parts.holds.classes.names", "parts.<part>.holds.classes", ("names",), id="names of classes"),
    pytest.param("parts.holds.classes.immutable", "parts.<part>.holds.classes", ("immutable",), id="immutable of classes"),
    pytest.param("parts.holds.classes.built_by", "parts.<part>.holds.classes", ("built-by",), id="built_by of classes"),
    pytest.param("parts.holds.functions.names", "parts.<part>.holds.functions", ("names",), id="names of functions"),
    pytest.param("parts.holds.records.names", "parts.<part>.holds.records", ("names",), id="names of records"),
    pytest.param("parts.holds.records.immutable", "parts.<part>.holds.records", ("immutable",), id="immutable of records"),
    pytest.param("parts.holds.exceptions.names", "parts.<part>.holds.exceptions", ("names",), id="names of exceptions"),
])
def test_each_kind_and_setting_answers_from_the_catalogue(address, where, rules):
    found = explained(address)
    assert isinstance(found, KeyExplained)
    assert (found.key, found.where, found.rules) == (address, where, rules)
    assert found.meaning and found.accepts and "holds:" in found.example


@pytest.mark.parametrize("address, text", [
    pytest.param("parts.immutable", "moved in 0.3.0: write it under the kind it applies to, such as holds: {records: "
                                    "{immutable: true}}", id="parts.immutable"),
    pytest.param("parts.<part>.names", 'moved in 0.3.0: write it under the kind it names, such as holds: {classes: '
                                       '{names: "*Service"}}', id="parts.<part>.names"),
    pytest.param("parts.built_by", "moved in 0.3.0: write holds: {classes: {built_by: [<part>, ...]}}",
                 id="parts.built_by"),
    pytest.param("parts.holds.functions.immutable", "a setting of classes and records",
                 id="parts.holds.functions.immutable"),
])
def test_a_setting_of_holds_written_where_it_no_longer_sits_is_answered_from_the_table_of_retired_names(address, text):
    found = explained(address)
    assert isinstance(found, UnknownKey) and found.retired == text


def test_holds_says_it_reads_no_top_level_functions_in_a_language_that_does_not_supply_them():
    spec, _ = spec_controller(**BUNDLED, languages={"toy": TOY})
    found = spec.explain(Explain("parts.holds"))
    assert Shortfall("parts.holds", "function.top_level",
                     "holds reads no top-level functions: the language Toy does not supply function.top_level",
                     True) in found.short
    assert [item for item in explained("parts.holds").short if item.unread] == []
    assert [item for item in spec.explain(Explain("parts.holds.functions")).short if item.unread] == []


@pytest.mark.parametrize("address, key", [
    pytest.param("parts.adapters.imports.may", "parts.imports.may", id="may on a part"),
    pytest.param("parts.adapters.imports", "parts.imports", id="the group on a part"),
    pytest.param("parts.services.imports.may.types_only", "parts.imports.may.types_only", id="the mark on a part"),
    pytest.param("parts.imports.must", "parts.imports.must", id="must, plain"),
    pytest.param("parts.uses.never", "parts.uses.never", id="a key whose second step is a key of the part"),
])
def test_a_key_is_explained_typed_plain_or_with_the_part_it_sits_on(address, key):
    assert explained(address).key == key
