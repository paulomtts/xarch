"""The question placement asks, from the profile's own words, and what each request sends."""
from tests.modules.review.builders import BODY, PARTS, found
from xarch.modules.review.application.logic.masking import MASK
from xarch.modules.review.application.logic.questions import (
    PLACEMENT,
    characters,
    placement,
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
