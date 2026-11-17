"""Use case: hold the evals of the profile's own to their examples around fakes: each example file asked as review
would ask a file of the app, the verdict and the line read, and the record rewritten for each eval whose every example
has its answer; with --dry-run nothing is sent or recorded; offline only the answers kept are read."""
from dataclasses import dataclass, field, replace
from pathlib import Path

import pytest

from tests.fakes.review import FakeAnswers, FakeCalibrations, FakeCode, FakeDecisionModel, FakeProfile
from tests.modules.review.application.helpers import controller
from tests.modules.review.builders import PARTS
from xarch.kernel.source import CommentSpan, Import
from xarch.modules.review.contract import (
    CHOOSE,
    CLEAN,
    DISAGREE,
    ELSEWHERE,
    FLAGGED,
    NOT_CACHED,
    PASSED,
    REFUSED,
    YES_NO,
    Calibrate,
    Calibrated,
    CalibrationPlanned,
    Choice,
    EvalHeld,
    ExampleRead,
    HeldExample,
    KeyMissing,
    Option,
    PartHeld,
    Request,
    ReviewRefused,
    Sender,
    Unasked,
    UnknownEvals,
)
from xarch.modules.review.domain.values import Answer, Calibration, CodeFile, EvalText, Read, Words

CWD, APP = Path("/src"), Path("/src/app")
RECORD = Path("/src/.xarch/calibration.json")
SENDS = Sender("Model", "https://model.example.test", "m-1", "MODEL_KEY", True)
QUESTION = Choice("Does it decide the rule itself?", (Option("yes", "it tests the fields"), Option("no", "")), YES_NO)
BAD, GOOD, WORSE, FINE = "def a(doc):\n    if doc.x: raise E\n", "def a(doc):\n    doc.a()\n", "def b(doc): ...\n", "b\n"
RULE = EvalText("rule", QUESTION, ("yes",), None, "{name} ({value})", "read it",
                (("domain/a.py", BAD), ("domain/b.py", WORSE)), (("domain/a.py", GOOD), ("domain/b.py", FINE)), "f")
PICK = Choice("What does it let its caller do?", (Option("reads", "finds"), Option("writes", "saves"),
                                                 Option("sends", "sends out")), CHOOSE)
SENDING = EvalText("sending", PICK, ("sends",), 0.6, "{name}", "read it", (("domain/a.py", BAD), ("domain/b.py", WORSE)),
                   (("domain/a.py", GOOD), ("domain/b.py", FINE)), "class")


def yes(p: float) -> Answer:
    return Answer("m-1.2", (("yes", p), ("no", 1 - p)), 10, 1)


PASSING = {BAD: yes(0.9), WORSE: yes(0.8), GOOD: yes(0.1), FINE: yes(0.2)}
NARROW = {BAD: yes(0.6), WORSE: yes(0.6), GOOD: yes(0.3), FINE: yes(0.4)}
CROSSED = {BAD: yes(0.9), WORSE: yes(0.3), GOOD: yes(0.1), FINE: yes(0.4)}
EXAMPLES = (ExampleRead("domain/a.py", True, 0.9), ExampleRead("domain/b.py", True, 0.8),
            ExampleRead("domain/a.py", False, 0.1), ExampleRead("domain/b.py", False, 0.2))


def pick(sends: float) -> Answer:
    rest = (1 - sends) / 2
    return Answer("m-1.2", (("reads", rest), ("writes", rest), ("sends", sends)))


@dataclass
class Given:
    evals: tuple[EvalText, ...] = (RULE,)
    answers: dict = field(default_factory=lambda: dict(PASSING))
    keyed: bool = True
    by_order: dict = field(default_factory=dict)
    recorded: dict = field(default_factory=dict)
    refused: dict = field(default_factory=dict)


def calibrate(given: Given, cmd: Calibrate):
    profile = FakeProfile({"cli": Words(PARTS, evals=given.evals)}, refused={"gone": "gone: cannot read the file"})
    model = FakeDecisionModel(given.answers, keyed=given.keyed, by_order=given.by_order, refused=given.refused)
    held = FakeCalibrations({RECORD: given.recorded})
    result = controller(FakeCode({}), profile, model, FakeAnswers(), held).calibrate(cmd)
    return result, held, model


