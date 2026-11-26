"""xarch review, shown: a dry run and a reading as text and as JSON, and every refusal in words."""
import json
from dataclasses import replace
from pathlib import Path

from xarch.cli.reports.review_report import (
    ADVISORY,
    accept_nothing,
    accepted_document,
    accepted_lines,
    all_and_others,
    all_in_pieces,
    no_key,
    no_reason,
    not_answered,
    not_doubtful,
    not_judged,
    not_recorded,
    nothing_chosen,
    plan_document,
    plan_lines,
    reading_document,
    reading_lines,
    removed_document,
    removed_lines,
    too_many,
)
from xarch.modules.review.contract import (
    A_TEST,
    BY_LIST,
    BY_PATHS,
    CALIBRATED,
    DISAGREE,
    FAILED,
    GONE,
    HOLDS,
    IMPORTS,
    LARGE,
    MISSING,
    MOVED,
    NEVER,
    NO_CONTEXT,
    NOT_CACHED,
    PASSED,
    REFUSED,
    SETTLED,
    SMALL,
    UNJUDGED,
    Acceptance,
    Accepted,
    Choice,
    FileAccepted,
    LeftOut,
    Litmus,
    LitmusRead,
    Option,
    PartHeld,
    PartRead,
    PieceReading,
    PiecesRead,
    PlacementStanding,
    Reading,
    Removed,
    Request,
    ReviewPlanned,
    ReviewReading,
    RuledOut,
    Sender,
    StaleAcceptance,
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
    assert lines[0] == f"review (experimental): advisory. {ADVISORY}"
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
    assert lines[10:14] == ["", "masked in each text: every comment (cut from its line, the line kept), the dotted name "
                                "each import of the app's own code imports from, and every e-mail address, always; and "
                                "what review.mask hides: nothing more",
                            "ruled out of each answer of a whole file: a part whose `holds` the file would break were "
                            "it to lie there (parts.<part>.holds): its probability dropped and what remains read as "
                            "summing to 1; never the file's own part, and never in the answer of a piece",
                            "accepted: 0 file(s) in .xarch/accepted.json"]
    assert lines[14:20] == ["", "request 1 of 1: app/a.py (domain, 1,200 characters)", "    | from <masked> import A",
                            "    |", "    | x = 1", ""]
    assert lines[20:] == ["left out:", "  app/b.py: under 800 characters (612)", "  app/c.py: not there"]


def test_a_dry_run_says_the_texts_review_mask_hides_and_each_file_review_never_sends_with_the_path_that_matched():
    held = replace(PLANNED, left_out=(LeftOut("app/k.py", NEVER, 900, "**/k.py"),), mask=("Northwind", "DOC-*"))
    lines = plan_lines(held)
    assert lines[11].endswith("and what review.mask hides: Northwind, DOC-*")
    assert lines[-2:] == ["left out:", "  app/k.py: held back by review.never (**/k.py)"]
    document = json.loads(plan_document("cli", held))
    assert (document["masked"], document["mask"]) == (["own-imports", "e-mail", "comments"], ["Northwind", "DOC-*"])
    assert document["selection"]["left_out"] == [{"file": "app/k.py", "why": "never", "chars": 900,
                                                  "pattern": "**/k.py"}]


def test_the_json_of_a_dry_run_holds_every_request_in_full_and_the_question_once():
    assert json.loads(plan_document("cli", PLANNED)) == {
        "ok": True, "experimental": True, "advisory": ADVISORY, "profile": "cli", "dry_run": True, "sent": False,
        "selection": {"by": ["paths", "files-from"], "found": 3, "judged": 1,
                      "left_out": [{"file": "app/b.py", "why": "small", "chars": 612, "pattern": None},
                                   {"file": "app/c.py", "why": "missing", "chars": 0, "pattern": None}]},
        "question": {"ask": "Which part?", "role_only": ["main"],
                     "options": [{"name": "domain", "description": "Is it an invariant?"},
                                 {"name": "main", "description": "starts the app"}], "litmus": None},
        "requests": [{"file": "app/a.py", "part": "domain", "chars": 1200, "cached": False,
                      "text": "from <masked> import A\n\nx = 1\n", "body": '{"state": "..."}', "piece": None,
                      "kind": None, "first": None, "last": None, "eval": None, "questions": None}],
        "evals": [],
        "pieces": False, "piece_question": None, "context": "none",
        "characters": 1250, "tokens": 313, "reorders": 0,
        "masked": ["own-imports", "e-mail", "comments"], "mask": [], "never": [], "alike": [], "ruled_out_by": ["holds"],
        "accepted": 0, "sends": {"name": "Model", "at": "https://model.example.test", "model": "m-1", "key": "MODEL_KEY", "keyed": False,
                  "unusable": None}}


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
    assert lines[:3] == [f"review (experimental): advisory. {ADVISORY}",
                         "Model m-1. 4 file(s) found (paths), 2 judged, 1 left out. Asked 1, from cache 1.",
                         "Sent 1 request(s) to Model (https://model.example.test): 2,400 input tokens, 3 output tokens."]
    assert lines[4:10] == [
        "placement: doubtful here: some of a file's content may not fit the part it sits in (probability on that part, "
        "below its line)",
        "  based on: measured on two codebases with one reader's labels and one model version: about 7 to 10% of "
        "well-placed files read as doubtful, and about 1 in 2 to 1 in 3 doubtful files is really misplaced",
        "  app/modules/documents/adapters/export.py   adapters   0.08 (line 0.30)   2,140 chars",
        "      what to do: read it against the litmus of adapters (`xarch where "
        "app/modules/documents/adapters/export.py`). Some of its content may not fit there, or all of it, or none: "
        "move only what does not fit, and if the litmus says it all belongs, leave it. In trials, about 1 in 2 to 1 "
        "in 3 files read this way was really misplaced.",
        "  accepted: 0 file(s) in .xarch/accepted.json, 0 of them read as accepted this run",
        "  held to its examples: no: uncalibrated: it was never held to its examples; run `xarch review calibrate "
        "--eval placement`"]
    assert lines[10:] == ["", "placement: reads as placed (lowest first)",
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
        "The request of a file whose answer is not in the cache carries the question in 2 other order(s) of the options "
        "too, each a question of its own, read on the mean only when its answer falls within 0.15 of its part's line.")
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
        "litmus_note": True, "examples": None}


