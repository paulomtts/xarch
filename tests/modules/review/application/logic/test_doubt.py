"""What a file's answer says: the probability on the part it sits in, doubtful below the line; and the readings
ranked, the most doubtful first."""
import pytest

from xarch.modules.review.application.logic.doubt import (
    asked_again,
    averaged,
    by_part,
    pieces_read,
    ranked,
    reading,
)
from xarch.modules.review.domain.published import PartRead, PieceReading, PiecesRead, Reading, Request
from xarch.modules.review.domain.values import Answer, CodeFile, PartText

REQUEST = Request("app/a.py", "domain", 1200, "text")
DOMAIN = PartText("domain", "domain/", "Is it a value?", "values", 0.3)


@pytest.mark.parametrize("probabilities, then", [
    pytest.param((("domain", 0.29), ("main", 0.71)), (0.29, True), id="below the line is doubtful"),
    pytest.param((("domain", 0.3), ("main", 0.7)), (0.3, False), id="at the line is not"),
    pytest.param((("main", 1.0),), (0.0, True), id="an answer that gives the part nothing holds 0 on it"),
])
def test_a_file_is_doubtful_where_it_sits_when_its_part_holds_less_than_the_line(probabilities, then):
    found = reading(REQUEST, Answer("m-1.0.1", probabilities), DOMAIN)
    assert (found.probability, found.doubtful) == then
    assert (found.file, found.part, found.chars, found.line, found.distribution, found.model) == (
        "app/a.py", "domain", 1200, 0.3, probabilities, "m-1.0.1")


def test_the_line_of_the_part_is_the_one_read_against_and_a_line_set_by_hand_is_said():
    found = reading(REQUEST, Answer("m", (("domain", 0.4),)), PartText("domain", "domain/", "", "values", 0.5, True))
    assert (found.line, found.doubtful, found.by_hand) == (0.5, True, True)
    assert reading(REQUEST, Answer("m", (("domain", 0.25),)), PartText("domain", "", "", "", 0.2)).doubtful is False


def test_the_readings_are_ranked_from_the_lowest_probability_by_file_on_a_tie():
    def at(file: str, probability: float) -> Reading:
        return Reading(file, "domain", 900, probability, 0.3, probability < 0.3, (), "m")
    readings = (at("app/c.py", 0.9), at("app/b.py", 0.1), at("app/a.py", 0.1), at("app/d.py", 0.5))
    assert [found.file for found in ranked(readings)] == ["app/a.py", "app/b.py", "app/d.py", "app/c.py"]


@pytest.mark.parametrize("probability, line, again", [
    pytest.param(0.15, 0.3, True, id="the low end of the band at the default line"),
    pytest.param(0.45, 0.3, True, id="the high end of the band at the default line"),
    pytest.param(0.149, 0.3, False, id="below the band"),
    pytest.param(0.451, 0.3, False, id="above the band"),
    pytest.param(0.3, 0.2, True, id="the band follows a line set by hand"),
    pytest.param(0.02, 0.1, True, id="a band reaching below 0"),
    pytest.param(0.4, 0.2, False, id="the default band, away from a line set by hand"),
])
def test_a_file_is_asked_again_when_its_first_answer_is_within_the_band_of_its_part_s_line(probability, line, again):
    answer = Answer("m", (("domain", probability), ("main", 1 - probability)))
    assert asked_again(answer, PartText("domain", "", "", "", line)) is again


def test_the_answers_in_several_orders_are_read_on_each_option_s_mean_in_the_order_of_the_first():
    found = averaged((Answer("m-1", (("domain", 0.2), ("main", 0.8)), 100, 4),
                      Answer("m-2", (("main", 0.6), ("domain", 0.4)), 110, 5),
                      Answer("m-2", (("main", 1.0),), 90, 3)))
    assert found.model == "m-1" and (found.input_tokens, found.output_tokens) == (300, 12)
    assert [(name, round(value, 9)) for name, value in found.probabilities] == [("domain", 0.2), ("main", 0.8)]


