"""What the keys a profile sets need of its language's reader: a key whose check reads a fact the language does not
supply is refused, naming the key, the fact and what to do; one that reads a fact supplied partly loads, and is kept
as approximate with the reader's note. A hand-made language, Toy, grades only some facts."""
from dataclasses import replace

import pytest

from tests.modules.spec.languages import PYTHON
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.application.logic.language_file import PARTIAL
from xarch.modules.spec.application.logic.profile_needs import refused, short
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import PROFILE, Key
from xarch.profile_values.capabilities import EXACT, FACTS, Shortfall, Supply

TOY = replace(PYTHON, name="toy", checked=replace(
    PYTHON.checked, title="Toy",
    supplies=(Supply("file", EXACT), Supply("import", EXACT), Supply("import.relative", EXACT),
              Supply("import.standard", EXACT), Supply("class", PARTIAL, "a class defined in a branch is not read"),
              Supply("public", EXACT))))
LANGUAGES = {"toy": TOY}
FLAT = replace(PYTHON, name="flat", checked=replace(
    PYTHON.checked, title="Flat", package_files=(),
    supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "file.package")))
"""A language whose reader supplies every fact but file.package: it has no package file."""
FLATS = {"flat": FLAT}
FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}
PARTLY = replace(PYTHON, checked=replace(PYTHON.checked, supplies=tuple(Supply(f, PARTIAL, "partly") for f in FACTS)))
"""Python, its reader supplying every fact only partly: every key the walk finds gives one shortfall per fact."""
OUTER, INNER, ROWS, ITEMS, CELLS = "outer", "outer.inner", "rows[]", "items.<item>", "items.<item>.cells[]"
NESTED = (
    Key(PROFILE, "outer", opens=OUTER), Key(PROFILE, "rows", opens=ROWS), Key(PROFILE, "items", opens=ITEMS),
    Key(PROFILE, "flat", needs=("use",)),
    Key(OUTER, "inner", opens=INNER), Key(OUTER, "own", needs=("call",)),
    Key(INNER, "deep", needs=("call",)),
    Key(ROWS, "form", needs=("call",)),
    Key(ITEMS, "cells", opens=CELLS),
    Key(CELLS, "kind", needs=("use",)),
)
"""A key table of the tests' own, its scopes named by their addresses (none is in SCOPES): a mapping in a mapping, a
list, and a list in each entry of a map of names. Toy supplies neither call nor use."""
RANKED = tuple(replace(key, needs=("use",)) if key.address == "rows" else key for key in NESTED)
"""NESTED, its key rows needing use itself."""


def services(**keys) -> dict:
    document = layered(language="toy")
    document["parts"]["service"] |= keys
    return document


def tiered(**keys) -> dict:
    """layered() in toy, with one tier, unit, that tests every part, its keys the ones given."""
    document = layered(language="toy", testing={"files": ["test_*.py"], "functions": "test_*"}, tiers={"unit": keys})
    for spec in document["parts"].values():
        spec["tests"] = "unit"
    return document


def refusal(address: str, fact: str) -> str:
    return (f"layered.yaml: {address}: its check reads {fact} ({FACTS[fact]}), which the language toy does not "
            f"supply: drop {address}, or check the app with a language whose reader supplies {fact}")


def walked(document: dict, keys: tuple[Key, ...] = NESTED) -> list[str]:
    """The address of each shortfall of the document under the table in Toy, in the order found; each is refused (no
    note), as Toy supplies neither call nor use."""
    found = short(document, {}, TOY, keys=keys)
    assert all(item.note is None for item in found)
    return [item.address for item in found]