def test_a_reading_with_nothing_sent_says_no_more_than_where_it_read_from_and_one_with_no_doubt_says_so():
    lines = reading_lines(replace(READ, readings=(PLACED,), sent=0, left_out=(), role_only=("main",)))
    assert lines[1].endswith("Asked 0, from cache 1.") and lines[2] == ""
    assert lines[5] == "  no file judged reads as doubtful here"
    assert lines[-1] == "parts the question describes by their role only, having no litmus: main"


def test_a_file_over_the_largest_size_sent_is_left_out_with_its_size_in_text_and_in_json():
    large = replace(READ, left_out=(LeftOut("app/huge.py", LARGE, 250_000),))
    assert reading_lines(large)[-2:] == ["left out:", "  app/huge.py: over 200,000 characters, never sent (250,000)"]
    assert json.loads(reading_document("cli", large))["selection"]["left_out"] == [
        {"file": "app/huge.py", "why": "large", "chars": 250_000, "pattern": None}]


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


def test_a_file_refused_alone_is_unanswered_with_what_the_decision_model_said_of_it_and_what_to_do():
    unanswered = replace(READ, unasked=(Unasked("app/c.py", REFUSED, said="TypeSafe answered 413: too large"),))
    lines = reading_lines(unanswered)
    at = lines.index("unanswered (1): the review is incomplete (exit 3)")
    assert lines[at + 1:at + 3] == [
        "  app/c.py: not answered: the decision model refused this request alone, and the rest was still sent: "
        "TypeSafe answered 413: too large",
        "  a request refused alone is refused again as it is: read what the decision model said of it"]
    assert json.loads(reading_document("cli", unanswered))["unanswered"] == [
        {"file": "app/c.py", "why": "refused", "piece": None, "eval": None, "said": "TypeSafe answered 413: too large"}]