def test_a_reading_says_in_how_many_orders_it_was_asked():
    assert reading(REQUEST, Answer("m", (("domain", 0.2),)), DOMAIN, 2).orders == 2


def test_a_file_under_2000_characters_is_marked_small():
    assert reading(Request("app/a.py", "domain", 1999, "t"), Answer("m", ()), DOMAIN).small is True
    assert reading(Request("app/a.py", "domain", 2000, "t"), Answer("m", ()), DOMAIN).small is False


def _read(part: str, *doubtful: bool) -> tuple[Reading, ...]:
    return tuple(Reading(f"app/{part}{n}.py", part, 900, 0.1 if low else 0.9, 0.3, low, (), "m")
                 for n, low in enumerate(doubtful))


@pytest.mark.parametrize("doubtful, then", [
    pytest.param((True, True), (2, 2, False, False), id="fewer than 3 read: too few to say anything of the part"),
    pytest.param((False, False, False), (3, 0, True, False), id="3 read, none doubtful: summed, no note"),
    pytest.param((True, False, False), (3, 1, True, False), id="1 doubtful of 3 is no pattern"),
    pytest.param((True, True, True), (3, 3, True, True), id="3 doubtful of 3: the litmus note"),
    pytest.param((True,) * 3 + (False,) * 9, (12, 3, True, False), id="3 doubtful of 12 is a quarter, not more"),
    pytest.param((True,) * 3 + (False,) * 8, (11, 3, True, True), id="3 doubtful of 11 is more than a quarter"),
])
def test_each_part_says_how_its_files_read_and_notes_its_litmus_when_more_than_a_quarter_and_3_are_doubtful(doubtful,
                                                                                                         then):
    (part,) = by_part(_read("domain", *doubtful), (DOMAIN,))
    assert (part.read, part.doubtful, part.summed, part.noted) == then


def test_the_parts_are_said_in_the_profile_s_order_only_when_a_file_of_theirs_was_read_with_their_line():
    parts = (PartText("main", "", "", "", 0.3), DOMAIN, PartText("logic", "", "", "", 0.2, True))
    assert by_part(_read("domain", True) + _read("logic", False), parts) == (
        PartRead("domain", 1, 1, 0.3, False, False, False), PartRead("logic", 1, 0, 0.2, True, False, False))


FILE = CodeFile("app/a.py", "domain", "text")


def _piece(name: str, first: int) -> Request:
    return Request("app/a.py", "domain", 1200, f"text of {name}", piece=name, kind="function", lines=(first, first + 9))


def _on(probability: float) -> Answer:
    return Answer("m", (("domain", probability), ("main", 1 - probability)))


def test_the_pieces_of_a_file_are_ranked_from_the_lowest_and_only_the_lowest_3_are_shown():
    pieces = tuple(_piece(name, first) for name, first in (("a", 1), ("b", 11), ("c", 21), ("d", 31), ("e", 41)))
    found = pieces_read(FILE, pieces, (_on(0.6), _on(0.1), _on(0.9), _on(0.1), _on(0.4)), 2, "none")
    assert (found.file, found.part, found.judged, found.too_small, found.context, found.answered) == (
        "app/a.py", "domain", 5, 2, "none", True)
    assert [(p.rank, p.name, p.lines, p.probability) for p in found.lowest] == [
        (1, "b", (11, 20), 0.1), (2, "d", (31, 40), 0.1), (3, "e", (41, 50), 0.4)]
    assert found.lowest[0] == PieceReading(1, "function", "b", (11, 20), 1200, 0.1, _on(0.1).probabilities)


def test_fewer_than_two_pieces_judged_is_nothing_to_rank():
    assert pieces_read(FILE, (_piece("a", 1),), (), 4, "none") == PiecesRead("app/a.py", "domain", 1, 4, "none", ())


def test_pieces_with_one_unanswered_are_not_ranked():
    found = pieces_read(FILE, (_piece("a", 1), _piece("b", 11)), (_on(0.2), None), 0, "imports")
    assert (found.lowest, found.answered, found.context) == ((), False, "imports")
