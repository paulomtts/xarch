"""The question placement asks, from the profile's own words, the other orders it is asked again in, and what each
request sends."""
from dataclasses import replace

import pytest

from tests.modules.review.builders import BODY, PARTS, found
from xarch.modules.review.application.logic.masking import MASK
from xarch.modules.review.application.logic.questions import (
    OF_A_PIECE,
    PLACEMENT,
    characters,
    entry_questions,
    of_piece,
    piece_requests,
    placement,
    reordered,
    request,
    role_only,
    tokens,
)
from xarch.modules.review.domain.published import YES_NO, Choice, Option, Request
from xarch.modules.review.domain.values import CodeFile, PartText, Span
from xarch.profile_values.litmus import ALL, Litmus


def test_each_part_is_an_option_in_the_profile_s_order_described_by_its_litmus_else_its_role():
    assert placement(PARTS) == Choice(PLACEMENT, (Option("domain", "Is it an invariant of one of this module's values?"),
                                                  Option("main", "starts the app")))


def test_the_parts_with_no_litmus_are_said():
    assert role_only(PARTS) == ("main",)


def test_a_request_sends_the_file_s_text_masked_with_the_size_of_what_it_sends():
    file = found()
    sent = f"from {MASK} import DocumentId\nfrom dataclasses import dataclass\n" + BODY
    assert request(file, "app") == Request(file.file, "domain", len(sent), sent)
    assert len(sent) != len(file.text)


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


def test_the_question_of_a_piece_is_placement_s_saying_the_text_is_one_piece_of_a_larger_file():
    asked = of_piece(placement(PARTS))
    assert asked.ask == f"{PLACEMENT} {OF_A_PIECE}" and asked.options == placement(PARTS).options
    assert OF_A_PIECE == "This text is one piece of a larger file."


HEAD_LINES = "from app.kernel.ids import DocumentId\nfrom dataclasses import dataclass\n\n"
FIRST = "def first():\n" + "    a = 1\n" * 120
SECOND = "def second():\n" + "    b = 2\n" * 120
TINY = "def tiny():\n" + "    c = 3\n" * 5
PIECED = CodeFile("app/modules/documents/domain/document.py", "domain", HEAD_LINES + FIRST + SECOND + TINY + FIRST, (
    found().imports), spans=(Span("function", "first", "", (4, 124)), Span("function", "second", "", (125, 245)),
                             Span("function", "tiny", "", (246, 251)), Span("function", "first", "", (252, 372))))


def test_each_piece_judged_sends_its_masked_text_with_its_name_kind_and_lines_and_the_small_ones_are_counted():
    requests, too_small = piece_requests(PIECED, "app", (), "none")
    assert [(r.piece, r.kind, r.lines, r.text) for r in requests] == [
        ("first", "function", (4, 124), FIRST), ("second", "function", (125, 245), SECOND),
        ("tiny, first", "function", (246, 372), TINY + FIRST)]
    assert too_small == 0 and all(r.chars == len(r.text) and r.file == PIECED.file for r in requests)


def test_with_context_each_piece_sends_the_file_s_opening_lines_masked_before_it():
    requests, _ = piece_requests(PIECED, "app", (), "imports")
    assert requests[0].text == f"from {MASK} import DocumentId\nfrom dataclasses import dataclass\n\n" + FIRST
    assert requests[0].chars == len(requests[0].text)


def test_a_piece_under_1000_characters_is_not_judged_but_counted():
    small = CodeFile("app/a.py", "domain", "def a():\n    x = 1\n" * 30 + "def b():\n" + "    y = 2\n" * 120,
                     spans=(Span("function", "a", "", (1, 60)), Span("function", "b", "", (61, 181))))
    requests, too_small = piece_requests(small, "app", (), "none")
    assert ([r.piece for r in requests], too_small) == (["b"], 1)


SAVE, LOAD = Litmus("Does it save?", "save"), Litmus("Does it load?", "load")
PURE = Litmus("Is it pure?", "pure", ALL)
LISTED = PartText("store", "store/", "", "keeps records", 0.3, entries=(SAVE, LOAD, PURE))


def test_a_part_whose_litmus_is_a_list_of_one_entry_reads_as_one_text_and_asks_nothing_of_its_own():
    single = replace(LISTED, entries=(PURE,))
    assert placement((single,)).options == (Option("store", "Is it pure?"),)
    assert entry_questions(single) == () and role_only((single,)) == ()


def test_a_part_whose_litmus_is_a_list_is_described_by_its_alternatives_then_its_conditions():
    assert placement((LISTED,)).options == (
        Option("store", "Does it save? Or: Does it load? And in every case: Is it pure?"),)
    assert role_only((LISTED,)) == ()


def test_each_entry_of_a_list_is_a_yes_or_no_question_of_its_own_named_after_its_part_and_its_label():
    assert entry_questions(LISTED) == tuple(
        (f"litmus.store.{entry.label}", Choice(entry.ask, (Option("yes", ""), Option("no", "")), YES_NO))
        for entry in (SAVE, LOAD, PURE))