def test_the_json_of_a_reading_holds_each_file_with_the_probability_of_each_part_and_what_was_sent():
    document = json.loads(reading_document("cli", replace(READ, unasked=(Unasked("app/c.py", NOT_CACHED),))))
    assert document == {
        "ok": True, "experimental": True, "advisory": ADVISORY, "profile": "cli", "dry_run": False, "complete": False, "model": "m-1",
        "answered_by": [], "selection": {"by": ["paths"], "found": 4, "judged": 3,
                      "left_out": [{"file": "app/b.py", "why": "small", "chars": 612, "pattern": None}]},
        "placement": {"calibration": {"state": "measured", "evidence": document["placement"]["calibration"]["evidence"],
                                      "examples": {"state": "uncalibrated", "why": "it was never held to its examples",
                                                   "parts": []}},
                      "role_only": [],
                      "files": [{"file": DOUBTFUL.file, "part": "adapters", "probability": 0.0812, "line": 0.3,
                                 "line_by_hand": False, "doubtful": True, "chars": 2140, "small": False, "orders": 1, "model": "m-1.0.1",
                                 "alike": [], "distribution": {"adapters": 0.0812, "logic": 0.9188}, "ruled_out": [],
                                 "accepted": None, "accepted_before": None, "litmus": None},
                                {"file": PLACED.file, "part": "domain", "probability": 0.71, "line": 0.3,
                                 "line_by_hand": False, "doubtful": False, "chars": 1200, "small": False, "orders": 1, "model": "m-1.0.1",
                                 "alike": [], "distribution": {"domain": 0.71, "logic": 0.29}, "ruled_out": [],
                                 "accepted": None, "accepted_before": None, "litmus": None}],
                      "parts": [], "accepted": {"recorded": 0, "stale": []}},
        "pieces": [],
        "evals": [],
        "sends": {"name": "Model", "at": "https://model.example.test", "model": "m-1", "key": "MODEL_KEY", "keyed": True,
                  "unusable": None},
        "sent": {"calls": 1, "answers": 1, "cached": 1, "input_tokens": 2400, "output_tokens": 3},
        "unanswered": [{"file": "app/c.py", "why": "not-cached", "piece": None, "eval": None, "said": None}],
        "failure": None}


LOWEST = (PieceReading(1, "method", "DocumentService.export_pdf", (41, 88), 1530, 0.11, (("services", 0.11),
                                                                                     ("logic", 0.89))),
          PieceReading(2, "method", "DocumentService.publish", (14, 27), 1100, 0.64, (("services", 0.64),)))
PIECES = PiecesRead("app/s.py", "services", 2, 3, NO_CONTEXT, LOWEST)


def test_the_pieces_of_a_file_are_ranked_inside_it_only_with_lines_and_numbers_and_what_to_do_naming_no_other_part():
    lines = reading_lines(replace(READ, pieces=(PIECES,), left_out=()))
    at = lines.index("pieces of app/s.py (ranked inside this file only: the lowest 2 of 2 judged; 3 piece(s) under "
                     "1,000 characters not judged)")
    assert lines[at + 1:at + 4] == [
        "  1. DocumentService.export_pdf   method   lines 41-88   0.11   1,530 chars",
        "  2. DocumentService.publish   method   lines 14-27   0.64   1,100 chars",
        "      what to do: read the first one against the litmus of services (`xarch where app/s.py`). A low number "
        "here is a reason to look, not a finding: in good files about a third of pieces read this low."]
    assert "logic" not in "\n".join(lines) and not any("doubtful" in line for line in lines[at:at + 4])