def everywhere() -> tuple[dict, dict]:
    """A profile setting keys that need facts in every scope, its testing written as the name of a preset, and the
    presets."""
    document = covered(guards={"dead-code": {"untested": True, "tests_only": True, "known": ["shared/wiring.py:build"]},
                               "no-comments": {}, "no-twins": {"translated": ["api"]}},
                       reserved={"json": "only io"})
    document["parts"]["service"]["holds"] = "classes"
    document["tiers"]["unit"]["must_import"] = ["service"]
    document["parts"]["service"]["uses"] = {"never": "pure"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    return document | {"testing": "pytest"}, {"pytest": document["testing"]}


def test_a_key_whose_check_reads_a_fact_the_language_does_not_supply_is_refused_naming_key_fact_and_what_to_do():
    assert problems(layered(language="toy", guards={"no-callbacks": {"parts": ["service"]}}), languages=LANGUAGES) == [
        "layered.yaml: guards.no-callbacks: its check reads callback (each call of a function's own parameter, "
        "whether it is the receiver and whether it is annotated as a callable), which the language toy does not "
        "supply: drop guards.no-callbacks, or check the app with a language whose reader supplies callback"]


def test_a_profile_without_the_guard_no_callbacks_needs_no_callback():
    assert parsed(layered(language="toy"), languages=LANGUAGES).approximate == ()


def test_callback_is_needed_by_the_guard_no_callbacks_alone():
    assert [key.address for key in KEYS if "callback" in key.needs] == ["guards.no-callbacks"]


def test_a_key_set_to_false_configures_no_check_and_needs_nothing():
    assert parsed(services(immutable=False), languages=LANGUAGES).approximate == ()


def test_a_key_whose_check_reads_a_fact_supplied_partly_loads_and_is_kept_as_approximate():
    assert parsed(services(names="*Service"), languages=LANGUAGES).approximate == (
        Shortfall("parts.service.names", "class", "a class defined in a branch is not read"),)


def test_a_key_whose_facts_are_all_supplied_exactly_is_neither_refused_nor_approximate():
    assert parsed(services(libraries=["sqlmodel"]), languages=LANGUAGES).approximate == ()


def test_a_language_whose_data_file_says_nothing_of_its_reader_holds_no_key_to_it():
    silent = replace(TOY, checked=replace(TOY.checked, supplies=None))
    assert parsed(layered(language="toy", guards={"no-callbacks": {"parts": ["service"]}}),
                  languages={"toy": silent}).approximate == ()


def test_python_supplies_every_fact_a_bundled_check_reads():
    assert {supply.fact: supply.grade for supply in PYTHON.checked.supplies} == {fact: EXACT for fact in FACTS}


def test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once():
    document, presets = everywhere()
    found = short(document, presets, PARTLY)
    configured = [("testing.skips", "testing.skips"), ("testing.table", "testing.table"),
                  ("testing.mocks", "testing.mocks"), ("parts.api.may_import", "parts.<part>.may_import"),
                  ("parts.service.may_import", "parts.<part>.may_import"), ("parts.service.holds", "parts.<part>.holds"),
                  ("parts.service.uses.never", "parts.<part>.uses.never"),
                  ("parts.store.may_import", "parts.<part>.may_import"),
                  ("parts.store.libraries", "parts.<part>.libraries"), ("reserved", "reserved"), ("tiers", "tiers"),
                  ("tiers.unit.uses.apply_never", "tiers.<tier>.uses.apply_never"),
                  ("tiers.unit.must_import", "tiers.<tier>.must_import"),
                  ("guards.no-comments", "guards.no-comments"), ("guards.no-twins", "guards.no-twins"),
                  ("guards.no-twins.translated", "guards.no-twins.translated"), ("guards.dead-code", "guards.dead-code"),
                  ("guards.dead-code.untested", "guards.dead-code.untested"),
                  ("guards.dead-code.tests_only", "guards.dead-code.tests_only"),
                  ("guards.dead-code.known", "guards.dead-code.known")]
    needs = {key.address: key.needs for key in KEYS}
    assert found == [Shortfall(address, fact, "partly") for address, key in configured for fact in needs[key]]


def test_the_table_walked_is_every_key_of_the_format_unless_another_is_given():
    document, presets = everywhere()
    assert short(document, presets, PARTLY) == short(document, presets, PARTLY, keys=(*KEYS, *SLOTS))


@pytest.mark.parametrize("key", [key for key in KEYS if key.needs], ids=lambda key: key.address)
def test_a_key_needs_only_facts_of_the_vocabulary_of_facts(key):
    assert set(key.needs) <= set(FACTS)


def test_a_part_s_never_list_under_uses_needs_the_facts_its_check_reads():
    document = services(uses={"never": "pure"})
    document["never"] = {"pure": ["socket"]}
    assert problems(document, languages=LANGUAGES) == [refusal("parts.service.uses.never", "use"),
                                                       refusal("parts.service.uses.never", "method_call"),
                                                       refusal("parts.service.uses.never", "import.resolved")]


def test_a_tier_that_applies_the_never_lists_needs_the_facts_their_check_reads():
    assert problems(tiered(uses={"apply_never": True}), languages=LANGUAGES) == [
        refusal("tiers.unit.uses.apply_never", "use"), refusal("tiers.unit.uses.apply_never", "method_call"),
        refusal("tiers.unit.uses.apply_never", "import.resolved")]


def test_apply_never_false_configures_nothing():
    assert parsed(tiered(uses={"apply_never": False}), languages=LANGUAGES).approximate == ()


@pytest.mark.parametrize("uses", [pytest.param("pure", id="a string"), pytest.param([{"never": "pure"}], id="a list")])
def test_a_uses_that_is_no_mapping_configures_nothing_in_any_language(uses):
    document = services(uses=uses)
    assert short(document, {}, TOY) == []


def test_a_key_three_scopes_down_is_held_to_its_facts_at_its_full_address():
    assert short({"outer": {"inner": {"deep": "x"}}}, {}, TOY, keys=NESTED) == [
        Shortfall("outer.inner.deep", "call", None)]


def test_each_entry_of_a_list_is_held_to_its_facts_addressed_by_its_index_from_0():
    assert walked({"rows": [{"form": "a"}, {"form": "b"}]}) == ["rows.0.form", "rows.1.form"]


def test_the_index_of_a_list_entry_counts_every_entry_not_only_the_mappings():
    assert walked({"rows": ["x", {"form": "a"}]}) == ["rows.1.form"]


def test_a_list_inside_an_entry_of_a_map_of_names_is_addressed_by_the_entry_s_name_and_the_index():
    assert short({"items": {"a": {"cells": [{"kind": "k"}]}}}, {}, TOY, keys=NESTED) == [
        Shortfall("items.a.cells.0.kind", "use", None)]


def test_the_walk_is_depth_first_and_takes_a_scope_s_keys_in_the_order_of_the_table():
    assert walked({"flat": 1, "outer": {"own": 1, "inner": {"deep": 1}}}) == ["outer.inner.deep", "outer.own", "flat"]


@pytest.mark.parametrize("document", [
    pytest.param({"outer": {"inner": {"deep": False}}}, id="a nested key set to false"),
    pytest.param({"outer": {"inner": {"deep": None}}}, id="a nested key set to null"),
    pytest.param({"outer": False}, id="an opening key set to false"),
    pytest.param({"outer": None}, id="an opening key set to null"),
    pytest.param({"rows": ["x"]}, id="a list entry that is no mapping"),
    pytest.param({"rows": [["x", {"form": "a"}]]}, id="a list entry that is a list"),
    pytest.param({"rows": {"form": "a"}}, id="a list scope written as a mapping"),
    pytest.param({"outer": [{"own": 1}]}, id="a mapping scope written as a list"),
    pytest.param({"items": {"a": "x"}}, id="an entry of a map of names that is no mapping"),
    pytest.param({"items": [{"cells": [{"kind": "k"}]}]}, id="a map of names written as a list"),
    pytest.param({"outer": {"stray": 1}}, id="a key the table does not list"),
])
def test_what_configures_nothing_is_held_to_no_fact(document):
    assert walked(document) == []


@pytest.mark.parametrize("value", [pytest.param(0, id="zero"), pytest.param("", id="an empty string"),
                                   pytest.param([], id="an empty list"), pytest.param({}, id="an empty mapping")])
def test_any_value_but_false_and_null_configures_a_key(value):
    assert walked({"outer": {"own": value}}) == ["outer.own"]


def test_a_key_that_needs_facts_is_held_to_them_whatever_the_shape_of_its_value():
    assert walked({"rows": "x"}, RANKED) == ["rows"]
    assert walked({"rows": [{"form": "a"}]}, RANKED) == ["rows", "rows.0.form"]


def test_an_entry_named_by_no_string_is_addressed_by_its_name_as_text():
    assert walked({"items": {7: {"cells": [{"kind": "k"}]}, False: {"cells": [{"kind": "k"}]}}}) == [
        "items.7.cells.0.kind", "items.False.cells.0.kind"]


def test_a_document_nested_deeper_than_the_table_is_walked_no_deeper_than_the_table():
    assert walked({"outer": {"inner": {"deep": {"inner": {"deep": 1}}}}}) == ["outer.inner.deep"]


def test_a_list_entry_s_refusal_reads_as_every_refusal_does():
    assert refused(short({"rows": [{"form": "a"}]}, {}, TOY, keys=NESTED), TOY) == [
        f"rows.0.form: its check reads call ({FACTS['call']}), which the language toy does not supply: drop "
        "rows.0.form, or check the app with a language whose reader supplies call"]


@pytest.mark.parametrize("value", [pytest.param(False, id="false"), pytest.param(None, id="null")])
def test_a_guard_is_configured_by_being_named_whatever_its_value(value):
    assert short(layered(language="toy", guards={"no-callbacks": value}), {}, TOY) == [
        Shortfall("guards.no-callbacks", "callback", None)]


def test_a_key_of_a_part_written_with_no_value_configures_nothing():
    assert short(services(holds=None), {}, TOY) == []


def test_a_key_of_a_guard_written_with_no_value_configures_nothing():
    found = short(layered(language="toy", guards={"no-twins": {"translated": None}}), {}, TOY)
    assert {item.address for item in found} == {"guards.no-twins"}


@pytest.mark.parametrize("testing", [pytest.param("nosuch", id="a name that is no preset"),
                                     pytest.param(3, id="a number"), pytest.param(["pytest"], id="a list")])
def test_a_testing_that_names_no_preset_and_is_no_mapping_walks_nothing(testing):
    assert short(layered(language="toy", testing=testing), {"pytest": {"skips": ["x"]}}, TOY) == []


def test_a_testing_that_names_a_preset_is_walked_as_the_preset():
    found = short(layered(language="toy", testing="pytest"), {"pytest": {"skips": ["x"]}}, TOY)
    assert [(item.address, item.fact) for item in found] == [("testing.skips", "use"),
                                                             ("testing.skips", "import.resolved")]


def test_a_key_whose_check_reads_names_through_imports_needs_them_followed_however_written():
    """Toy is given calls, so the one fact built_by still lacks is that its imports are followed."""
    calling = replace(TOY, checked=replace(TOY.checked, supplies=(*TOY.checked.supplies, Supply("call", EXACT))))
    assert problems(services(built_by=["api"]), languages={"toy": calling}) == [
        refusal("parts.service.built_by", "import.resolved")]


def test_whether_a_class_is_an_interface_is_a_fact_the_marks_of_the_data_file_say():
    assert FACTS["class.interface"] == "whether a class is an interface, by the marks of the language's data file"


@pytest.mark.parametrize("address", ["guards.stand-ins", "guards.dead-code", "fakes"])
def test_a_key_that_reads_ports_needs_the_reader_to_mark_interfaces(address):
    assert "class.interface" in {key.address: key.needs for key in KEYS}[address]


def test_fakes_are_refused_in_a_language_whose_reader_marks_no_interface():
    document = services()
    document["fakes"] = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}
    assert refusal("fakes", "class.interface") in problems(document, languages=LANGUAGES)


