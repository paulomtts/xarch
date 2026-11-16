"""xarch review, shown: a dry run and a reading as text and as JSON, and every refusal in words."""
import json
from dataclasses import replace

from xarch.cli.reports.review_report import (
    ADVISORY,
    all_and_others,
    no_key,
    nothing_chosen,
    plan_document,
    plan_lines,
    reading_document,
    reading_lines,
    too_many,
)
from xarch.modules.review.contract import (
    BY_LIST,
    BY_PATHS,
    FAILED,
    MISSING,
    NEVER,
    NOT_CACHED,
    SMALL,
    Choice,
    LeftOut,
    Option,
    PartRead,
    Reading,
    Request,
    ReviewPlanned,
    ReviewReading,
    Sender,
    Unasked,
)

QUESTION = Choice("Which part?", (Option("domain", "Is it an invariant?"), Option("main", "starts the app")))
SENDS = Sender("Model", "https://model.example.test", "m-1", "MODEL_KEY", False)
PLANNED = ReviewPlanned((BY_PATHS, BY_LIST), 3, (Request("app/a.py", "domain", 1200, "from <masked> import A\n\nx = 1\n",
                                                         False, '{"state": "..."}'),),
                        (LeftOut("app/b.py", SMALL, 612), LeftOut("app/c.py", MISSING)), QUESTION, ("main",), 1250, 313,
                        (), SENDS)


def test_a_dry_run_says_first_what_review_is_that_nothing_was_sent_and_what_leaves_the_machine():
    lines = plan_lines(PLANNED)
    assert lines[0] == f"review: advisory. {ADVISORY}"
    assert lines[1] == "Nothing was sent (--dry-run)."
    assert lines[2] == ("Without --dry-run, review sends to Model (https://model.example.test), as the model m-1, the "
                        "masked text of each file below that is not in the cache and the question after it: nothing "
                        "else of the project. It sends whenever MODEL_KEY is set: the key alone allows it, and the key "
                        "is not set now.")
    assert lines[3] == ("3 file(s) found (paths, --files-from), 1 to be judged, 2 left out; 1 request(s), 1,250 "
                        "characters, about 313 tokens; 0 in the cache already.")
    assert plan_lines(replace(PLANNED, sends=replace(SENDS, keyed=True)))[2].endswith("and the key is set now.")


def test_a_dry_run_shows_the_question_once_and_each_request_with_the_exact_text_it_would_send():
    lines = plan_lines(PLANNED)
    assert lines[5:10] == ["the question each request carries:", "  Which part?",
                           "  options: 2 parts, each described by its litmus test (by its role only: main)",
                           "    domain: Is it an invariant?", "    main: starts the app"]
    assert lines[10:12] == ["", "masked in each text: the dotted name each import of the app's own code imports from, "
                                "and every e-mail address, always; and what review.mask hides: nothing more"]
    assert lines[12:18] == ["", "request 1 of 1: app/a.py (domain, 1,200 characters)", "    | from <masked> import A",
                            "    |", "    | x = 1", ""]
    assert lines[18:] == ["left out:", "  app/b.py: under 800 characters (612)", "  app/c.py: not there"]


def test_a_dry_run_says_the_texts_review_mask_hides_and_each_file_review_never_sends_with_the_path_that_matched():
    held = replace(PLANNED, left_out=(LeftOut("app/k.py", NEVER, 900, "**/k.py"),), mask=("Northwind", "DOC-*"))
    lines = plan_lines(held)
    assert lines[11].endswith("and what review.mask hides: Northwind, DOC-*")
    assert lines[-2:] == ["left out:", "  app/k.py: held back by review.never (**/k.py)"]
    document = json.loads(plan_document("cli", held))
    assert document["mask"] == ["Northwind", "DOC-*"]
    assert document["selection"]["left_out"] == [{"file": "app/k.py", "why": "never", "chars": 900,
                                                  "pattern": "**/k.py"}]


def test_the_json_of_a_dry_run_holds_every_request_in_full_and_the_question_once():
    assert json.loads(plan_document("cli", PLANNED)) == {
        "ok": True, "advisory": ADVISORY, "profile": "cli", "dry_run": True, "sent": False,
        "selection": {"by": ["paths", "files-from"], "found": 3, "judged": 1,
                      "left_out": [{"file": "app/b.py", "why": "small", "chars": 612, "pattern": None},
                                   {"file": "app/c.py", "why": "missing", "chars": 0, "pattern": None}]},
        "question": {"ask": "Which part?", "role_only": ["main"],
                     "options": [{"name": "domain", "description": "Is it an invariant?"},
                                 {"name": "main", "description": "starts the app"}]},
        "requests": [{"file": "app/a.py", "part": "domain", "chars": 1200, "cached": False,
                      "text": "from <masked> import A\n\nx = 1\n", "body": '{"state": "..."}'}],
        "characters": 1250, "tokens": 313, "reorders": 0, "mask": [],
        "sends": {"name": "Model", "at": "https://model.example.test", "model": "m-1", "key": "MODEL_KEY", "keyed": False}}