def test_pieces_read_with_context_say_their_numbers_never_compare_with_those_read_without():
    lines = reading_lines(replace(READ, pieces=(replace(PIECES, context=IMPORTS, too_small=0),)))
    assert ("pieces of app/s.py (ranked inside this file only: the lowest 2 of 2 judged; each sent after the file's "
            "opening lines, which raises every number: never compare these with numbers read without them)") in lines


def test_pieces_with_nothing_to_rank_or_with_no_answer_say_so():
    assert "pieces of app/s.py: nothing to rank (1 judged; 3 piece(s) under 1,000 characters not judged)" in (
        reading_lines(replace(READ, pieces=(replace(PIECES, judged=1, lowest=()),))))
    unanswered = replace(READ, pieces=(replace(PIECES, lowest=(), answered=False),),
                         unasked=(Unasked("app/s.py", NOT_CACHED, "DocumentService.publish"),))
    lines = reading_lines(unanswered)
    assert "pieces of app/s.py: not ranked: some of its 2 pieces judged have no answer (see unanswered)" in lines
    assert "  app/s.py (piece DocumentService.publish): not in the cache, and --offline sends nothing" in lines


def test_the_json_of_pieces_holds_each_ranked_piece_with_its_lines_and_the_probability_of_each_part():
    document = json.loads(reading_document("cli", replace(READ, pieces=(PIECES,))))
    assert document["pieces"] == [{
        "file": "app/s.py", "part": "services", "judged": 2, "too_small": 3, "context": "none", "answered": True,
        "alike": [], "lowest": [{"rank": 1, "kind": "method", "name": "DocumentService.export_pdf", "first": 41, "last": 88,
                    "chars": 1530, "probability": 0.11, "distribution": {"services": 0.11, "logic": 0.89}},
                   {"rank": 2, "kind": "method", "name": "DocumentService.publish", "first": 14, "last": 27,
                    "chars": 1100, "probability": 0.64, "distribution": {"services": 0.64}}]}]


def test_a_dry_run_with_pieces_says_the_question_of_a_piece_what_is_sent_before_it_and_each_piece_request():
    piece = Request("app/a.py", "domain", 1100, "def f():\n    pass\n", piece="f", kind="function", lines=(3, 40))
    planned = replace(PLANNED, requests=PLANNED.requests + (piece,), piece_ask="Which part? One piece.")
    lines = plan_lines(planned)
    assert lines[3].startswith("3 file(s) found (paths, --files-from), 1 to be judged, 2 left out; 2 request(s)")
    assert "  a request of a piece of a file asks instead: Which part? One piece." in lines
    assert "the masked text of each file and each piece of a file below that is not in the cache" in lines[2]
    assert "  sent before each piece: nothing: the piece alone" in lines
    assert "request 2 of 2: app/a.py piece f (function, lines 3-40, domain, 1,100 characters)" in lines
    document = json.loads(plan_document("cli", planned))
    assert (document["pieces"], document["piece_question"], document["context"]) == (True, "Which part? One piece.",
                                                                                     "none")
    assert {key: document["requests"][1][key] for key in ("piece", "kind", "first", "last")} == {
        "piece": "f", "kind": "function", "first": 3, "last": 40}


def test_every_file_in_pieces_is_refused_saying_why():
    assert all_in_pieces().startswith("--pieces ranks the pieces of files already chosen, never of every file")


def test_the_model_versions_that_answered_are_said_when_they_are_not_the_model_asked_alone():
    assert reading_lines(replace(READ, answered_by=("m-1",)))[1].startswith("Model m-1. ")
    assert reading_lines(replace(READ, answered_by=("m-0.9", "m-1")))[1].startswith("Model m-1, answered by m-0.9, m-1. ")
    assert json.loads(reading_document("cli", replace(READ, answered_by=("m-0.9",))))["answered_by"] == ["m-0.9"]


