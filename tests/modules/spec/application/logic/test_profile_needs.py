"""What the keys a profile sets need of its language's reader: a key whose check reads a fact the language does not
supply is refused, naming the key, the fact and what to do; one that reads a fact supplied partly loads, and is kept
as approximate with the reader's note. A hand-made language, Toy, grades only some facts."""
from dataclasses import replace

import pytest

from tests.modules.spec.languages import PYTHON
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.application.logic.language_file import PARTIAL
from xarch.modules.spec.application.logic.profile_needs import short
from xarch.modules.spec.domain.key_table import KEYS
from xarch.profile_values.capabilities import EXACT, FACTS, Shortfall, Supply

TOY = replace(PYTHON, name="toy", checked=replace(
    PYTHON.checked, title="Toy",
    supplies=(Supply("file", EXACT), Supply("import", EXACT), Supply("import.relative", EXACT),
              Supply("import.standard", EXACT), Supply("class", PARTIAL, "a class defined in a branch is not read"))))
LANGUAGES = {"toy": TOY}


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


def test_a_key_whose_check_reads_a_fact_the_language_does_not_supply_is_refused_naming_key_fact_and_what_to_do():
    assert problems(services(no_callbacks=True), languages=LANGUAGES) == [
        "layered.yaml: parts.service.no_callbacks: its check reads callback (each call of a function's own parameter, "
        "whether it is the receiver and whether it is annotated as a callable), which the language toy does not "
        "supply: drop parts.service.no_callbacks, or check the app with a language whose reader supplies callback"]


def test_a_key_set_to_false_configures_no_check_and_needs_nothing():
    assert parsed(services(no_callbacks=False), languages=LANGUAGES).approximate == ()


def test_a_key_whose_check_reads_a_fact_supplied_partly_loads_and_is_kept_as_approximate():
    assert parsed(services(names="*Service"), languages=LANGUAGES).approximate == (
        Shortfall("parts.service.names", "class", "a class defined in a branch is not read"),)


def test_a_key_whose_facts_are_all_supplied_exactly_is_neither_refused_nor_approximate():
    assert parsed(services(libraries=["sqlmodel"]), languages=LANGUAGES).approximate == ()


def test_a_language_whose_data_file_says_nothing_of_its_reader_holds_no_key_to_it():
    silent = replace(TOY, checked=replace(TOY.checked, supplies=None))
    assert parsed(services(no_callbacks=True), languages={"toy": silent}).approximate == ()


def test_python_supplies_every_fact_a_bundled_check_reads():
    assert {supply.fact: supply.grade for supply in PYTHON.checked.supplies} == {fact: EXACT for fact in FACTS}


def test_the_keys_a_profile_sets_are_found_in_every_scope_and_through_a_testing_preset_each_once():
    document = covered(guards={"dead-code": {"untested": True, "tests_only": True, "known": ["shared/wiring.py:build"]},
                               "no-comments": {}, "no-twins": {"translated": ["api"]}},
                       reserved={"json": "only io"})
    document["parts"]["service"]["holds"] = "classes"
    document["tiers"]["unit"]["must_import"] = ["service"]
    document["parts"]["service"]["uses"] = {"never": "pure"}
    document["tiers"]["unit"]["uses"] = {"apply_never": True}
    partly = replace(PYTHON, checked=replace(PYTHON.checked, supplies=tuple(Supply(f, PARTIAL, "partly") for f in FACTS)))
    found = short(document | {"testing": "pytest"}, {"pytest": document["testing"]}, partly)
    configured = [("reserved", "reserved"), ("tiers", "tiers"), ("parts.api.may_import", "parts.<part>.may_import"),
                  ("parts.service.may_import", "parts.<part>.may_import"), ("parts.service.holds", "parts.<part>.holds"),
                  ("parts.service.uses.never", "parts.<part>.uses.never"),
                  ("parts.store.may_import", "parts.<part>.may_import"),
                  ("parts.store.libraries", "parts.<part>.libraries"), ("tiers.unit.must_import", "tiers.<tier>.must_import"),
                  ("tiers.unit.uses.apply_never", "tiers.<tier>.uses.apply_never"),
                  ("testing.skips", "testing.skips"), ("testing.table", "testing.table"), ("testing.mocks", "testing.mocks"),
                  ("guards.no-comments", "guards.no-comments"), ("guards.no-twins", "guards.no-twins"),
                  ("guards.no-twins.translated", "guards.no-twins.translated"), ("guards.dead-code", "guards.dead-code"),
                  ("guards.dead-code.untested", "guards.dead-code.untested"),
                  ("guards.dead-code.tests_only", "guards.dead-code.tests_only"),
                  ("guards.dead-code.known", "guards.dead-code.known")]
    needs = {key.address: key.needs for key in KEYS}
    assert found == [Shortfall(address, fact, "partly") for address, key in configured for fact in needs[key]]


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


def test_a_key_whose_check_reads_names_through_imports_needs_them_followed_however_written():
    """Toy is given calls, so the one fact built_by still lacks is that its imports are followed."""
    calling = replace(TOY, checked=replace(TOY.checked, supplies=(*TOY.checked.supplies, Supply("call", EXACT))))
    assert problems(services(built_by=["api"]), languages={"toy": calling}) == [
        refusal("parts.service.built_by", "import.resolved")]