@pytest.mark.parametrize("given, when, then", [
    pytest.param(Given(), Calibrate(CWD, APP, "cli"),
                 Calibrated((EvalHeld("rule", EXAMPLES, True, 0.5),), RECORD, (), SENDS, 4, 0, 40, 4, "", None, ("m-1.2",)),
                 id="an eval whose flagged examples read above its clean ones by the gap passes, its line set midway"),
    pytest.param(Given(answers=NARROW), Calibrate(CWD, APP, "cli"), Calibrated((EvalHeld("rule", (
        ExampleRead("domain/a.py", True, 0.6), ExampleRead("domain/b.py", True, 0.6),
        ExampleRead("domain/a.py", False, 0.3), ExampleRead("domain/b.py", False, 0.4)), False, 0.5,
        "the flagged examples read 0.25 above the clean ones on the mean, under 0.4"),), RECORD, (), SENDS, 4, 0, 40, 4,
        "", None, ("m-1.2",)),
                 id="an eval whose examples are apart by less than the gap fails"),
    pytest.param(Given(answers=CROSSED), Calibrate(CWD, APP, "cli"), Calibrated((EvalHeld("rule", (
        ExampleRead("domain/a.py", True, 0.9), ExampleRead("domain/b.py", True, 0.3),
        ExampleRead("domain/a.py", False, 0.1), ExampleRead("domain/b.py", False, 0.4)), False, 0.5,
        "clean example domain/b.py reads 0.40, not below flagged example domain/b.py at 0.30"),), RECORD, (), SENDS, 4,
        0, 40, 4, "", None, ("m-1.2",)),
                 id="an eval a clean example of which reads above a flagged one fails, naming both"),
    pytest.param(Given(evals=(SENDING,), answers={}, by_order={
        (BAD, "reads"): pick(0.9), (BAD, "sends"): pick(0.3), (WORSE, "reads"): pick(0.9), (WORSE, "sends"): pick(0.9),
        (GOOD, "reads"): pick(0.1), (GOOD, "sends"): pick(0.1), (FINE, "reads"): pick(0.1), (FINE, "sends"): pick(0.1)}),
                 Calibrate(CWD, APP, "cli"), Calibrated((EvalHeld("sending", (
                     ExampleRead("domain/a.py", True, 0.6), ExampleRead("domain/b.py", True, 0.9),
                     ExampleRead("domain/a.py", False, 0.1), ExampleRead("domain/b.py", False, 0.1)), True, 0.6,
                     by_hand=True),), RECORD, (), SENDS, 8, 0, 0, 0, "", None, ("m-1.2",)),
                 id="a choice is asked in both orders and read on their mean, against the line the profile writes"),
    pytest.param(Given(answers={BAD: yes(0.9), WORSE: yes(0.8), GOOD: yes(0.1)}), Calibrate(CWD, APP, "cli", offline=True),
                 Calibrated((EvalHeld("rule", (), False, 0.0, "", False),), None, tuple(
                     Unasked(path, NOT_CACHED, "", "rule", kind) for path, kind in (
                         ("domain/a.py", FLAGGED), ("domain/b.py", FLAGGED), ("domain/a.py", CLEAN),
                         ("domain/b.py", CLEAN))), SENDS, 0, 0, 0, 0, ""),
                 id="offline, an eval with an example not in the cache is not held, and nothing is recorded"),
    pytest.param(Given(), Calibrate(CWD, APP, "cli", ("other",)), UnknownEvals(("other",), ("placement", "rule")),
                 id="an eval the profile does not write is refused, with the ones it does"),
    pytest.param(Given(keyed=False), Calibrate(CWD, APP, "cli"), KeyMissing("MODEL_KEY"),
                 id="a calibration that would send with no key is refused before anything is sent"),
    pytest.param(Given(), Calibrate(CWD, APP, "gone"), ReviewRefused("gone: cannot read the file"),
                 id="a profile that cannot be used is refused with why"),
])
def test_calibrate(given, when, then):
    assert calibrate(given, when)[0] == then


