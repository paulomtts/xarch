"""Placement held to its examples: the hash of what it is held as, each part's verdict (its clean examples at or above
its line, a flagged one and every other part's example below it on it, none of its own measured elsewhere only), how
it stands against its record, and a part whose examples disagree never marking its files doubtful."""
import pytest

from xarch.modules.review.application.logic.placing import held_as, marked, standing, undoubted, verdicts
from xarch.modules.review.domain.published import (
    CALIBRATED,
    DISAGREE,
    ELSEWHERE,
    PASSED,
    STALE,
    UNCALIBRATED,
    Choice,
    Option,
    PartHeld,
    PartRead,
    PlacementHeld,
    PlacementStanding,
    Reading,
)
from xarch.modules.review.domain.values import CodeFile, PartText

PARTS = (PartText("domain", "domain/", "Is it a value?", "values", 0.3),
         PartText("services", "services/", "Is it a use case?", "use cases", 0.3),
         PartText("kernel", "kernel/", "Is it shared?", "shared", 0.2))
QUESTION = Choice("Which part?", tuple(Option(part.name, part.litmus) for part in PARTS))
VALUE, CASE = CodeFile("domain/value.py", "domain", "v\n"), CodeFile("services/case.py", "services", "c\n")
WRONG = CodeFile("domain/case.py", "domain", "c\n")


def on(**probabilities: float) -> dict[str, float]:
    return probabilities


@pytest.mark.parametrize("clean, flagged, then", [
    pytest.param(((VALUE, on(domain=0.8, services=0.1)), (CASE, on(domain=0.1, services=0.85))), (),
                 (PartHeld("domain", PASSED, "", 1), PartHeld("services", PASSED, "", 1), PartHeld("kernel", ELSEWHERE)),
                 id="each part's examples read on it at or above its line, and the others below: a part with none is "
                    "measured elsewhere only"),
    pytest.param(((VALUE, on(domain=0.2, services=0.7)),), (),
                 (PartHeld("domain", DISAGREE, "clean example domain/value.py reads 0.20, below its line 0.30", 1),
                  PartHeld("services", ELSEWHERE), PartHeld("kernel", ELSEWHERE)),
                 id="a clean example below its part's line"),
    pytest.param(((VALUE, on(domain=0.6, services=0.35)), (CASE, on(services=0.9))), (),
                 (PartHeld("domain", PASSED, "", 1),
                  PartHeld("services", DISAGREE, "example domain/value.py of domain reads 0.35 on it, not below its line "
                                                 "0.30", 1), PartHeld("kernel", ELSEWHERE)),
                 id="a deliberate claim: an example of another part reads at or above the line on it"),
    pytest.param(((VALUE, on(domain=0.9)),), ((WRONG, on(domain=0.4, services=0.6)),),
                 (PartHeld("domain", DISAGREE, "flagged example domain/case.py reads 0.40, not below its line 0.30", 2),
                  PartHeld("services", ELSEWHERE), PartHeld("kernel", ELSEWHERE)),
                 id="a flagged example lying in a part reads at or above its line"),
])
def test_each_part_held_to_the_examples(clean, flagged, then):
    assert verdicts(PARTS, clean, flagged) == then


def test_what_placement_is_held_as_changes_with_its_question_its_lines_and_its_examples():
    plain = held_as(QUESTION, PARTS, ((VALUE,), ()))
    assert plain != held_as(Choice("Where?", QUESTION.options), PARTS, ((VALUE,), ()))
    assert plain != held_as(QUESTION, (PARTS[0], PARTS[1], PartText("kernel", "kernel/", "Is it shared?", "", 0.25)),
                            ((VALUE,), ()))
    assert plain != held_as(QUESTION, PARTS, ((VALUE, CASE), ()))
    assert plain == held_as(QUESTION, PARTS, ((VALUE,), ()))


HELD = PlacementHeld("h", "m-1", "m-1.2", (PartHeld("domain", DISAGREE, "it crossed", 1), PartHeld("kernel", ELSEWHERE)))


@pytest.mark.parametrize("record, held, model, then", [
    pytest.param(None, "h", "m-1", PlacementStanding(UNCALIBRATED, "it was never held to its examples"),
                 id="never held"),
    pytest.param(HELD, "h", "m-1", PlacementStanding(CALIBRATED, "", HELD.parts), id="held as it is now"),
    pytest.param(HELD, "other", "m-1", PlacementStanding(STALE, "its parts, their texts, their lines or its examples "
                                                                "changed since it was held to its examples"),
                 id="changed since"),
    pytest.param(HELD, "h", "m-2", PlacementStanding(STALE, "it was held to its examples by m-1, and m-2 is asked now"),
                 id="another model asked"),
])
def test_how_placement_stands_against_its_record(record, held, model, then):
    assert standing(record, held, model) == then


def test_a_file_of_a_part_whose_examples_disagree_is_never_doubtful_and_each_part_says_how_it_was_held():
    stood = standing(HELD, "h", "m-1")
    doubted = Reading("app/domain/x.py", "domain", 900, 0.1, 0.3, True, (), "m-1")
    other = Reading("app/kernel/y.py", "kernel", 900, 0.1, 0.2, True, (), "m-1")
    assert [item.doubtful for item in undoubted((doubted, other), stood)] == [False, True]
    parts = (PartRead("domain", 1, 0, 0.3, False, False, False), PartRead("services", 1, 0, 0.3, False, False, False))
    assert [part.held for part in marked(parts, stood)] == [DISAGREE, ""]


def test_what_placement_is_held_as_changes_with_how_its_examples_are_masked():
    plain = held_as(QUESTION, PARTS, ((VALUE,), ()))
    assert plain != held_as(QUESTION, PARTS, ((VALUE,), ()), ("shop",))
    assert plain != held_as(QUESTION, PARTS, ((VALUE,), ()), (), ("Value",))