def test_a_dry_run_lists_the_paths_of_review_never_and_says_each_that_matched_nothing():
    held = replace(PLANNED, never=("app/modules/x.py", "**/k.py"), unmatched=("app/modules/x.py",))
    lines = plan_lines(held)
    at = lines.index("held back by review.never: app/modules/x.py, **/k.py")
    assert lines[at + 1] == ("  app/modules/x.py: matched nothing this run (a path of review.never is read below the "
                             "app, without its folder's name)")
    assert json.loads(plan_document("cli", held))["never"] == [{"path": "app/modules/x.py", "matched": False},
                                                               {"path": "**/k.py", "matched": True}]


def test_a_file_of_a_part_whose_examples_disagree_is_not_said_to_read_as_placed_and_the_disagreement_is_counted():
    low = replace(PLACED, probability=0.05, doubtful=False)
    stood = PlacementStanding(CALIBRATED, "", (PartHeld("domain", DISAGREE, "it crossed", 1), PartHeld("adapters", PASSED)))
    lines = reading_lines(replace(READ, readings=(DOUBTFUL, low), calibration=stood))
    assert "placement: reads as placed (lowest first)" not in lines
    at = lines.index("placement: not read against a line: the examples of domain disagree (lowest first)")
    assert lines[at + 1].startswith("  app/modules/documents/domain/document.py   domain   0.05")
    assert any(line.startswith("  held to its examples: yes, 1 of 2 parts disagree;") for line in lines)


def test_a_reading_in_which_nothing_was_answered_says_so_and_not_that_nothing_reads_as_doubtful():
    nothing = replace(READ, readings=(), unasked=(Unasked("app/a.py", NOT_CACHED), Unasked("app/c.py", NOT_CACHED)))
    assert "  none of the 2 file(s) judged was answered" in reading_lines(nothing)
    assert not any("reads as doubtful here" in line for line in reading_lines(nothing))
    some = replace(READ, readings=(PLACED,), unasked=(Unasked("app/c.py", NOT_CACHED),))
    assert "  no file judged reads as doubtful here (1 of 2 answered)" in reading_lines(some)


def test_every_text_output_of_review_and_of_calibrate_opens_as_experimental_and_every_json_document_says_so():
    from xarch.cli.reports.eval_report import (
        calibration_document,
        calibration_lines,
        calibration_plan_document,
        calibration_plan_lines,
    )
    from xarch.modules.review.contract import Calibrated, CalibrationPlanned

    done = Calibrated((), None, (), SENDS, 0, 0, 0, 0, "")
    planned = CalibrationPlanned((), ("placement",), 0, 0, (), SENDS)
    firsts = [plan_lines(PLANNED)[0], reading_lines(READ)[0], calibration_lines(done, "")[0],
              calibration_plan_lines(planned)[0]]
    assert all("(experimental)" in first for first in firsts)
    documents = [plan_document("cli", PLANNED), reading_document("cli", READ), calibration_document(done, ""),
                 calibration_plan_document(planned)]
    assert all(json.loads(text)["experimental"] is True for text in documents)


SUMMED = Reading("app/modules/documents/application/logic/titles.py", "logic", 1200, 0.62, 0.3, False,
                 (("logic", 0.22), ("kernel-logic", 0.4), ("domain", 0.38)), "m-1.0.1", alike=("kernel-logic",))


def test_a_file_of_a_part_read_alike_says_which_parts_were_counted_with_its_own_in_text_and_in_json():
    read = replace(READ, readings=(SUMMED,))
    assert ("  app/modules/documents/application/logic/titles.py   logic   0.62 (line 0.30)   1,200 chars   summed with "
            "kernel-logic (evals.placement.alike)") in reading_lines(read)
    (file,) = json.loads(reading_document("cli", read))["placement"]["files"]
    assert (file["probability"], file["alike"], file["distribution"]) == (
        0.62, ["kernel-logic"], {"logic": 0.22, "kernel-logic": 0.4, "domain": 0.38})