def test_an_example_refused_alone_is_unanswered_with_the_words_its_eval_is_not_held_and_the_others_are_asked():
    result, held, model = calibrate(Given(evals=(RULE, SENDING), answers=dict(PASSING),
                                          refused={BAD: "TypeSafe answered 413: too large"},
                                          by_order={(t, o): pick(0.9 if t in (BAD, WORSE) else 0.1)
                                                    for t in (WORSE, GOOD, FINE) for o in ("reads", "sends")}),
                                    Calibrate(CWD, APP, "cli"))
    assert isinstance(result, Calibrated) and result.failure == "" and not result.complete
    assert result.unasked == (Unasked("domain/a.py", REFUSED, "", "rule", FLAGGED, "TypeSafe answered 413: too large"),
                              Unasked("domain/a.py", REFUSED, "", "sending", FLAGGED,
                                      "TypeSafe answered 413: too large"))
    assert [item.complete for item in result.held] == [False, False] and held.kept.get(RECORD, {}) == {}
    assert model.asked.count(WORSE) == 3 and model.asked.count(FINE) == 3


def test_a_placement_example_refused_alone_leaves_placement_unheld_and_the_next_example_is_asked():
    profile = FakeProfile({"cli": Words(PARTS, examples_root="app")}, examples={"cli": ((VALUE, START), ())})
    model = FakeDecisionModel(placed((START, {"domain": 0.1, "main": 0.9})), refused={VALUE.text: "too large"})
    held = FakeCalibrations()
    result = controller(FakeCode({}), profile, model, FakeAnswers(), held).calibrate(Calibrate(CWD, APP, "cli"))
    assert isinstance(result, Calibrated) and result.placement is None and result.failure == ""
    assert result.unasked == (Unasked(VALUE.file, REFUSED, "", "placement", CLEAN, "too large"),)
    assert model.asked == [VALUE.text, START.text] and held.placed == {}


def test_the_record_holds_each_eval_held_by_its_hash_the_model_asked_and_the_values_and_drops_one_no_longer_written():
    _, held, _ = calibrate(Given(recorded={"gone": Calibration("x", "m-1", "m-1", True, 0.5)}), Calibrate(CWD, APP, "cli"))
    entry = held.kept[RECORD]["rule"]
    assert list(held.kept[RECORD]) == ["rule"] and len(entry.held) == 64
    assert entry == Calibration(entry.held, "m-1", "m-1.2", True, 0.5, (("domain/a.py", 0.9), ("domain/b.py", 0.8)),
                                (("domain/a.py", 0.1), ("domain/b.py", 0.2)), "")
    changed = EvalText("rule", Choice("Is it?", QUESTION.options, YES_NO), ("yes",), None, "", "", RULE.flagged_examples,
                       RULE.clean_examples, "f")
    _, again, _ = calibrate(Given(evals=(changed,)), Calibrate(CWD, APP, "cli"))
    assert again.kept[RECORD]["rule"].held != entry.held


def test_an_eval_not_asked_for_keeps_its_record():
    kept = Calibration("x", "m-1", "m-1", True, 0.5)
    _, held, _ = calibrate(Given(evals=(RULE, SENDING), recorded={"sending": kept}), Calibrate(CWD, APP, "cli", ("rule",)))
    assert held.kept[RECORD]["sending"] == kept and "rule" in held.kept[RECORD]