def flat(**keys) -> dict:
    document = layered(language="flat")
    document["parts"]["service"] |= keys
    return document


def unsupplied(address: str) -> str:
    return (f"layered.yaml: {address}: its check reads file.package (a file stands for the folder that holds it), "
            f"which the language flat does not supply: drop {address}, or check the app with a language whose reader "
            "supplies file.package")


@pytest.mark.parametrize("keys, address", [
    pytest.param({"package_only": True}, "parts.service.package_only", id="package_only"),
    pytest.param({"must_import": ["store"]}, "parts.service.must_import", id="a part's must_import"),
])
def test_a_key_that_reads_the_package_file_as_written_is_refused_under_a_language_with_none(keys, address):
    assert problems(flat(**keys), languages=FLATS) == [unsupplied(address)]


def test_dead_code_untested_is_refused_under_a_language_with_no_package_file():
    document = covered(guards={"dead-code": {"untested": True}}, fakes=FAKES, language="flat")
    assert problems(document, languages=FLATS) == [unsupplied("guards.dead-code.untested")]


def test_the_keys_that_read_the_package_file_negated_load_under_a_language_with_none():
    assert parsed(flat(holds="functions", immutable=True), languages=FLATS).approximate == ()
    assert parsed(covered(guards={"dead-code": {}}, fakes=FAKES, language="flat"), languages=FLATS).approximate == ()
    assert parsed(flat(), languages=FLATS).approximate == ()


