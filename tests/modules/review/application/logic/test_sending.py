"""Whether a question is sent, and whether a run is refused for want of a key before anything is sent."""
import pytest

from xarch.modules.review.application.logic.sending import asks, needs_key, why_unasked
from xarch.modules.review.domain.published import FAILED, NOT_CACHED, REFUSED
from xarch.modules.review.domain.values import Answer

KEPT = Answer("m", (("domain", 1.0),))


@pytest.mark.parametrize("kept, offline, failed, then", [
    pytest.param(None, False, False, True, id="an answer not kept is asked"),
    pytest.param(KEPT, False, False, False, id="an answer kept is not asked again"),
    pytest.param(None, True, False, False, id="offline nothing is asked"),
    pytest.param(None, False, True, False, id="after a failure nothing more is asked"),
])
def test_whether_a_question_is_sent(kept, offline, failed, then):
    assert asks(kept, offline, failed) is then


@pytest.mark.parametrize("failed, then", [
    pytest.param(True, FAILED, id="after a failure it is the failure"),
    pytest.param(False, NOT_CACHED, id="else it was not kept, and offline sends nothing"),
])
def test_why_a_question_has_no_answer(failed, then):
    assert why_unasked(failed) == then


@pytest.mark.parametrize("failed", [False, True])
def test_a_question_the_decision_model_refused_alone_is_refused_whatever_failed_after_it(failed):
    assert why_unasked(failed, "TypeSafe answered 413: too large") == REFUSED


@pytest.mark.parametrize("kept, offline, keyed, then", [
    pytest.param((KEPT, None), False, False, True, id="a question to send and no key is refused"),
    pytest.param((KEPT, None), False, True, False, id="with the key it is not"),
    pytest.param((KEPT, None), True, False, False, id="offline nothing would be sent"),
    pytest.param((KEPT, KEPT), False, False, False, id="every answer kept, nothing would be sent"),
    pytest.param((), False, False, False, id="no question, nothing would be sent"),
])
def test_whether_a_run_is_refused_for_want_of_a_key(kept, offline, keyed, then):
    assert needs_key(kept, offline, keyed) is then
