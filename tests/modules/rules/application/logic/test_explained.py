"""What `profile explain` reads of the vocabulary: a word by its address, a category alone, the nearest addresses to
one that does not exist, the kinds a word applies to, the fields of a kind, whether a rule is written with a word, and
the rules a key expands to, with any part in place of the one it names."""
import pytest

from xarch.modules.rules.application.logic.explained import (
    CATEGORIES,
    MEANINGS,
    applies,
    category_at,
    fields,
    keyed,
    nearest,
    needs,
    uses,
    word_at,
)
from xarch.modules.rules.domain.rule import EXISTING, MAY_NOT, Condition, Match, Rule, Saying, Scope
from xarch.modules.rules.domain.vocabulary import FILTERS, KINDS, QUANTIFIERS, TARGETS, VARIABLES

RULE = Rule("names", Scope(part="store"), ("class",), MAY_NOT, (Match("name", words=("*Store",)),),
            (Saying("{name} is {targets}", "f"),), keep=(Condition("public"),), key="parts.store.names")


def test_every_category_holds_its_table_of_the_vocabulary_and_says_what_it_holds():
    assert CATEGORIES == {"kinds": KINDS, "quantifiers": QUANTIFIERS, "targets": TARGETS, "filters": FILTERS,
                          "variables": VARIABLES}
    assert set(MEANINGS) == set(CATEGORIES)


@pytest.mark.parametrize("address, found", [
    pytest.param("filters.public", ("filters", "public"), id="a filter"),
    pytest.param("kinds.class", ("kinds", "class"), id="a kind"),
    pytest.param(" variables.verb. ", ("variables", "verb"), id="blanks and stray dots are left out"),
])
def test_a_word_is_found_by_its_category_and_name(address, found):
    category, word = word_at(address)
    assert (category, word.name) == found


@pytest.mark.parametrize("address", [
    pytest.param("filters.publik", id="no word by that name"),
    pytest.param("public", id="a name without its category"),
])
def test_an_address_of_no_word_finds_none(address):
    assert word_at(address) is None


def test_a_category_is_found_alone():
    assert (category_at("filters"), category_at("filters.public"), category_at("checks")) == ("filters", "", "")


@pytest.mark.parametrize("typed, near", [
    pytest.param("filters.publik", ("filters.public", "filters.below", "filters.placed"), id="a word misspelt"),
    pytest.param("publc", ("filters.public", "targets.place"), id="a name without its category"),
    pytest.param("filtrs", ("filters", "filters.test", "filters.named"), id="a category misspelt"),
    pytest.param("zzz", tuple(CATEGORIES), id="nothing alike: the categories"),
])
def test_an_address_of_no_word_has_the_nearest_ones(typed, near):
    assert nearest(typed) == near


def test_a_word_applies_to_the_kinds_that_carry_what_it_reads_and_a_kind_carries_its_fields():
    assert applies(next(t for t in TARGETS if t.name == "text")) == ("syntax-error", "comment")
    imported = next(k for k in KINDS if k.name == "imported-name")
    assert [(name, when) for name, _, when in fields(imported)] == [
        ("line", ""), ("path", ""), ("written", ""), ("relative", ""), ("standard", ""), ("name", "takes-a-name")]
    assert needs(imported) == ("import", "import.relative", "import.standard")


@pytest.mark.parametrize("category, name, used", [
    pytest.param("kinds", "class", True, id="a kind it reads"),
    pytest.param("quantifiers", "may_not", True, id="its quantifier"),
    pytest.param("targets", "name", True, id="a target"),
    pytest.param("filters", "public", True, id="a filter it keeps"),
    pytest.param("variables", "targets", True, id="a variable of its message"),
    pytest.param("filters", "test", False, id="a filter it does not name"),
    pytest.param("variables", "line", False, id="a variable it does not print"),
])
def test_whether_a_rule_is_written_with_a_word(category, name, used):
    assert uses(RULE, category, name) is used


def test_a_key_expands_to_the_rules_of_that_key_or_of_any_part_in_its_place():
    other = Rule("names", Scope(part="api"), ("class",), MAY_NOT, EXISTING, (Saying("m", "f"),), key="parts.api.names")
    both = Rule("forbidden", Scope(part="store"), ("use",), MAY_NOT, (Match("path", names=(("x",),)),),
                (Saying("m", "f"),), key="parts.store.forbidden; tiers.unit.apply_forbidden")
    rules = [RULE, other, both]
    assert keyed(rules, "parts.names") == [RULE, other]
    assert keyed(rules, "parts.store.names") == [RULE]
    assert keyed(rules, "tiers.apply_forbidden") == [both]
    assert keyed(rules, "guards.no-comments") == []
