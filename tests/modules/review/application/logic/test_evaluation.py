"""How an eval of the profile's own reads an answer (yes or no, a score, a choice in two orders), the lowest its line
may be, the hash of what it is held as, whether it may run, the verdict on its examples, and the text it reads."""
import pytest

from xarch.modules.review.application.logic.evaluation import cut, floor, held_as, orders, said, state, value, verdict
from xarch.modules.review.domain.published import (
    CALIBRATED,
    CHOOSE,
    FAILED_EXAMPLES,
    SCORE,
    STALE,
    UNCALIBRATED,
    YES_NO,
    Choice,
    Option,
)
from xarch.modules.review.domain.values import Answer, Calibration, EvalText

YES_OR_NO = Choice("Does it decide the rule itself?", (Option("yes", "it tests the fields"), Option("no", "")), YES_NO)
LEVELS = Choice("How much does it reach outside?", tuple(Option(str(n), f"level {n}") for n in range(5)), SCORE)
PICK = Choice("What does it let its caller do?", (Option("reads", "finds"), Option("writes", "saves"),
                                                 Option("sends", "sends out")), CHOOSE)
RULE = EvalText("rule", YES_OR_NO, ("yes",), None, "{name} ({value})", "read {file}",
                (("a.py", "x = 1\n"), ("b.py", "y = 2\n")), (("c.py", "z = 3\n"), ("d.py", "w = 4\n")), "function")


def answer(*probabilities: tuple[str, float]) -> Answer:
    return Answer("m-1", probabilities)


def test_a_choice_is_asked_as_written_and_reversed_and_any_other_form_once():
    assert orders(PICK) == (PICK, Choice(PICK.ask, tuple(reversed(PICK.options)), CHOOSE))
    assert orders(YES_OR_NO) == (YES_OR_NO,) and orders(LEVELS) == (LEVELS,)


@pytest.mark.parametrize("answers, question, flagged, read", [
    pytest.param((answer(("yes", 0.8), ("no", 0.2)),), YES_OR_NO, ("yes",), 0.8, id="a yes or no reads P(yes)"),
    pytest.param((answer(("0", 0.0), ("1", 0.0), ("2", 0.5), ("3", 0.5), ("4", 0.0)),), LEVELS, ("3", "4"), 0.625,
                 id="a score reads its expected level over 4"),
    pytest.param((answer(("reads", 0.1), ("writes", 0.1), ("sends", 0.8)),
                  answer(("sends", 0.6), ("writes", 0.2), ("reads", 0.2))), PICK, ("sends",), 0.7,
                 id="a choice reads its options flagged, the mean of its two orders"),
    pytest.param((answer(("reads", 0.1), ("writes", 0.5), ("sends", 0.4)),), PICK, ("writes", "sends"), 0.9,
                 id="a choice of several options flagged reads their sum"),
])
def test_the_value_of_an_answer(answers, question, flagged, read):
    assert value(answers, question, flagged) == pytest.approx(read)


def test_the_line_set_from_the_examples_is_never_below_a_half_nor_for_a_score_below_its_first_level_flagged():
    assert floor(YES_OR_NO, ("yes",)) == floor(PICK, ("sends",)) == 0.5
    assert floor(LEVELS, ("3", "4")) == 0.75 and floor(LEVELS, ("1", "2", "3", "4")) == 0.25


@pytest.mark.parametrize("changed", [
    pytest.param(EvalText("rule", Choice("Is it?", YES_OR_NO.options, YES_NO), ("yes",)), id="its question"),
    pytest.param(EvalText("rule", YES_OR_NO, ("yes",), 0.6), id="its line"),
    pytest.param(EvalText("rule", YES_OR_NO, ("yes",), reads="class"), id="what it reads"),
    pytest.param(EvalText("rule", YES_OR_NO, ("yes",), clean_examples=(("c.py", "z = 4\n"),)), id="an example"),
])
def test_what_an_eval_is_held_as_changes_with_what_it_asks_and_its_examples_but_not_with_its_words(changed):
    plain = EvalText("rule", YES_OR_NO, ("yes",))
    assert held_as(plain) != held_as(changed)
    assert held_as(plain) == held_as(EvalText("rule", YES_OR_NO, ("yes",), message="other", fix="other"))