def test_file_package_is_a_fact_after_class_interface_and_only_the_keys_that_read_it_as_written_need_it():
    facts = list(FACTS)
    assert facts[facts.index("class.interface") + 1] == "file.package"
    assert FACTS["file.package"] == "a file stands for the folder that holds it"
    needing = sorted(key.address for key in KEYS if "file.package" in key.needs)
    assert needing == ["guards.dead-code.untested", "parts.<part>.must_import", "parts.<part>.package_only"]


def test_comment_doc_is_a_fact_after_file_package_and_comment_says_the_marker_it_opens_with():
    facts = list(FACTS)
    assert facts[facts.index("file.package") + 1] == "comment.doc"
    assert FACTS["comment.doc"] == "whether a comment is a doc comment"
    assert FACTS["comment"] == ("each comment, its text, its line and where on it it starts and ends, and the marker it "
                                "opens with, which review cuts before it sends a text")


def test_no_comments_is_refused_under_a_language_that_does_not_say_which_comments_are_doc_comments():
    commenting = replace(TOY, checked=replace(TOY.checked, supplies=(*TOY.checked.supplies, Supply("comment", EXACT))))
    document = layered(language="toy", guards={"no-comments": {}})
    assert problems(document, languages={"toy": commenting}) == [refusal("guards.no-comments", "comment.doc")]
    both = replace(TOY, checked=replace(TOY.checked, supplies=(*commenting.checked.supplies,
                                                                Supply("comment.doc", EXACT))))
    assert parsed(document, languages={"toy": both}).approximate == ()
    assert sorted(key.address for key in KEYS if "comment.doc" in key.needs) == ["guards.no-comments"]


