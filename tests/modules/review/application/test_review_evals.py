"""Use case: review chosen files around fakes, with evals of the profile's own: an eval runs only once it was held to
its examples (calibrated), as it is written now, by the model asked, and passed; it asks one question of each thing it
reads in each file judged, and lists the readings at or above its line; any other eval does not run, and says why."""
from dataclasses import replace
from pathlib import Path

import pytest

from tests.fakes.review import FakeAnswers, FakeCalibrations, FakeCode, FakeDecisionModel, FakeProfile
from tests.modules.review.application.helpers import controller
from tests.modules.review.builders import PARTS, found
from xarch.modules.review.contract import (
    CALIBRATED,
    DISAGREE,
    FAILED_EXAMPLES,
    NOT_CACHED,
    PASSED,
    STALE,
    UNCALIBRATED,
    YES_NO,
    Calibrate,
    Choice,
    EvalRead,
    EvalReading,
    KeyMissing,
    Option,
    Review,
    ReviewPlanned,
    ReviewReading,
    Unasked,
)
from xarch.modules.review.domain.values import Answer, Calibration, CodeFile, EvalText, Found, Read, Words

CWD, APP = Path("/src"), Path("/src/app")
RECORD = Path("/src/.xarch/calibration.json")
TEXT = "class Doc:\n    def publish(self):\n        if not self.title:\n            raise E\n" + "    x: int = 0\n" * 60
FILE = found("app/modules/documents/domain/doc.py", text=TEXT)
QUESTION = Choice("Does it decide the rule itself?", (Option("yes", "it tests the fields"), Option("no", "")), YES_NO)
RULE = EvalText("rule", QUESTION, ("yes",), None, "{name} may decide it ({value})", "read {name} against the litmus",
                (("domain/a.py", "a\n"), ("domain/b.py", "b\n")), (("domain/c.py", "c\n"), ("domain/d.py", "d\n")))
OTHER = EvalText("other", QUESTION, ("yes",))
PUBLISH = "    def publish(self):\n        if not self.title:\n            raise E\n"
READS = {("rule", TEXT): (Read((2, 4), "Doc.publish"),)}
PLACED = Answer("m-1.2", (("domain", 0.9), ("main", 0.1)))


def yes(p: float) -> Answer:
    return Answer("m-1.2", (("yes", p), ("no", 1 - p)))


def calibrated() -> Calibration:
    """The record of RULE held to its examples, every flagged one above every clean one."""
    held = FakeCalibrations()
    model = FakeDecisionModel({"a\n": yes(0.9), "b\n": yes(0.8), "c\n": yes(0.1), "d\n": yes(0.2)})
    controller(FakeCode({}), FakeProfile({"p": Words(PARTS, evals=(RULE,))}), model, FakeAnswers(), held).calibrate(
        Calibrate(CWD, APP, "p"))
    return held.kept[RECORD]["rule"]


HELD = calibrated()

def review(record: dict[str, Calibration], answers: dict[str, Answer], dry_run: bool = False, offline: bool = False,
           keyed: bool = True, evals: tuple[EvalText, ...] = (RULE,)):
    code = FakeCode({"app/x.py": Found((FILE,))}, reads=READS)
    profile = FakeProfile({"p": Words(PARTS, evals=evals)})
    model = FakeDecisionModel(answers, keyed)
    command = Review((Path("app/x.py"),), (), False, CWD, APP, "p", None, dry_run, None, offline)
    result = controller(code, profile, model, FakeAnswers(), FakeCalibrations({RECORD: record})).review(command)
    return result, model, code


STOOD = EvalRead("rule", CALIBRATED, "", 0.5, 2, 2, "m-1.2", ask=QUESTION.ask, form=YES_NO)


@pytest.mark.parametrize("record, answers, then", [
    pytest.param({"rule": HELD}, {TEXT: PLACED, PUBLISH: yes(0.83)}, (EvalRead(
        "rule", CALIBRATED, "", 0.5, 2, 2, "m-1.2", 1, (EvalReading(
            FILE.file, 2, "Doc.publish", 0.83, "Doc.publish may decide it (0.83)",
            "read Doc.publish against the litmus"),), QUESTION.ask, YES_NO),),
                 id="a calibrated eval reads what it reads in each file judged, listing a reading at or above its line"),
    pytest.param({"rule": HELD}, {TEXT: PLACED, PUBLISH: yes(0.4)}, (EvalRead(
        "rule", CALIBRATED, "", 0.5, 2, 2, "m-1.2", 1, (), QUESTION.ask, YES_NO),),
                 id="a reading below its line is not listed"),
    pytest.param({}, {TEXT: PLACED}, (EvalRead("rule", UNCALIBRATED, "it was never held to its examples",
                                               ask=QUESTION.ask, form=YES_NO),),
                 id="an eval never held to its examples does not run, and says so"),
    pytest.param({"rule": replace(HELD, passed=False, crossed="the gap is 0.21")},
                 {TEXT: PLACED}, (EvalRead("rule", FAILED_EXAMPLES, "its examples failed: the gap is 0.21",
                                           ask=QUESTION.ask, form=YES_NO),),
                 id="an eval whose examples failed does not run, and says what crossed"),
    pytest.param({"rule": replace(HELD, model="m-0")}, {TEXT: PLACED}, (EvalRead(
        "rule", STALE, "it was held to its examples by m-0, and m-1 is asked now", ask=QUESTION.ask, form=YES_NO),),
                 id="an eval held to its examples by another model is stale"),
    pytest.param({"rule": replace(HELD, held="another")}, {TEXT: PLACED}, (EvalRead(
        "rule", STALE, "its question, answer, scope, line or examples changed since it was held to its examples",
        ask=QUESTION.ask, form=YES_NO),), id="an eval changed since it was held to its examples is stale"),
])
def test_how_each_eval_goes_in_a_review(record, answers, then):
    result, _, _ = review(record, answers)
    assert isinstance(result, ReviewReading) and result.evals == then and result.complete


