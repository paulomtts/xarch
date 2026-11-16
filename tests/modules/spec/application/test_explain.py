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
UNTOLD = {"bundled": {"base": {}}, "keys": {"fragments": {}, "smallest": "xarch: 2\n", "symbols": []}}
SAID = (
    Symbol("<word>", "in a path: a repeating folder, one per name, as in units/<unit>/store; there may be several"),
    Symbol("store", "in may_import, a bare name: that part, in the importer's own instance of its repeating folder"),
    Symbol("store@any", "that part in any instance; the only way to name a part of another repeating folder"),
    Symbol("store/schema", "only what lies below that path of the part"),
    Symbol("store:*Id", "in may_import, after `:`: only the names that match the pattern, `*` for any text"),
    Symbol("everything", "in may_import or libraries: no limit"),
    Symbol("a path ending in .py", "a last path step with a dot: the part is one file, not a folder"),
)
"""The symbols as the format says them for the default language, its extension in place of %extension%."""
SMALLEST = "xarch: 2\nname: documents-app\nparts:\n  documents:\n    path: documents\n    role: the documents\n"
"""The smallest valid profile, as the format shows it."""


def explained(key: str):
    return spec_controller(**BUNDLED)[0].explain(Explain(key))


BASED_ON = explained("based_on")
FORMAT = spec_controller(**BUNDLED)[0].explain(Explain())
SHAPE = (
    Shown('xarch', 0, 'the format version', True, False),
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
    Shown('parts.may_import', 1, 'what the part may import besides itself', False, True),
    Shown('parts.must_import', 1, 'what each file of the part has to reach', False, True),
    Shown('parts.types_only', 1, 'the parts its files may use only as types', False, True),
    Shown('parts.holds', 1, 'what the files of the part define at the top level', False, True),
    Shown('parts.immutable', 1, 'the classes of the part are immutable records', False, True),
    Shown('parts.no_callbacks', 1, 'its code calls none of its own parameters', False, True),
    Shown('parts.names', 1, 'how the classes of the part are named', False, True),
    Shown('parts.built_by', 1, 'the only parts that may build its classes', False, True),
    Shown('parts.shared', 1, 'the part is there to be shared, by at least this many users', False, True),
    Shown('parts.libraries', 1, 'the outside packages the part may import', False, True),
    Shown('parts.forbidden', 1, 'the list of names the part may not use', False, True),
    Shown('parts.tier', 1, 'the tier whose tests cover the part', False, True),
    Shown('parts.untested', 1, 'why no tier tests the part', False, True),
    Shown('parts.package_only', 1, 'the part is imported only as a package', False, True),
    Shown('parts.folders', 1, 'the folders below the part that the layout shows', False, True),
    Shown('forbidden', 0, 'named lists of names a part may not use', False, True),
    Shown('reserved', 0, 'standard-library names only some parts may import', False, True),
    Shown('layers', 0, 'chains of parts from the inside out', False, True),
    Shown('tiers', 0, 'the kinds of test, in the order their litmus tests run', False, True),
    Shown('tiers.proves', 1, 'what its tests prove, in one line', False, False),
    Shown('tiers.litmus', 1, 'the question that tells a test belongs to the tier', False, False),
    Shown('tiers.apply_forbidden', 1, 'its tests keep to the forbidden list of the part they mirror', False, True),
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
    Shown('guards.private-imports', 1, 'no name starting with `_` is imported from another file', False, True),
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
    Shown('evals', 0, 'how `xarch review` reads what it asks: placement', False, False, 'review'),
)
"""The keys of the file, each followed by the keys it holds, as the table of keys lists them; the keys of what review
may send and of how it reads what it asks are left to the explanation of `review` and of `evals`."""


@pytest.mark.parametrize("given, when, then", [
    pytest.param(BUNDLED, Explain(), FormatExplained(2, SHAPE, SAID, SMALLEST),
                 id="with no key the whole format is explained"),
    pytest.param(BUNDLED, Explain("based_on"),
                 KeyExplained("based_on", "the file", "the bundled profile this was copied from",
                              "the name of a bundled profile: `profile check` reports how this one is looser than it",
                              False, False, (), "based_on: base", ("base", "other"), (), name="based_on"),
                 id="a key that names a bundled profile offers the ones xarch ships"),
    pytest.param(BUNDLED, Explain("parts.may_imports"),
                 UnknownKey("parts.may_imports", ("parts.may_import", "parts.must_import", "tiers.may_import")),
                 id="a key the format does not have is refused with the nearest keys"),
    pytest.param(BROKEN, Explain(), ProfileRefused("presets/language/python.yaml: must be a mapping of keys, such as title, "
                                                   "extension and package_file"),
                 id="the format is refused with why when the data file of a language does not load"),
    pytest.param(UNTOLD, Explain("based_on"), ProfileRefused("presets/format/keys.yaml: missing `keys`\n"
                                                             "presets/format/keys.yaml: symbols: must be a mapping of names "
                                                             "to text"),
                 id="a key is refused with why when the data file of the format's texts does not load"),
])
def test_explain(given, when, then):
    spec, _ = spec_controller(**given)
    assert spec.explain(when) == then


def test_the_whole_format_is_the_keys_of_the_file_their_symbols_and_the_smallest_profile():
    assert FORMAT.version == 2 and FORMAT.smallest == SMALLEST
    assert FORMAT.symbols == SAID
    assert FORMAT.shape[0] == Shown("xarch", 0, "the format version", True, False)
    assert Shown("parts.may_import", 1, "what the part may import besides itself", False, True) in FORMAT.shape


def test_a_key_says_what_it_accepts_whether_check_enforces_it_through_which_rule_and_what_it_holds():
    key = explained("parts.may_import")
    assert (key.key, key.where, key.required, key.enforced, key.rules) == (
        "parts.may_import", "parts.<part>", False, True, ("rules",))
    assert "@any" in key.accepts and "may_import: [core]" in key.example and key.keys == ()
    assert [(held_key.key, held_key.required) for held_key in explained("fakes").keys] == [
        ("fakes.folder", True), ("fakes.for", True), ("fakes.prefix", False)]


def test_the_choices_are_the_bundled_profiles_the_testing_presets_and_the_languages_the_files_hold():
    assert BASED_ON.choices == ("base", "other") and "based_on: base" in BASED_ON.example
    assert explained("language").choices == ("python",) and explained("language").example == "language: python"
    assert explained("testing").choices == ("pytest",)
    assert explained("parts").choices == ()


def test_a_key_that_configures_a_check_names_the_facts_it_reads_as_the_default_language_supplies_them():
    found = explained("parts.no_callbacks")
    assert (found.needs, found.language) == (
        (Need("callback", FACTS["callback"], Supply("callback", EXACT)),), "Python")
    assert (BASED_ON.needs, BASED_ON.language) == ((), "")


def test_a_fact_the_default_language_does_not_grade_is_said_to_be_absent():
    toy = {"title": "Toy", "extension": ".toy", "package_file": "pkg.toy", "namespace": "core",
           "standard": "interpreter", "supplies": {"class": {"partial": "nested classes are not read"}}}
    spec, _ = spec_controller(**BUNDLED, languages={"toy": toy})
    found = spec.explain(Explain("parts.names"))
    assert (found.needs, found.graded) == (
        (Need("class", FACTS["class"], Supply("class", "partial", "nested classes are not read")),), True)
    assert (found.short, found.holder, found.name) == (
        (Shortfall("parts.names", "class", "nested classes are not read"),), "part", "names")
    assert spec.explain(Explain("parts.no_callbacks")).needs == (Need("callback", FACTS["callback"]),)