def test_public_is_a_fact_after_comment_doc():
    facts = list(FACTS)
    assert facts[facts.index("comment.doc") + 1] == "public"
    assert FACTS["public"] == ("whether a name a file defines, or takes by an import, is for other files to use, as the "
                               "language decides it")


def test_class_record_is_a_fact_after_public():
    facts = list(FACTS)
    assert facts[facts.index("public") + 1] == "class.record"
    assert FACTS["class.record"] == "whether a class is a record, as the language writes one"


def test_function_top_level_is_a_fact_after_class_record():
    facts = list(FACTS)
    assert facts[facts.index("class.record") + 1] == "function.top_level"
    assert FACTS["function.top_level"] == "whether a function is defined at the top level of its file, in no class"


def test_private_imports_is_refused_under_a_language_whose_reader_does_not_say_which_names_are_public():
    unsaid = replace(TOY, checked=replace(TOY.checked, supplies=tuple(
        supply for supply in TOY.checked.supplies if supply.fact != "public")))
    document = layered(language="toy", guards={"private-imports": {}})
    assert problems(document, languages={"toy": unsaid}) == [refusal("guards.private-imports", "public")]
    assert parsed(document, languages=LANGUAGES).approximate == ()


UNSAID = replace(PYTHON, name="unsaid", checked=replace(
    PYTHON.checked, title="Unsaid", supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "public")))