def test_an_eval_that_does_not_run_asks_nothing_and_the_evals_are_said_in_the_profile_order():
    result, model, code = review({"rule": HELD}, {TEXT: PLACED, PUBLISH: yes(0.83)}, evals=(OTHER, RULE))
    assert isinstance(result, ReviewReading)
    assert [item.asked for item in result.evals] == ["other", "rule"] and model.asked == [TEXT, PUBLISH]
    assert code.asked == [("rule", ("modules/documents/domain/doc.py",))]


def test_a_dry_run_shows_each_request_of_an_eval_that_would_run_and_how_each_eval_stands():
    result, model, _ = review({"rule": HELD}, {}, dry_run=True, keyed=False, evals=(RULE, OTHER))
    assert isinstance(result, ReviewPlanned) and model.asked == []
    assert [(item.asked, item.piece, item.text) for item in result.requests] == [("", "", TEXT),
                                                                                 ("rule", "Doc.publish", PUBLISH)]
    assert [item.state for item in result.evals] == [CALIBRATED, UNCALIBRATED] and result.evals[0] == STOOD


def test_a_question_of_an_eval_to_send_with_no_key_is_refused_before_anything_is_sent():
    result, model, _ = review({"rule": HELD}, {TEXT: PLACED}, keyed=False)
    assert result == KeyMissing("MODEL_KEY") and model.asked == []


def test_offline_a_question_of_an_eval_not_in_the_cache_is_unanswered():
    result, _, _ = review({"rule": HELD}, {}, offline=True)
    assert isinstance(result, ReviewReading) and not result.complete
    assert Unasked(FILE.file, NOT_CACHED, "Doc.publish", "rule") in result.unasked


DOUBTED = Answer("m-1.2", (("domain", 0.1), ("main", 0.9)))
VALUE = CodeFile("modules/documents/domain/value.py", "domain", "class Value: ...\n")


def held_placement(answer: Answer) -> FakeCalibrations:
    """The record of placement held to VALUE, which the decision model answers so."""
    held = FakeCalibrations()
    profile = FakeProfile({"p": Words(PARTS)}, examples={"p": ((VALUE,), ())})
    controller(FakeCode({}), profile, FakeDecisionModel({VALUE.text: answer}), FakeAnswers(), held).calibrate(
        Calibrate(CWD, APP, "p", ("placement",)))
    return held


@pytest.mark.parametrize("answer, doubtful, held", [
    pytest.param(Answer("m-1.2", (("domain", 0.2), ("main", 0.8))), False, DISAGREE,
                 id="a file of a part whose examples disagree is read, never doubtful"),
    pytest.param(Answer("m-1.2", (("domain", 0.9), ("main", 0.1))), True, PASSED,
                 id="a file of a part whose examples agree is doubtful below its line"),
])
def test_a_review_reads_how_placement_was_held_to_its_examples(answer, doubtful, held):
    calibrations = held_placement(answer)
    profile = FakeProfile({"p": Words(PARTS)}, examples={"p": ((VALUE,), ())})
    command = Review((Path("app/x.py"),), (), False, CWD, APP, "p")
    result = controller(FakeCode({"app/x.py": Found((FILE,))}), profile, FakeDecisionModel({TEXT: DOUBTED}),
                        FakeAnswers(), calibrations).review(command)
    assert isinstance(result, ReviewReading) and result.calibration.state == CALIBRATED
    assert result.readings[0].doubtful is doubtful and result.parts[0].held == held


def test_a_review_with_placement_held_to_other_examples_says_it_is_stale():
    calibrations = held_placement(Answer("m-1.2", (("domain", 0.9), ("main", 0.1))))
    profile = FakeProfile({"p": Words(PARTS)}, examples={"p": ((VALUE, VALUE), ())})
    result = controller(FakeCode({"app/x.py": Found((FILE,))}), profile, FakeDecisionModel({TEXT: DOUBTED}),
                        FakeAnswers(), calibrations).review(Review((Path("app/x.py"),), (), False, CWD, APP, "p"))
    assert isinstance(result, ReviewReading) and result.calibration.state == STALE