def test_the_pieces_of_a_file_of_a_part_read_alike_say_which_parts_were_counted_with_its_own_in_text_and_in_json():
    read = replace(READ, pieces=(replace(PIECES, alike=("logic", "kernel")),), left_out=())
    assert ("pieces of app/s.py (ranked inside this file only: the lowest 2 of 2 judged; 3 piece(s) under 1,000 "
            "characters not judged; each read on services summed with logic, kernel (evals.placement.alike))"
            in reading_lines(read))
    assert json.loads(reading_document("cli", read))["pieces"][0]["alike"] == ["logic", "kernel"]


def test_a_dry_run_says_the_groups_of_parts_read_alike_after_what_is_masked_and_nothing_of_them_when_none():
    lines = plan_lines(replace(PLANNED, alike=(("logic", "kernel-logic"),)))
    at = lines.index("read alike, each file of a part of a group read on the sum of the group's probabilities "
                     "(evals.placement.alike): logic + kernel-logic")
    assert lines[at - 1].startswith("masked in each text:")
    assert json.loads(plan_document("cli", replace(PLANNED, alike=(("logic", "kernel-logic"),))))["alike"] == [
        ["logic", "kernel-logic"]]
    assert not any(line.startswith("read alike") for line in plan_lines(PLANNED))


RULED = Reading("app/modules/documents/application/logic/checks.py", "logic", 2400, 0.42, 0.3, False,
                (("logic", 0.13), ("profile-values", 0.45), ("domain", 0.31), ("kernel-logic", 0.11)), "m-1.0.1",
                ruled_out=(RuledOut("profile-values", HOLDS, 0.45), RuledOut("domain", HOLDS, 0.31)))


def test_a_reading_with_parts_ruled_out_says_each_with_what_the_answer_put_on_it_in_text_and_in_json():
    lines = reading_lines(replace(READ, readings=(RULED,)))
    at = lines.index("  app/modules/documents/application/logic/checks.py   logic   0.42 (line 0.30)   2,400 chars")
    assert lines[at + 1] == "      ruled out by holds: profile-values 0.45, domain 0.31"
    (file,) = json.loads(reading_document("cli", replace(READ, readings=(RULED,))))["placement"]["files"]
    assert file["ruled_out"] == [{"part": "profile-values", "by": "holds", "probability": 0.45},
                                 {"part": "domain", "by": "holds", "probability": 0.31}]
    assert file["distribution"] == {"logic": 0.13, "profile-values": 0.45, "domain": 0.31, "kernel-logic": 0.11}



WHY_FINE = "it implements the port against the file system"
ACCEPTED_FILE = replace(DOUBTFUL, doubtful=False, accepted=Acceptance(WHY_FINE, "logic"))
CHANGED = replace(DOUBTFUL, accepted_before=Acceptance(WHY_FINE, "logic"))


def test_a_file_accepted_is_listed_in_its_own_section_with_its_reason_and_not_as_doubtful_in_text_and_in_json():
    read = replace(READ, readings=(ACCEPTED_FILE, PLACED), accepted=2)
    lines = reading_lines(read)
    assert "  accepted: 2 file(s) in .xarch/accepted.json, 1 of them read as accepted this run" in lines
    at = lines.index("placement: accepted (doubtful here, and accepted by a person who read it; its code as it was "
                     "then)")
    assert lines[at + 1:at + 3] == [
        "  app/modules/documents/adapters/export.py   adapters   0.08 (line 0.30)   2,140 chars",
        f"      accepted: it read as logic then; why: {WHY_FINE}"]
    assert "  no file judged reads as doubtful here" in lines
    assert lines.count("  app/modules/documents/adapters/export.py   adapters   0.08 (line 0.30)   2,140 chars") == 1
    document = json.loads(reading_document("cli", read))
    file = document["placement"]["files"][0]
    assert (file["doubtful"], file["accepted"], file["accepted_before"]) == (
        False, {"why": WHY_FINE, "reads_as": "logic"}, None)
    assert document["placement"]["accepted"] == {"recorded": 2, "stale": []}