def test_a_request_in_the_cache_already_is_said_not_to_be_sent():
    kept = replace(PLANNED, requests=(replace(PLANNED.requests[0], cached=True),))
    assert "request 1 of 1: app/a.py (domain, 1,200 characters, in the cache: not sent)" in plan_lines(kept)
    assert plan_lines(kept)[3].endswith("; 1 in the cache already.")


def test_a_review_with_nothing_chosen_names_every_way_to_choose():
    said = nothing_chosen()
    assert said.startswith("review reads only the files it is given, and none was")
    assert all(way in said for way in ("as paths", "--files-from -", "--all"))


def test_each_refusal_says_what_to_do():
    assert "without paths and without --files-from" in all_and_others()
    assert too_many(60, 50).startswith("60 files would be judged, more than one run judges (50): choose fewer, or raise "
                                       "--max-files")
    assert no_key("MODEL_KEY") == ("no key: set MODEL_KEY, or run --dry-run to see what would be sent, or --offline to "
                                   "use cached answers only")


DOUBTFUL = Reading("app/modules/documents/adapters/export.py", "adapters", 2140, 0.0812, 0.3, True,
                   (("adapters", 0.0812), ("logic", 0.9188)), "m-1.0.1")
PLACED = Reading("app/modules/documents/domain/document.py", "domain", 1200, 0.71, 0.3, False,
                 (("domain", 0.71), ("logic", 0.29)), "m-1.0.1")
READ = ReviewReading((BY_PATHS,), 4, (DOUBTFUL, PLACED), (LeftOut("app/b.py", SMALL, 612),), (), replace(SENDS, keyed=True),
                     1, 1, 2400, 3, "", ())


def test_a_reading_says_what_review_is_what_was_sent_and_each_doubtful_file_with_what_to_do_naming_no_other_part():
    lines = reading_lines(READ)
    assert lines[:3] == [f"review: advisory. {ADVISORY}",
                         "Model m-1. 4 file(s) found (paths), 2 judged, 1 left out. Asked 1, from cache 1.",
                         "Sent 1 request(s) to Model (https://model.example.test): 2,400 input tokens, 3 output tokens."]
    assert lines[4:8] == [
        "placement: doubtful here (probability on the part the file sits in, below that part's line)",
        "  based on: measured on two codebases with one reader's labels and one model version: about 7 to 10% of "
        "well-placed files read as doubtful, and about 1 in 2 to 1 in 3 doubtful files is really misplaced",
        "  app/modules/documents/adapters/export.py   adapters   0.08 (line 0.30)   2,140 chars",
        "      what to do: read it against the litmus of adapters (`xarch where "
        "app/modules/documents/adapters/export.py`). If the litmus says it belongs, leave it. In trials, about 1 in "
        "2 to 1 in 3 files read this way was really misplaced."]
    assert lines[8:] == ["", "placement: reads as placed (lowest first)",
                         "  app/modules/documents/domain/document.py   domain   0.71 (line 0.30)   1,200 chars",
                         "", "left out:", "  app/b.py: under 800 characters (612)"]
    assert "logic" not in "\n".join(lines)


def test_a_line_the_profile_sets_by_hand_is_said_beside_the_number_in_text_and_in_json():
    by_hand = replace(READ, readings=(replace(PLACED, line=0.2, by_hand=True),))
    assert ("  app/modules/documents/domain/document.py   domain   0.71 (line 0.20, set by the profile)   1,200 chars"
            in reading_lines(by_hand))
    assert json.loads(reading_document("cli", by_hand))["placement"]["files"][0]["line_by_hand"] is True


def test_a_file_asked_in_several_orders_says_its_number_is_their_mean_and_a_dry_run_says_how_many_more_it_may_ask():
    again = replace(READ, readings=(replace(PLACED, orders=3),))
    assert ("  app/modules/documents/domain/document.py   domain   0.71 (line 0.30)   1,200 chars   the mean of 3 orders "
            "of the options") in reading_lines(again)
    assert json.loads(reading_document("cli", again))["placement"]["files"][0]["orders"] == 3
    assert plan_lines(replace(PLANNED, reorders=2))[4] == (
        "A file whose answer falls within 0.15 of its part's line is asked again in 2 other order(s) of the options and "
        "read on the mean: up to 2 more request(s) for each such file.")
    assert json.loads(plan_document("cli", replace(PLANNED, reorders=2)))["reorders"] == 2


