"""The evals of the profile's own, worded: how each stands in a review (it runs only once calibrated; else why not and
what to run) and its readings with what to do; and a calibration: each eval's verdict, line and examples, what to do
about one that failed, and where the record is; in text and as JSON."""
import json
from pathlib import Path

from xarch.cli.reports.eval_report import (
    calibration_document,
    calibration_lines,
    calibration_plan_document,
    calibration_plan_lines,
    eval_documents,
    eval_lines,
    eval_plan_lines,
    shown_from,
    standing_document,
    standing_lines,
    unknown_evals,
)
from xarch.modules.review.contract import (
    CALIBRATED,
    DISAGREE,
    ELSEWHERE,
    FLAGGED,
    NOT_CACHED,
    PASSED,
    STALE,
    UNCALIBRATED,
    YES_NO,
    Calibrated,
    CalibrationPlanned,
    EvalHeld,
    EvalRead,
    EvalReading,
    ExampleRead,
    PartHeld,
    PlacementHeld,
    PlacementStanding,
    Request,
    Sender,
    Unasked,
)

SENDS = Sender("Model", "https://model.example.test", "m-1", "MODEL_KEY", False)
FILE = "app/modules/documents/application/services/publishing.py"
RAN = EvalRead("rule", CALIBRATED, "", 0.55, 3, 2, "m-1.2", 4, (EvalReading(
    FILE, 14, "PublishingService.publish", 0.83, "PublishingService.publish may decide a rule (0.83)",
    "read it against the litmus of domain/"),), "Does it decide the rule itself?", YES_NO)
STALE_ONE = EvalRead("wording", STALE, "it was held to its examples by m-0, and m-1 is asked now")
HELD = EvalHeld("rule", (ExampleRead("services/a.py", True, 0.9), ExampleRead("services/b.py", False, 0.1)), True, 0.5)
FAILED_ONE = EvalHeld("wording", (ExampleRead("services/a.py", True, 0.4), ExampleRead("services/b.py", False, 0.61)),
                      False, 0.5, "clean example services/b.py reads 0.61, not below flagged example services/a.py at "
                                  "0.40")


def test_an_eval_that_ran_lists_each_reading_with_what_to_do_and_one_that_did_not_says_why_and_what_to_run():
    lines = eval_lines((RAN, STALE_ONE))
    assert lines[:3] == ["", "evals of the profile's own",
                         "  rule   calibrated: held to 3 flagged and 2 clean examples by m-1.2, line 0.55; asked of 4; how "
                         "often it reads well-written code as flagged is not known"]
    assert f"    {FILE}:14 PublishingService.publish   0.83" in lines
    assert ("      what to do: read it against the litmus of domain/. A reading is a reason to look, not a finding."
            in lines)
    assert lines[-1] == ("  wording   not run: stale: it was held to its examples by m-0, and m-1 is asked now; run "
                         "`xarch review calibrate --eval wording`")
    assert eval_lines(()) == []


def test_an_eval_asked_of_nothing_says_so():
    assert eval_lines((EvalRead("rule", CALIBRATED, "", 0.5, 2, 2, "m-1"),))[-1] == (
        "    asked of nothing: no file judged holds what it reads in its scope")


def test_a_dry_run_says_the_question_of_each_eval_that_would_run_and_why_the_others_would_not():
    lines = eval_plan_lines((RAN, STALE_ONE))
    assert lines[2:4] == ["  rule   would run (line 0.55): Does it decide the rule itself?",
                          "    answered as yes or no, read as the probability of yes"]
    assert lines[4].startswith("  wording   would not run: stale:")


def test_the_json_of_an_eval_gives_its_state_what_to_run_its_line_and_its_readings():
    assert eval_documents((RAN, STALE_ONE)) == [
        {"id": "rule", "state": "calibrated", "why": None, "run": None, "line": 0.55,
         "ask": "Does it decide the rule itself?", "form": "yes-no", "examples": {"flagged": 3, "clean": 2},
         "model": "m-1.2", "asked": 4, "readings": [{"file": FILE, "line": 14, "name": "PublishingService.publish",
                                                    "value": 0.83, "message": RAN.readings[0].message,
                                                    "fix": RAN.readings[0].fix}]},
        {"id": "wording", "state": "stale", "why": STALE_ONE.why, "run": "xarch review calibrate --eval wording",
         "line": None, "ask": "", "form": "choice", "examples": {"flagged": 0, "clean": 0}, "model": None, "asked": 0,
         "readings": []}]


