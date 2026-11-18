"""What the profile's rules leave of an answer: each part whose `holds` the file would break is ruled out, with the
probability the answer put on it, and what remains is made to sum to 1 again; a part the answer puts nothing on is
left as it is, the file's own part is never ruled out, and an answer that would leave nothing is read as it was
answered."""
import pytest

from xarch.modules.review.application.logic.ruling import ruled
from xarch.modules.review.domain.published import HOLDS, RuledOut
from xarch.modules.review.domain.values import Answer

ANSWER = Answer("m", (("domain", 0.2), ("values", 0.5), ("logic", 0.3), ("kernel", 0.0)), 10, 2)


@pytest.mark.parametrize("part, breaks, probabilities, out", [
    pytest.param("logic", ("values",), (("domain", 0.4), ("logic", 0.6), ("kernel", 0.0)), (RuledOut("values", HOLDS, 0.5),),
                 id="a part the file would break is dropped, and what remains sums to 1"),
    pytest.param("logic", ("domain", "values", "kernel"), (("logic", 1.0), ("kernel", 0.0)),
                 (RuledOut("domain", HOLDS, 0.2), RuledOut("values", HOLDS, 0.5)),
                 id="each part it would break is ruled out, in the order of the answer"),
    pytest.param("values", ("values", "domain"), (("values", 0.5 / 0.8), ("logic", 0.3 / 0.8), ("kernel", 0.0)),
                 (RuledOut("domain", HOLDS, 0.2),),
                 id="the file's own part is never ruled out, though it breaks its holds"),
    pytest.param("logic", (), ANSWER.probabilities, (), id="nothing broken leaves the answer as it was"),
    pytest.param("logic", ("main",), ANSWER.probabilities, (), id="a part the answer does not name rules nothing out"),
    pytest.param("logic", ("kernel",), ANSWER.probabilities, (), id="a part the answer puts nothing on rules nothing out"),
])
def test_the_parts_a_file_would_break_are_ruled_out_of_its_answer(part, breaks, probabilities, out):
    answer, found = ruled(ANSWER, part, breaks)
    assert found == out
    assert dict(answer.probabilities) == pytest.approx(dict(probabilities))
    assert [name for name, _ in answer.probabilities] == [name for name, _ in probabilities]
    assert (answer.model, answer.input_tokens, answer.output_tokens) == ("m", 10, 2)


def test_an_answer_that_would_leave_nothing_but_its_own_part_at_nothing_is_read_as_answered():
    answer = Answer("m", (("domain", 0.0), ("values", 1.0)))
    assert ruled(answer, "domain", ("values",)) == (answer, ())
