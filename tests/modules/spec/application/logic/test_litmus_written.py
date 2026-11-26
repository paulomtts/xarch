"""A litmus as a part or a tier writes it: one text, as before, or a list of entries, each a text or a map
{ask, label, mode}, refused at the entry's address when its text is empty, its label is taken, its mode is unknown or
it holds a key that is none of these."""
import pytest

from tests.modules.spec.profiles import covered, layered, parsed, part_of, problems
from xarch.profile_values.litmus import ALL, ANY, Litmus


def with_part_litmus(value) -> dict:
    document = layered()
    part_of(document, "store")["litmus"] = value
    return document


def with_tier_litmus(value) -> dict:
    document = covered()
    document["tiers"]["unit"]["litmus"] = value
    return document


def test_a_litmus_of_one_text_reads_as_before_with_no_entries():
    part = parsed(with_part_litmus("Does it save?")).parts["store"]
    assert (part.litmus, part.litmus_list) == ("Does it save?", ())
    tier = parsed(covered()).tiers[0]
    assert (tier.litmus, tier.litmus_list) == ("Does it decide?\nIf yes, it is a unit test.", ())


def test_a_litmus_list_reads_each_entry_with_its_label_written_else_its_position_and_its_mode_else_any():
    part = parsed(with_part_litmus(["Does it save?", {"ask": "Does it load?\n", "label": "load"},
                                    {"ask": "Is it pure?", "mode": "all"}])).parts["store"]
    assert part.litmus == ""
    assert part.litmus_list == (Litmus("Does it save?", "1", ANY), Litmus("Does it load?", "load", ANY),
                                Litmus("Is it pure?", "3", ALL))


def test_a_tier_takes_a_litmus_list_too():
    tier = parsed(with_tier_litmus(["Does it decide?", {"ask": "Is it fast?", "label": "fast", "mode": "all"}])).tiers[0]
    assert (tier.litmus, tier.litmus_list) == ("", (Litmus("Does it decide?", "1"), Litmus("Is it fast?", "fast", ALL)))


@pytest.mark.parametrize("value, expected", [
    pytest.param([], ["parts.store.litmus: must hold at least one entry: a text, or {ask, label, mode}"],
                 id="an empty list"),
    pytest.param(["  "], ["parts.store.litmus[0]: must be text: a question that tells code belongs to the part"],
                 id="an entry of blanks"),
    pytest.param([{"ask": ""}], ["parts.store.litmus[0].ask: must be text: a question that tells code belongs to "
                                 "the part"], id="an ask that is empty"),
    pytest.param([{"label": "x"}], ["parts.store.litmus[0]: missing `ask`"], id="no ask"),
    pytest.param([3], ["parts.store.litmus[0]: must be a text, or a map {ask, label, mode}"], id="no text, no map"),
    pytest.param(["Does it save?", {"ask": "Does it load?", "label": "1"}],
                 ["parts.store.litmus[1].label: '1' is the label of litmus[0] too: give each entry its own"],
                 id="a label taken by a position"),
    pytest.param([{"ask": "a?", "label": "x"}, {"ask": "b?", "label": "x"}],
                 ["parts.store.litmus[1].label: 'x' is the label of litmus[0] too: give each entry its own"],
                 id="a label written twice"),
    pytest.param([{"ask": "a?", "label": "two\nlines"}],
                 ["parts.store.litmus[0].label: must be one line of text: a short name of the entry"],
                 id="a label of two lines"),
    pytest.param([{"ask": "a?", "mode": "some"}],
                 ["parts.store.litmus[0].mode: 'some' is no mode: use all, any"], id="an unknown mode"),
    pytest.param([{"ask": "a?", "why": "x"}],
                 ["parts.store.litmus[0]: unknown key 'why': use ask, label, mode"], id="an unknown key"),
    pytest.param(3, ["parts.store.litmus: must be a string, or a list of entries, each a text or {ask, label, mode}"],
                 id="no text, no list"),
])
def test_a_part_s_litmus_list_is_refused_at_the_entry_s_address(value, expected):
    assert problems(with_part_litmus(value)) == [f"layered.yaml: {problem}" for problem in expected]


def test_a_tier_s_litmus_list_is_refused_at_its_address_in_the_tier_s_words():
    assert problems(with_tier_litmus(["", {"ask": "b?", "mode": "none"}])) == [
        "layered.yaml: tiers.unit.litmus[0]: must be text: a question that tells a test belongs to the tier",
        "layered.yaml: tiers.unit.litmus[1].mode: 'none' is no mode: use all, any"]
