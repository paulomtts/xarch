"""What an eval of the profile's own asks, and what it reads, in a run: how it stands, one question about each thing
it reads in a file, the readings at or above its line with what is said of them, what has no answer, the value of an
example file, and the profile's order."""
from xarch.modules.review.application.logic.evaluation import held_as
from xarch.modules.review.application.logic.judging import (
    asked_of,
    below_app,
    example_value,
    in_order,
    standing,
    unasked_of,
    went,
)
from xarch.modules.review.domain.published import (
    CALIBRATED,
    NOT_CACHED,
    UNCALIBRATED,
    YES_NO,
    Choice,
    EvalRead,
    EvalReading,
    Option,
    Request,
    Unasked,
)
from xarch.modules.review.domain.values import Answer, Calibration, CodeFile, EvalText, Read, Reads

QUESTION = Choice("Does it decide the rule itself?", (Option("yes", ""), Option("no", "")), YES_NO)
RULE = EvalText("rule", QUESTION, ("yes",), None, "{name} may decide it ({value})", "read {name} against the litmus")
OTHER = EvalText("other", QUESTION, ("yes",))
RECORD = {"rule": Calibration(held_as(RULE), "m-1", "m-1.2", True, 0.6, (("a.py", 0.9), ("b.py", 0.8)),
                              (("c.py", 0.1),))}
TEXT = "class Doc:\n    def publish(self):\n        return 1\n\n\ndef helper():\n    return 2\n"
FILE = "app/modules/documents/domain/doc.py"


def said(yes: float) -> tuple[Answer, ...]:
    return (Answer("m-1.2", (("yes", yes), ("no", 1 - yes))),)


def test_an_eval_held_to_its_examples_stands_with_its_line_and_examples_and_one_never_held_with_why():
    assert standing(RULE, RECORD, "m-1") == EvalRead("rule", CALIBRATED, "", 0.6, 2, 1, "m-1.2", ask=QUESTION.ask,
                                                     form=YES_NO)
    assert standing(OTHER, RECORD, "m-1") == EvalRead("other", UNCALIBRATED, "it was never held to its examples",
                                                      ask=QUESTION.ask, form=YES_NO)


def test_one_question_is_asked_of_each_thing_an_eval_reads_in_a_file_with_its_own_lines_alone():
    found = Reads(CodeFile("modules/documents/domain/doc.py", "", TEXT), (Read((2, 3), "Doc.publish"),
                                                                         Read((6, 7), "helper")))
    assert asked_of(RULE, FILE, "domain", TEXT, found) == (
        Request(FILE, "domain", 40, "    def publish(self):\n        return 1\n", piece="Doc.publish", lines=(2, 3),
                asked="rule"),
        Request(FILE, "domain", 27, "def helper():\n    return 2\n", piece="helper", lines=(6, 7), asked="rule"))
    whole = asked_of(RULE, FILE, "domain", TEXT, Reads(CodeFile("x.py", "", TEXT), (Read((0, 0), ""),)))
    assert [(item.text, item.piece) for item in whole] == [(TEXT, "")]


def test_a_reading_at_or_above_the_line_is_listed_the_highest_first_with_its_message_and_fix():
    stood = standing(RULE, RECORD, "m-1")
    requests = (Request(FILE, "domain", 10, "a", piece="Doc.publish", lines=(2, 3), asked="rule"),
                Request(FILE, "domain", 10, "b", piece="helper", lines=(6, 7), asked="rule"),
                Request(FILE, "domain", 10, "c", piece="low", lines=(9, 9), asked="rule"))
    ran = went(RULE, stood, requests, (said(0.6), said(0.9), said(0.59)))
    assert ran.read == 3 and ran.readings == (
        EvalReading(FILE, 6, "helper", 0.9, "helper may decide it (0.90)", "read helper against the litmus"),
        EvalReading(FILE, 2, "Doc.publish", 0.6, "Doc.publish may decide it (0.60)",
                    "read Doc.publish against the litmus"))


def test_what_has_no_answer_is_said_and_read_no_further():
    requests = (Request(FILE, "domain", 1, "a", piece="helper", asked="rule"),)
    assert unasked_of(RULE, requests, (None,), False) == [Unasked(FILE, NOT_CACHED, "helper", "rule")]
    assert went(RULE, standing(RULE, RECORD, "m-1"), requests, (None,)).readings == ()


def test_the_value_of_an_example_file_is_the_highest_of_what_the_eval_reads_in_it():
    assert example_value(RULE, (), ()) == 0.0
    assert example_value(RULE, (Request("a.py", "", 1, "a"), Request("a.py", "", 1, "b")), (said(0.2), said(0.7))) == 0.7
    assert example_value(RULE, (Request("a.py", "", 1, "a"),), (None,)) is None


def test_the_evals_are_said_in_the_profile_order_and_a_file_by_its_path_below_the_app():
    assert in_order((EvalRead("other", UNCALIBRATED), EvalRead("rule", CALIBRATED)), (RULE, OTHER)) == (
        EvalRead("rule", CALIBRATED), EvalRead("other", UNCALIBRATED))
    assert below_app(FILE) == "modules/documents/domain/doc.py"