def test_a_dry_run_sends_nothing_records_nothing_and_shows_each_request_of_each_example():
    found, held, model = calibrate(Given(keyed=False), Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(found, CalibrationPlanned) and model.asked == [] and held.kept[RECORD] == {}
    assert [(item.file, item.example, item.text) for item in found.requests] == [
        ("domain/a.py", FLAGGED, BAD), ("domain/b.py", FLAGGED, WORSE), ("domain/a.py", CLEAN, GOOD),
        ("domain/b.py", CLEAN, FINE)]
    assert found.requests[0] == Request("domain/a.py", "", len(BAD), BAD, body=f"{QUESTION.ask} 2 {BAD}", asked="rule",
                                        example=FLAGGED)
    assert (found.evals, found.sends.keyed) == (("rule",), False)


def test_what_an_eval_reads_in_an_example_is_asked_alone():
    code = FakeCode({}, reads={("rule", BAD): (Read((2, 2), "a"),)})
    profile = FakeProfile({"cli": Words(PARTS, evals=(RULE,))})
    model = FakeDecisionModel({"    if doc.x: raise E\n": yes(0.9), WORSE: yes(0.8), GOOD: yes(0.1), FINE: yes(0.2)})
    found = controller(code, profile, model, FakeAnswers()).calibrate(Calibrate(CWD, APP, "cli"))
    assert isinstance(found, Calibrated) and found.passed and "    if doc.x: raise E\n" in model.asked


VALUE = CodeFile("modules/documents/domain/value.py", "domain", "class Value: ...\n")
START = CodeFile("__main__.py", "main", "run()\n")
STRAY = CodeFile("stray/x.py", "", "x = 1\n")
WRONG = CodeFile("modules/documents/domain/start.py", "domain", "run(now)\n")


def placed(*examples: tuple[CodeFile, dict[str, float]]) -> dict:
    return {example.text: Answer("m-1.2", tuple(probabilities.items())) for example, probabilities in examples}


def holding(answers: dict, clean: tuple[CodeFile, ...], flagged: tuple[CodeFile, ...] = (), cmd=None):
    profile = FakeProfile({"cli": Words(PARTS, examples_root="app")}, examples={"cli": (clean, flagged)})
    held = FakeCalibrations()
    result = controller(FakeCode({}), profile, FakeDecisionModel(answers), FakeAnswers(), held).calibrate(
        cmd or Calibrate(CWD, APP, "cli"))
    return result, held


def test_placement_is_held_to_the_docs_examples_and_its_own_each_part_with_its_verdict_and_recorded():
    answers = placed((VALUE, {"domain": 0.9, "main": 0.1}), (START, {"domain": 0.4, "main": 0.6}),
                     (WRONG, {"domain": 0.1, "main": 0.9}))
    result, held = holding(answers, (VALUE, START, STRAY), (WRONG,))
    assert isinstance(result, Calibrated) and result.complete and result.passed and result.record == RECORD
    assert result.placement is not None and result.placement.parts == (
        PartHeld("domain", DISAGREE, "example __main__.py of main reads 0.40 on it, not below its line 0.30", 2),
        PartHeld("main", PASSED, "", 1))
    assert held.placed[RECORD] == result.placement and held.kept == {}


def test_a_dry_run_shows_each_example_placement_is_asked_of_and_an_example_in_no_part_is_not():
    result, _ = holding({}, (VALUE, STRAY), (WRONG,), Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(result, CalibrationPlanned) and result.evals == ("placement",)
    assert [(item.file, item.asked, item.example) for item in result.requests] == [
        ("modules/documents/domain/value.py", "placement", CLEAN), ("modules/documents/domain/start.py", "placement",
                                                                    FLAGGED)]


def test_offline_placement_with_an_example_not_in_the_cache_is_not_held_and_names_it():
    result, held = holding(placed((VALUE, {"domain": 0.9})), (VALUE, START), (),
                           Calibrate(CWD, APP, "cli", ("placement",), offline=True))
    assert isinstance(result, Calibrated) and result.placement is None and not result.complete
    assert result.unasked == (Unasked("modules/documents/domain/value.py", NOT_CACHED, "", "placement", CLEAN),
                              Unasked("__main__.py", NOT_CACHED, "", "placement", CLEAN)) and held.placed == {}


def test_placement_alone_is_held_when_it_alone_is_asked_for_and_an_eval_alone_holds_placement_not():
    result, held = holding(placed((VALUE, {"domain": 0.9})), (VALUE,), (), Calibrate(CWD, APP, "cli", ("placement",)))
    assert isinstance(result, Calibrated) and result.placement is not None and RECORD in held.placed
    profile = FakeProfile({"cli": Words(PARTS, evals=(RULE,))}, examples={"cli": ((VALUE,), ())})
    calibrations = FakeCalibrations()
    controller(FakeCode({}), profile, FakeDecisionModel(dict(PASSING)), FakeAnswers(), calibrations).calibrate(
        Calibrate(CWD, APP, "cli", ("rule",)))
    assert calibrations.placed == {} and "rule" in calibrations.kept[RECORD]


def test_placement_s_examples_are_masked_as_written_for_their_own_app_whatever_the_project_s_app_is_named():
    imported = Import(1, ("app", "modules", "documents", "domain", "value"), ("Value",),
                      written="app.modules.documents.domain.value")
    example = CodeFile("modules/documents/domain/use.py", "domain",
                       "from app.modules.documents.domain.value import Value\n", (imported,))
    result, _ = holding({}, (example,), (), Calibrate(CWD, Path("/src/shop"), "cli", dry_run=True))
    assert isinstance(result, CalibrationPlanned)
    assert [item.text for item in result.requests] == ["from <masked> import Value\n"]


UNUSABLE = "it holds a character a request header cannot carry; set it to the key alone"


def test_a_key_that_cannot_be_used_refuses_a_calibration_that_would_send_and_blocks_no_dry_run_nor_one_offline():
    profile = FakeProfile({"cli": Words(PARTS, evals=(RULE,))})
    model = FakeDecisionModel(PASSING, unusable=UNUSABLE)
    held = FakeCalibrations({RECORD: {}})
    calibrating = controller(FakeCode({}), profile, model, FakeAnswers(), held)
    assert calibrating.calibrate(Calibrate(CWD, APP, "cli")) == ReviewRefused(f"MODEL_KEY cannot be used: {UNUSABLE}")
    planned = calibrating.calibrate(Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(planned, CalibrationPlanned) and planned.sends.unusable == UNUSABLE
    offline = calibrating.calibrate(Calibrate(CWD, APP, "cli", offline=True))
    assert isinstance(offline, Calibrated) and {item.why for item in offline.unasked} == {NOT_CACHED}
    assert model.tried == [] and held.kept[RECORD] == {}


THIRD = "def c(doc):\n    if doc.y: raise E\n"
WIDER = EvalText("rule", QUESTION, ("yes",), None, "{name} ({value})", "read it",
                 (("domain/a.py", BAD), ("domain/b.py", WORSE), ("drafts/c.py", THIRD)),
                 (("domain/a.py", GOOD), ("domain/b.py", FINE)), "f")


def test_an_example_review_never_matches_is_never_sent_is_listed_held_back_and_the_eval_held_on_the_rest():
    given = Given(evals=(WIDER,), answers=dict(PASSING) | {THIRD: yes(0.1)})
    profile = FakeProfile({"cli": Words(PARTS, ("drafts",), evals=(WIDER,))})
    model, held = FakeDecisionModel(given.answers), FakeCalibrations({RECORD: {}})
    calibrating = controller(FakeCode({}), profile, model, FakeAnswers(), held)
    planned = calibrating.calibrate(Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(planned, CalibrationPlanned) and THIRD not in [item.text for item in planned.requests]
    assert planned.held_back == (HeldExample("rule", FLAGGED, "drafts/c.py", "drafts"),)
    done = calibrating.calibrate(Calibrate(CWD, APP, "cli"))
    assert isinstance(done, Calibrated) and THIRD not in model.asked and done.passed
    assert done.held_back == (HeldExample("rule", FLAGGED, "drafts/c.py", "drafts"),)
    assert [item.path for item in done.held[0].examples] == ["domain/a.py", "domain/b.py", "domain/a.py", "domain/b.py"]
    _, plain, _ = calibrate(Given(), Calibrate(CWD, APP, "cli"))
    _, wider, _ = calibrate(Given(evals=(WIDER,), answers=given.answers), Calibrate(CWD, APP, "cli"))
    assert held.kept[RECORD]["rule"].held == plain.kept[RECORD]["rule"].held != wider.kept[RECORD]["rule"].held


def test_an_eval_left_with_too_few_examples_by_review_never_is_not_held_sends_nothing_and_is_recorded_failed():
    profile = FakeProfile({"cli": Words(PARTS, ("domain/a.py",), evals=(RULE,))})
    model, held = FakeDecisionModel(dict(PASSING)), FakeCalibrations({RECORD: {}})
    calibrating = controller(FakeCode({}), profile, model, FakeAnswers(), held)
    planned = calibrating.calibrate(Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(planned, CalibrationPlanned) and planned.requests == () and planned.too_few == (("rule", FLAGGED),)
    assert planned.held_back == (HeldExample("rule", FLAGGED, "domain/a.py", "domain/a.py"),
                                 HeldExample("rule", CLEAN, "domain/a.py", "domain/a.py"))
    done = calibrating.calibrate(Calibrate(CWD, APP, "cli"))
    why = "fewer than 2 of its flagged examples remain once review.never holds some back"
    assert isinstance(done, Calibrated) and model.asked == [] and not done.passed and done.complete
    assert done.held == (EvalHeld("rule", (), False, 0.0, why, too_few=True),)
    entry = held.kept[RECORD]["rule"]
    _, plain, _ = calibrate(Given(), Calibrate(CWD, APP, "cli"))
    assert entry == Calibration(entry.held, "m-1", "m-1", False, 0.0, crossed=why)
    assert len(entry.held) == 64 and entry.held != plain.kept[RECORD]["rule"].held


def test_a_placement_example_review_never_matches_is_never_sent_and_its_part_is_then_measured_elsewhere_only():
    profile = FakeProfile({"cli": Words(PARTS, ("modules/*/domain/value.py",), examples_root="app")},
                          examples={"cli": ((VALUE, START), ())})
    model, held = FakeDecisionModel(placed((START, {"domain": 0.1, "main": 0.9}))), FakeCalibrations()
    calibrating = controller(FakeCode({}), profile, model, FakeAnswers(), held)
    planned = calibrating.calibrate(Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(planned, CalibrationPlanned) and [item.file for item in planned.requests] == [START.file]
    assert planned.held_back == (HeldExample("placement", CLEAN, VALUE.file, "modules/*/domain/value.py"),)
    done = calibrating.calibrate(Calibrate(CWD, APP, "cli"))
    assert isinstance(done, Calibrated) and model.asked == [START.text] and done.placement is not None
    assert done.held_back == planned.held_back
    assert done.placement.parts == (PartHeld("domain", ELSEWHERE), PartHeld("main", PASSED, "", 1))


def test_placement_s_examples_are_sent_with_their_comments_cut_in_a_dry_run_and_a_calibration_alike():
    example = CodeFile("modules/documents/domain/noted.py", "domain",
                       "# an invariant: domain\nclass Value:  # one value\n    text = '# kept'\n",
                       comments=(CommentSpan(1, 0, 22), CommentSpan(2, 14, 25)))
    sent = "\nclass Value:\n    text = '# kept'\n"
    planned, _ = holding({}, (example,), (), Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(planned, CalibrationPlanned)
    assert [(item.text, item.chars) for item in planned.requests] == [(sent, len(sent))]
    result, held = holding({sent: Answer("m-1.2", (("domain", 0.9), ("main", 0.1)))}, (example,))
    assert isinstance(result, Calibrated) and result.placement is not None and RECORD in held.placed


def test_an_eval_s_own_examples_are_sent_with_their_comments_cut_in_a_dry_run_and_a_calibration_alike():
    noted = "def a(doc):\n    # it decides here\n    if doc.x: raise E  # the rule\n"
    rule = replace(RULE, flagged_examples=(("domain/a.py", noted), ("domain/b.py", WORSE)))
    code = FakeCode({}, comments={noted: (CommentSpan(2, 4, 21), CommentSpan(3, 23, 33))})
    sent = "def a(doc):\n\n    if doc.x: raise E\n"
    profile = FakeProfile({"cli": Words(PARTS, evals=(rule,))})
    planned = controller(code, profile, FakeDecisionModel({}), FakeAnswers()).calibrate(
        Calibrate(CWD, APP, "cli", dry_run=True))
    assert isinstance(planned, CalibrationPlanned) and planned.requests[0].text == sent
    model = FakeDecisionModel({sent: yes(0.9), WORSE: yes(0.8), GOOD: yes(0.1), FINE: yes(0.2)})
    found = controller(code, profile, model, FakeAnswers()).calibrate(Calibrate(CWD, APP, "cli"))
    assert isinstance(found, Calibrated) and found.passed and model.asked[0] == sent
    assert not any("decides here" in text or "the rule" in text for text in model.asked)
