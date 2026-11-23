"""The vocabulary holds together: every name once, every field a word reads one some kind carries and the table of
fields says, every fact a kind needs one the language's data file can supply, every filter that guards a field one
that exists, and every word applies to some kind of fact. That a slot means something for each slot the format has, in
its order, is proved through the app in tests/bootstrap/test_checks_of_its_own.py."""
import pytest

from xarch.modules.rules.domain.vocabulary import FIELDS, FILTERS, KINDS, QUANTIFIERS, TARGETS, VARIABLES
from xarch.profile_values.capabilities import FACTS

WORDS = {"kind": KINDS, "filter": FILTERS, "target": TARGETS, "variable": VARIABLES, "quantifier": QUANTIFIERS}


@pytest.mark.parametrize("table", WORDS.values(), ids=WORDS.keys())
def test_every_name_is_in_its_table_once(table):
    names = [word.name for word in table]
    assert len(names) == len(set(names))


def test_every_field_a_kind_carries_or_a_word_reads_is_one_the_table_of_fields_says():
    carried = {name for kind in KINDS for name in (*kind.fields, *kind.sometimes)}
    read = {name for table in (FILTERS, TARGETS, VARIABLES) for word in table for name in word.reads}
    assert carried | read <= set(FIELDS)
    assert read <= carried


def test_every_fact_a_kind_needs_is_one_a_language_can_supply():
    assert {need for kind in KINDS for need in (*kind.needs, *(n for ns in kind.field_needs.values() for n in ns))} <= set(
        FACTS)
    assert all(set(kind.field_needs) <= {*kind.fields, *kind.sometimes} for kind in KINDS)


def test_a_field_carried_only_sometimes_is_guarded_by_a_filter_that_exists():
    assert {guard for kind in KINDS for guard in kind.sometimes.values()} <= {word.name for word in FILTERS}


@pytest.mark.parametrize("word", [*FILTERS, *TARGETS, *VARIABLES], ids=lambda word: word.name)
def test_every_word_applies_to_some_kind_of_fact(word):
    assert any(word.applies_to(kind) for kind in KINDS)


def test_the_variable_key_is_shown_with_a_key_of_the_profile_as_a_profile_writes_it_now():
    key = next(variable for variable in VARIABLES if variable.name == "key")
    assert key.meaning == "the key of the profile the check comes from: parts.store.uses.never, checks.<id>"


def test_the_interface_of_a_class_needs_the_reader_to_mark_interfaces_and_says_no_word_of_bases():
    kind = next(kind for kind in KINDS if kind.name == "class")
    interface = next(word for word in FILTERS if word.name == "interface")
    assert (kind.field_needs["interface"], interface.meaning) == (
        ("class.interface",), "the class is an interface: the language marks it as one")


def test_whether_a_name_is_public_is_a_field_of_the_kinds_whose_names_the_language_decides_and_needs_the_fact():
    public = next(word for word in FILTERS if word.name == "public")
    carrying = [kind for kind in KINDS if kind.carries("public")]
    assert [kind.name for kind in carrying] == ["imported-name", "class", "function"]
    assert [kind.field_needs["public"] for kind in carrying] == [("public",), ("public",), ("public",)]
    assert [kind.name for kind in KINDS if public.applies_to(kind)] == ["imported-name", "class", "function"]
    assert (public.reads, public.meaning, FIELDS["public"]) == (
        ("public",), "the name the fact carries is public: the language's reader says it is for other files to use",
        "whether the name is for other files to use, as the language decides it")