def test_a_file_accepted_before_and_changed_since_is_doubtful_with_the_old_reason_and_what_it_read_as_then():
    lines = reading_lines(replace(READ, readings=(CHANGED,), accepted=1))
    at = lines.index("  app/modules/documents/adapters/export.py   adapters   0.08 (line 0.30)   2,140 chars")
    assert lines[at + 1:at + 3] == [
        f"      accepted before, changed since: it read as logic then; why: {WHY_FINE}",
        "      read it again: if it still belongs, accept it again (`xarch review accept "
        "app/modules/documents/adapters/export.py --why \"...\"`)"]
    file = json.loads(reading_document("cli", replace(READ, readings=(CHANGED,))))["placement"]["files"][0]
    assert (file["doubtful"], file["accepted"], file["accepted_before"]) == (
        True, None, {"why": WHY_FINE, "reads_as": "logic"})


def test_the_files_of_the_record_that_are_stale_are_listed_with_why_and_the_command_that_takes_them_out():
    stale = (StaleAcceptance("app/gone.py", "domain", GONE), StaleAcceptance("app/moved.py", "domain", MOVED, "logic"),
             StaleAcceptance("app/none.py", "domain", MOVED), StaleAcceptance("app/fine.py", "domain", SETTLED),
             StaleAcceptance("app/test.py", "domain", UNJUDGED, A_TEST))
    read = replace(READ, accepted=5, stale=stale)
    lines = reading_lines(read)
    at = lines.index("accepted, stale (5): .xarch/accepted.json names them, and review never edits it")
    assert lines[at + 1:at + 7] == [
        "  app/gone.py (accepted in domain): no longer there",
        "  app/moved.py (accepted in domain): lies in logic now",
        "  app/none.py (accepted in domain): lies in no part now",
        "  app/fine.py (accepted in domain): no longer reads as doubtful: there is nothing to accept",
        "  app/test.py (accepted in domain): not judged now (a test: review reads the app's files only)",
        "  what to do: xarch review accept --remove app/gone.py app/moved.py app/none.py app/fine.py app/test.py"]
    assert json.loads(reading_document("cli", read))["placement"]["accepted"]["stale"][:2] == [
        {"file": "app/gone.py", "part": "domain", "why": "gone", "now": None},
        {"file": "app/moved.py", "part": "domain", "why": "moved", "now": "logic"}]


def test_files_accepted_and_removed_are_said_with_the_record_in_text_and_in_json():
    done = Accepted((FileAccepted("app/x.py", "domain", "logic"),), WHY_FINE, Path("/src/.xarch/accepted.json"))
    assert accepted_lines(done, ".xarch/accepted.json") == [
        "review accept (experimental): 1 file(s) accepted, nothing sent",
        "  app/x.py   domain   reads as logic", f"  why: {WHY_FINE}",
        "recorded in .xarch/accepted.json: commit it; a review reads each as accepted while its code is as it is now, "
        "and any change to its code brings it back as doubtful"]
    assert json.loads(accepted_document(done, ".xarch/accepted.json")) == {
        "ok": True, "experimental": True, "accepted": [{"file": "app/x.py", "part": "domain", "reads_as": "logic"}],
        "why": WHY_FINE, "record": ".xarch/accepted.json"}
    gone = Removed(("app/x.py",), Path("/src/.xarch/accepted.json"))
    assert removed_lines(gone, ".xarch/accepted.json") == [
        "review accept --remove (experimental): 1 file(s) taken out of .xarch/accepted.json", "  app/x.py"]
    assert json.loads(removed_document(gone, ".xarch/accepted.json"))["removed"] == ["app/x.py"]


def test_each_refusal_of_accept_names_the_file_and_what_to_do():
    assert no_reason() == ("accept needs a reason, which the record keeps: give --why \"<what you read, and why the "
                           "file belongs where it is>\"")
    assert not_judged((LeftOut("app/b.py", SMALL, 612),)) == (
        "app/b.py is not judged by review (under 800 characters (612)): only a file review judges can be accepted")
    assert not_answered(("app/x.py",)) == ("app/x.py has no answer in the cache, and accept sends nothing: run "
                                           "`xarch review app/x.py` first, then accept it")
    assert not_doubtful((PLACED,)) == ("app/modules/documents/domain/document.py does not read as doubtful (0.71 on "
                                       "domain, line 0.30): there is nothing to accept")
    assert not_recorded(("app/x.py",)) == "app/x.py is not in .xarch/accepted.json: there is nothing to take out"
    assert accept_nothing() == ("accept takes the files to accept, named as paths: `xarch review accept <file> --why "
                                "\"...\"`, or `xarch review accept --remove <file>`")