def held(passed: bool = True, model: str = "m-1", of: EvalText = RULE) -> Calibration:
    return Calibration(held_as(of), model, "m-1.2", passed, 0.5, (("a.py", 0.9),), (("c.py", 0.1),),
                       "" if passed else "the gap is too small")


@pytest.mark.parametrize("record, then", [
    pytest.param(None, (UNCALIBRATED, "it was never held to its examples"), id="never held to its examples"),
    pytest.param(held(), (CALIBRATED, ""), id="held as it is written, by the model asked, and passed"),
    pytest.param(held(False), (FAILED_EXAMPLES, "its examples failed: the gap is too small"), id="its examples failed"),
    pytest.param(held(of=EvalText("rule", YES_OR_NO, ("yes",))),
                 (STALE, "its question, answer, scope, line or examples changed since it was held to its examples"),
                 id="it changed since"),
    pytest.param(held(model="m-0"), (STALE, "it was held to its examples by m-0, and m-1 is asked now"),
                 id="another model is asked now"),
])
def test_an_eval_runs_only_when_held_to_its_examples_as_written_by_the_model_asked_and_passed(record, then):
    assert state(RULE, record, "m-1") == then


@pytest.mark.parametrize("flagged, clean, written, then", [
    pytest.param((("a.py", 0.9), ("b.py", 0.8)), (("c.py", 0.1), ("d.py", 0.2)), None, (True, 0.5, ""),
                 id="every flagged above every clean by the gap: the line midway, never below a half"),
    pytest.param((("a.py", 0.95), ("b.py", 0.9)), (("c.py", 0.3), ("d.py", 0.4)), None, (True, 0.65, ""),
                 id="the line midway between the lowest flagged and the highest clean"),
    pytest.param((("a.py", 0.4), ("b.py", 0.9)), (("c.py", 0.61), ("d.py", 0.1)), None,
                 (False, 0.51, "clean example c.py reads 0.61, not below flagged example a.py at 0.40"),
                 id="a clean example at or above a flagged one"),
    pytest.param((("a.py", 0.6), ("b.py", 0.6)), (("c.py", 0.3), ("d.py", 0.5)), None,
                 (False, 0.55, "the flagged examples read 0.20 above the clean ones on the mean, under 0.4"),
                 id="a gap under 0.4"),
    pytest.param((("a.py", 0.45), ("b.py", 0.48)), (("c.py", 0.0), ("d.py", 0.0)), None,
                 (False, 0.5, "flagged example a.py reads 0.45, below the line 0.50"),
                 id="a flagged example below the lowest line"),
    pytest.param((("a.py", 0.9), ("b.py", 0.9)), (("c.py", 0.3), ("d.py", 0.2)), 0.25,
                 (False, 0.25, "clean example c.py reads 0.30, not below the line 0.25"),
                 id="a clean example at or above the line the profile writes"),
])
def test_the_verdict_on_the_examples(flagged, clean, written, then):
    assert verdict(flagged, clean, written, 0.5) == then


def test_what_an_eval_reads_is_the_lines_it_spans_or_the_text_whole_and_its_sentences_are_filled_in():
    assert cut("a\nb\nc\n", (2, 3)) == "b\nc\n" and cut("a\nb\n", (0, 0)) == "a\nb\n"
    assert cut("a\x0c\u2028\nb\nc\n", (2, 2)) == "b\n"
    assert said("{name} at {file}:{line} reads {value}", "app/x.py", 4, "Doc.publish", 0.834) == (
        "Doc.publish at app/x.py:4 reads 0.83")
    assert said("{name} reads {value}", "app/x.py", 0, "", 0.5) == "app/x.py reads 0.50"