def test_a_small_file_is_marked_and_what_small_means_is_said_once():
    small = replace(READ, readings=(replace(DOUBTFUL, chars=1540, small=True), replace(PLACED, small=True)))
    lines = reading_lines(small)
    assert "  app/modules/documents/adapters/export.py   adapters   0.08 (line 0.30)   1,540 chars, small" in lines
    assert [line for line in lines if line.startswith("small:")] == [
        "small: under 2,000 characters; small files read lower for being small (in trials, a tenth of the smallest "
        "quarter of files read as doubtful, a fiftieth of the largest)"]
    assert not any(line.startswith("small:") for line in reading_lines(READ))
    assert json.loads(reading_document("cli", small))["placement"]["files"][0]["small"] is True


PARTS = (PartRead("services", 3, 0, 0.3, False, True, False), PartRead("domain", 4, 3, 0.2, True, True, True),
         PartRead("ports", 1, 1, 0.3, False, False, False))


def test_each_part_read_says_how_its_files_read_and_a_part_low_across_the_board_points_at_its_litmus_first():
    lines = reading_lines(replace(READ, parts=PARTS, left_out=()))
    at = lines.index("parts (read this run)")
    assert lines[at + 1:] == [
        "  services   3 files read   0 doubtful   line 0.30",
        "  domain   4 files read   3 doubtful   line 0.20, set by the profile",
        "      3 of its 4 files read as doubtful, more than a quarter, which usually means its litmus does not describe "
        "them: read the litmus (`xarch where` on one of its files) before the files; if the litmus and the files are "
        "right, set evals.placement.lines.domain in the profile",
        "  ports   1 file(s) read: too few to say anything of the part (fewer than 3)"]
    assert json.loads(reading_document("cli", replace(READ, parts=PARTS)))["placement"]["parts"][1] == {
        "part": "domain", "read": 4, "doubtful": 3, "line": 0.2, "line_by_hand": True, "summed": True,
        "litmus_note": True}


def test_a_reading_with_nothing_sent_says_no_more_than_where_it_read_from_and_one_with_no_doubt_says_so():
    lines = reading_lines(replace(READ, readings=(PLACED,), sent=0, left_out=(), role_only=("main",)))
    assert lines[1].endswith("Asked 0, from cache 1.") and lines[2] == ""
    assert lines[5] == "  no file judged reads as doubtful here"
    assert lines[-1] == "parts the question describes by their role only, having no litmus: main"


def test_a_reading_with_files_unanswered_says_why_each_how_the_decision_model_failed_and_what_to_do():
    unanswered = replace(READ, unasked=(Unasked("app/c.py", NOT_CACHED), Unasked("app/d.py", FAILED)),
                         failure="TypeSafe answered 401: Invalid API key")
    lines = reading_lines(unanswered)
    at = lines.index("unanswered (2): the review is incomplete (exit 3)")
    assert lines[at + 1:] == [
        "  app/c.py: not in the cache, and --offline sends nothing",
        "  app/d.py: not answered: the decision model failed, and nothing more was sent",
        "  the decision model said: TypeSafe answered 401: Invalid API key",
        "  what to do: run it again once the cache holds the answers, or without --offline with the key set; what was "
        "answered is kept and not asked again"]


def test_the_json_of_a_reading_holds_each_file_with_the_probability_of_each_part_and_what_was_sent():
    document = json.loads(reading_document("cli", replace(READ, unasked=(Unasked("app/c.py", NOT_CACHED),))))
    assert document == {
        "ok": True, "advisory": ADVISORY, "profile": "cli", "dry_run": False, "complete": False, "model": "m-1",
        "selection": {"by": ["paths"], "found": 4, "judged": 3,
                      "left_out": [{"file": "app/b.py", "why": "small", "chars": 612, "pattern": None}]},
        "placement": {"calibration": {"state": "measured", "evidence": document["placement"]["calibration"]["evidence"]},
                      "role_only": [],
                      "files": [{"file": DOUBTFUL.file, "part": "adapters", "probability": 0.0812, "line": 0.3,
                                 "line_by_hand": False, "doubtful": True, "chars": 2140, "small": False, "orders": 1, "model": "m-1.0.1",
                                 "distribution": {"adapters": 0.0812, "logic": 0.9188}},
                                {"file": PLACED.file, "part": "domain", "probability": 0.71, "line": 0.3,
                                 "line_by_hand": False, "doubtful": False, "chars": 1200, "small": False, "orders": 1, "model": "m-1.0.1",
                                 "distribution": {"domain": 0.71, "logic": 0.29}}],
                      "parts": []},
        "sends": {"name": "Model", "at": "https://model.example.test", "model": "m-1", "key": "MODEL_KEY", "keyed": True},
        "sent": {"calls": 1, "cached": 1, "input_tokens": 2400, "output_tokens": 3},
        "unanswered": [{"file": "app/c.py", "why": "not-cached"}], "failure": None}