def test_a_request_carrying_several_questions_names_them_in_a_dry_run_and_its_json():
    carrying = replace(PLANNED, requests=(replace(PLANNED.requests[0], questions=("placement", "placement.order-2")),))
    lines = plan_lines(carrying)
    at = next(i for i, line in enumerate(lines) if line.startswith("request 1 of 1:"))
    assert lines[at + 1] == "  questions: placement, placement.order-2"
    assert json.loads(plan_document("cli", carrying))["requests"][0]["questions"] == ["placement", "placement.order-2"]


def test_a_reading_says_the_requests_sent_and_the_answers_asked_apart():
    batched = replace(READ, sent=3, requests_sent=1)
    assert json.loads(reading_document("cli", batched))["sent"]["calls"] == 1
    assert json.loads(reading_document("cli", batched))["sent"]["answers"] == 3
    assert any(line.startswith("Sent 1 request(s) to") for line in reading_lines(batched))


ENTRIES = (LitmusRead("save", "any", 0.2, False), LitmusRead("session", "all", 0.9, True))


def test_a_file_of_a_part_whose_litmus_is_a_list_says_each_entry_and_whether_it_holds_against_the_unmeasured_line():
    entered = replace(READ, readings=(replace(PLACED, doubtful=True, litmus=ENTRIES, litmus_holds=False,
                                              yes_line=0.5),))
    lines = reading_lines(entered)
    at = next(i for i, line in enumerate(lines) if line.startswith(f"  {PLACED.file}"))
    assert lines[at + 1] == ("      litmus: does not hold (an entry answers yes at 0.50 or above, a line not yet "
                             "measured): save (any) 0.20 no, session (all) 0.90 yes")
    assert json.loads(reading_document("cli", entered))["placement"]["files"][0]["litmus"] == {
        "holds": False, "yes_line": 0.5, "measured": False,
        "entries": [{"label": "save", "mode": "any", "yes": 0.2, "answered_yes": False},
                    {"label": "session", "mode": "all", "yes": 0.9, "answered_yes": True}]}


def test_a_file_of_any_other_part_has_no_litmus_in_its_reading():
    assert json.loads(reading_document("cli", READ))["placement"]["files"][0]["litmus"] is None
    assert not any("litmus: " in line and "holds" in line for line in reading_lines(READ))


def test_a_dry_run_lists_the_yes_or_no_question_of_each_entry_and_its_yes_line():
    asked = replace(PLANNED, litmus=(("litmus.store.save", "store", Litmus("Does it save?", "save")),
                                     ("litmus.store.pure", "store", Litmus("Is it pure?", "pure", "all"))))
    lines = plan_lines(asked)
    at = lines.index("the yes-or-no questions of the parts whose litmus is a list, each asked of a file of its part in "
                     "the request of placement's question, an entry answering yes at 0.50 or above (a line not yet "
                     "measured):")
    assert lines[at + 1:at + 3] == ["  litmus.store.save (any): Does it save?", "  litmus.store.pure (all): Is it pure?"]
    assert json.loads(plan_document("cli", asked))["question"]["litmus"] == {
        "yes_line": 0.5, "measured": False, "questions": [
            {"name": "litmus.store.save", "part": "store", "label": "save", "mode": "any", "ask": "Does it save?"},
            {"name": "litmus.store.pure", "part": "store", "label": "pure", "mode": "all", "ask": "Is it pure?"}]}
    assert "yes-or-no questions" not in "\n".join(plan_lines(PLANNED))
