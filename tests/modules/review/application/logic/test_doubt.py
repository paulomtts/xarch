"""What a file's answer says: the probability on the part it sits in, doubtful below the line; and the readings
ranked, the most doubtful first."""
import pytest

from xarch.modules.review.application.logic.doubt import asked_again, averaged, ranked, reading
from xarch.modules.review.domain.published import Reading, Request
from xarch.modules.review.domain.values import Answer, PartText

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
