"""The question placement asks, from the profile's own words, the other orders it is asked again in, and what each
request sends."""
import pytest

from tests.modules.review.builders import BODY, PARTS, found
from xarch.modules.review.application.logic.masking import MASK
from xarch.modules.review.application.logic.questions import (
    PLACEMENT,
    characters,
    placement,
    reordered,
    request,
    role_only,
    tokens,
)
from xarch.modules.review.domain.published import Choice, Option, Request


def test_each_part_is_an_option_in_the_profile_s_order_described_by_its_litmus_else_its_role():
    assert placement(PARTS) == Choice(PLACEMENT, (Option("domain", "Is it an invariant of one of this module's values?"),
                                                  Option("main", "starts the app")))


def test_the_parts_with_no_litmus_are_said():
    assert role_only(PARTS) == ("main",)


def test_a_request_sends_the_file_s_text_masked_with_its_size_before_masking():
    file = found()
    assert request(file, "app") == Request(file.file, "domain", len(file.text),
                                           f"from {MASK} import DocumentId\nfrom dataclasses import dataclass\n" + BODY)


def test_each_request_sends_the_question_with_its_text():
    question = Choice("Ask?", (Option("a", "bc"), Option("d", "")))
    sent = (Request("x", "a", 3, "abc"), Request("y", "a", 1, "d"))
    assert characters(sent, question) == (3 + 8) + (1 + 8)


def test_tokens_are_a_fourth_of_the_characters_rounded_up():
    assert (tokens(0), tokens(4), tokens(5)) == (0, 1, 2)


def _options(*names: str) -> Choice:
    return Choice("Which?", tuple(Option(name, f"is it {name}?") for name in names))


@pytest.mark.parametrize("names, orders", [
    pytest.param("abc", ["bca", "cab"], id="three options: rotated by one and by two"),
    pytest.param("abcdef", ["cdefab", "efabcd"], id="six options: rotated by a third and by two thirds"),
    pytest.param("abcdefghijklm", ["efghijklmabcd", "jklmabcdefghi"], id="thirteen options: rotated by four and nine"),
    pytest.param("ab", ["ba"], id="two options: the one other order, once"),
    pytest.param("a", [], id="one option: no other order"),
])
def test_a_question_is_asked_again_in_its_options_rotated_by_a_third_and_two_thirds_each_order_once(names, orders):
    again = reordered(_options(*names))
    assert ["".join(option.name for option in choice.options) for choice in again] == orders
    assert all(choice.ask == "Which?" for choice in again)
