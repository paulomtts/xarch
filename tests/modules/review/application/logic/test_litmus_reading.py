"""What the yes-or-no answers to the entries of a part's litmus list say of a file: each entry's yes against the yes
line, and whether the litmus holds: at least one alternative (when there is any) and every condition; a file whose
litmus does not hold reads as doubtful."""
import pytest

from xarch.modules.review.application.logic.litmus_reading import holds, with_litmus
from xarch.modules.review.domain.published import LitmusRead, Reading
from xarch.modules.review.domain.values import Answer
from xarch.profile_values.litmus import ALL, Litmus

A, B = Litmus("Does it save?", "save"), Litmus("Does it load?", "load")
C, D = Litmus("Is it pure?", "pure", ALL), Litmus("Is it short?", "short", ALL)


@pytest.mark.parametrize("answers, expected", [
    pytest.param(((A, False), (B, True)), True, id="one alternative of two is enough"),
    pytest.param(((A, False), (B, False)), False, id="no alternative fails"),
    pytest.param(((C, True), (D, True)), True, id="every condition holds"),
    pytest.param(((C, True), (D, False)), False, id="one condition fails"),
    pytest.param(((A, True), (C, False)), False, id="an alternative does not excuse a condition"),
    pytest.param(((A, False), (B, True), (C, True)), True, id="an alternative and every condition"),
    pytest.param(((A, False), (C, True)), False, id="a condition does not stand for the alternatives"),
])
def test_the_alternatives_and_the_conditions_combine_with_and(answers, expected):
    assert holds(answers) is expected


def yes(probability: float) -> Answer:
    return Answer("m-1", (("yes", probability), ("no", 1 - probability)))


PLACED = Reading("app/store/a.py", "store", 900, 0.8, 0.3, False, (("store", 0.8),), "m-1")


def test_each_entry_reads_yes_at_or_above_the_yes_line_and_a_litmus_that_holds_leaves_the_reading_as_it_was():
    read = with_litmus(PLACED, (A, B, C), (yes(0.2), yes(0.5), yes(0.9)), 0.5)
    assert read.litmus == (LitmusRead("save", "any", 0.2, False), LitmusRead("load", "any", 0.5, True),
                           LitmusRead("pure", "all", 0.9, True))
    assert (read.litmus_holds, read.yes_line, read.doubtful) == (True, 0.5, False)


def test_a_litmus_that_does_not_hold_makes_the_file_doubtful_whatever_its_probability():
    read = with_litmus(PLACED, (A, C), (yes(0.9), yes(0.4)), 0.5)
    assert (read.litmus_holds, read.doubtful, read.probability) == (False, True, 0.8)


def test_a_part_with_no_entries_of_its_own_reads_as_before():
    assert with_litmus(PLACED, (), (), 0.5) == PLACED