def test_a_calibration_says_each_verdict_with_its_line_and_examples_what_to_do_about_a_failure_and_the_record():
    done = Calibrated((HELD, FAILED_ONE), Path("/p/.xarch/calibration.json"), (), SENDS, 0, 4, 0, 0, "")
    lines = calibration_lines(done, ".xarch/calibration.json")
    assert "rule   passed: line 0.50 (set from the examples)" in lines
    assert "  flagged  services/a.py   0.90" in lines and "  clean    services/b.py   0.10" in lines
    assert ("wording   failed: clean example services/b.py reads 0.61, not below flagged example services/a.py at 0.40: "
            "make it one short rule about what the text shows; add a clean example of the case it must not catch"
            in lines)
    assert lines[-1] == "recorded in .xarch/calibration.json: commit it, so that every review reads the same verdicts"
    document = json.loads(calibration_document(done, ".xarch/calibration.json"))
    assert (document["passed"], document["complete"], document["record"]) == (False, True, ".xarch/calibration.json")
    assert document["calibrated"][0] == {"id": "rule", "complete": True, "passed": True, "line": 0.5,
                                         "line_by_hand": False, "crossed": None,
                                         "examples": [{"path": "services/a.py", "flagged": True, "value": 0.9},
                                                      {"path": "services/b.py", "flagged": False, "value": 0.1}]}


def test_a_calibration_with_examples_unanswered_says_it_is_incomplete_and_recorded_nothing_of_them():
    done = Calibrated((EvalHeld("rule", (), False, 0.0, "", False),), None,
                      (Unasked("services/a.py", NOT_CACHED, "", "rule"),), SENDS, 0, 0, 0, 0, "")
    lines = calibration_lines(done, "")
    assert "rule   not held: some of its examples have no answer (see unanswered)" in lines
    assert "  rule: services/a.py: not in the cache, and --offline sends nothing" in lines
    assert not any(line.startswith("recorded in") for line in lines)


def test_a_profile_with_no_eval_of_its_own_has_nothing_to_calibrate():
    done = Calibrated((), None, (), SENDS, 0, 0, 0, 0, "")
    assert calibration_lines(done, "")[-1] == ("nothing to calibrate: the profile writes no eval of its own and has no "
                                               "example")


def test_a_dry_run_of_a_calibration_says_what_leaves_the_machine_and_each_request_with_its_text():
    planned = CalibrationPlanned((Request("services/a.py", "", 8, "def a():\n", body="{}", piece="a", lines=(1, 1),
                                          asked="rule", example=FLAGGED),), ("rule",), 40, 10, (), SENDS)
    lines = calibration_plan_lines(planned)
    assert "the key alone allows it, and the key is not set now" in lines[2]
    assert "request 1 of 1: rule, flagged example services/a.py a (lines 1-1), 8 characters" in lines
    assert "    | def a():" in lines
    document = json.loads(calibration_plan_document(planned))
    assert document["requests"] == [{"id": "rule", "example": "services/a.py", "kind": "flagged", "part": None, "name": "a",
                                     "first": 1, "last": 1, "chars": 8, "cached": False, "text": "def a():\n",
                                     "body": "{}"}]


def test_evals_asked_for_that_the_profile_does_not_write_are_refused_with_those_it_does():
    assert unknown_evals(("x",), ("rule", "wording")) == "no eval of the profile's own named x: use rule, wording"
    assert unknown_evals(("x",), ()) == "no eval of the profile's own named x: the profile writes none under evals"
    assert shown_from(Path("/p/.xarch/calibration.json"), Path("/p")) == ".xarch/calibration.json"


PLACED = PlacementHeld("h", "m-1", "m-1.2", (PartHeld("domain", DISAGREE, "clean example a.py reads 0.12, below its line "
                                                                       "0.30", 2),
                                             PartHeld("services", PASSED, "", 3), PartHeld("kernel", ELSEWHERE)))


def test_a_calibration_says_each_part_of_placement_held_to_its_examples_and_that_they_are_a_sanity_check():
    lines = calibration_lines(Calibrated((), Path("/p/.xarch/calibration.json"), (), SENDS, 3, 0, 0, 0, "", PLACED),
                              ".xarch/calibration.json")
    assert lines[4:8] == [
        "placement   held to the docs' examples and the profile's own, by m-1.2; the examples are short, and short "
        "files read lower for being short: a sanity check of the litmus texts, not a way to set lines",
        "  domain   examples disagree: clean example a.py reads 0.12, below its line 0.30; read its litmus against the "
        "example, and the example against the litmus",
        "  services   passed (3 example(s) of its own)",
        "  kernel   measured elsewhere only: no example of its own"]


def test_a_review_says_whether_placement_was_held_to_its_examples_and_each_part_whose_examples_disagree():
    assert standing_lines(PlacementStanding(UNCALIBRATED, "it was never held to its examples")) == [
        "  held to its examples: no: uncalibrated: it was never held to its examples; run `xarch review calibrate "
        "--eval placement`"]
    held = standing_lines(PlacementStanding(CALIBRATED, "", PLACED.parts))
    assert held[1] == ("  placement of domain: examples disagree (clean example a.py reads 0.12, below its line 0.30): "
                       "its files are read, never marked doubtful") and len(held) == 2
    assert standing_document(PlacementStanding(CALIBRATED, "", PLACED.parts[1:2])) == {
        "state": "calibrated", "why": None, "parts": [{"part": "services", "verdict": "passed", "crossed": None,
                                                       "examples": 3}]}