"""A language whose reader supplies every fact but public: it does not say which names are for other files to use."""


def test_a_shared_part_is_refused_under_a_language_whose_reader_does_not_say_which_names_are_public():
    document = layered(language="unsaid")
    document["parts"]["service"] |= {"shared": 2}
    assert problems(document, languages={"unsaid": UNSAID}) == [
        "layered.yaml: parts.service.shared: its check reads public (whether a name a file defines, or takes by an "
        "import, is for other files to use, as the language decides it), which the language unsaid does not supply: "
        "drop parts.service.shared, or check the app with a language whose reader supplies public"]
    said = replace(UNSAID, checked=replace(UNSAID.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"unsaid": said}).approximate == ()
    assert sorted(key.address for key in KEYS if "public" in key.needs) == [
        "guards.dead-code.known", "guards.dead-code.tests_only", "guards.no-twins", "guards.no-twins.min_renamed",
        "guards.no-twins.translated", "guards.private-imports", "parts.<part>.holds", "parts.<part>.names",
        "parts.<part>.shared"]


UNRECORDED = replace(PYTHON, name="unrecorded", checked=replace(
    PYTHON.checked, title="Unrecorded", supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "class.record")))
"""A language whose reader supplies every fact but class.record: it does not say which classes are records."""


def test_a_part_that_holds_is_refused_under_a_language_whose_reader_does_not_say_which_classes_are_records():
    document = layered(language="unrecorded")
    document["parts"]["service"] |= {"holds": "functions"}
    assert problems(document, languages={"unrecorded": UNRECORDED}) == [
        "layered.yaml: parts.service.holds: its check reads class.record (whether a class is a record, as the language "
        "writes one), which the language unrecorded does not supply: drop parts.service.holds, or check the app with a "
        "language whose reader supplies class.record"]
    said = replace(UNRECORDED, checked=replace(UNRECORDED.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"unrecorded": said}).approximate == ()
    assert sorted(key.address for key in KEYS if "class.record" in key.needs) == ["parts.<part>.holds"]


UNTOPPED = replace(PYTHON, name="untopped", checked=replace(
    PYTHON.checked, title="Untopped",
    supplies=tuple(Supply(fact, EXACT) for fact in FACTS if fact != "function.top_level")))
"""A language whose reader supplies every fact but function.top_level: it does not say which functions are defined at
the top level of their file."""


def untopped(address: str) -> str:
    return (f"layered.yaml: {address}: its check reads function.top_level (whether a function is defined at the top "
            f"level of its file, in no class), which the language untopped does not supply: drop {address}, or check "
            "the app with a language whose reader supplies function.top_level")


@pytest.mark.parametrize("holds", [
    pytest.param("functions", id="a part of functions"),
    pytest.param("classes", id="a part of classes, whose rule reads top-level"),
])
def test_a_part_that_holds_is_refused_under_a_language_whose_reader_does_not_say_which_functions_are_top_level(holds):
    document = layered(language="untopped")
    document["parts"]["service"] |= {"holds": holds}
    assert problems(document, languages={"untopped": UNTOPPED}) == [untopped("parts.service.holds")]
    said = replace(UNTOPPED, checked=replace(UNTOPPED.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"untopped": said}).approximate == ()
    assert sorted(key.address for key in KEYS if "function.top_level" in key.needs) == [
        "guards.dead-code.tests_only", "parts.<part>.holds"]


def test_dead_code_tests_only_is_refused_under_a_language_whose_reader_does_not_say_which_functions_are_top_level():
    document = covered(guards={"dead-code": {"tests_only": True}}, fakes=FAKES, language="untopped")
    assert problems(document, languages={"untopped": UNTOPPED}) == [untopped("guards.dead-code.tests_only")]
    said = replace(UNTOPPED, checked=replace(UNTOPPED.checked, supplies=PYTHON.checked.supplies))
    assert parsed(document, languages={"untopped": said}).approximate == ()
