"""xarch review, shown: a dry run as text and as JSON, and every refusal in words."""
import json
from dataclasses import replace

from xarch.cli.reports.review_report import (
    ADVISORY,
    all_and_others,
    not_sendable,
    nothing_chosen,
    plan_document,
    plan_lines,
    too_many,
)
from xarch.modules.review.contract import (
    BY_LIST,
    BY_PATHS,
    MISSING,
    NEVER,
    SMALL,
    Choice,
    LeftOut,
    Option,
    Request,
    ReviewPlanned,
)

QUESTION = Choice("Which part?", (Option("domain", "Is it an invariant?"), Option("main", "starts the app")))
PLANNED = ReviewPlanned((BY_PATHS, BY_LIST), 3, (Request("app/a.py", "domain", 1200, "from <masked> import A\n\nx = 1\n"),),
                        (LeftOut("app/b.py", SMALL, 612), LeftOut("app/c.py", MISSING)), QUESTION, ("main",), 1250, 313)


def test_a_dry_run_says_first_what_review_is_that_nothing_was_sent_and_what_leaves_the_machine():
    lines = plan_lines(PLANNED)
    assert lines[0] == f"review: advisory. {ADVISORY}"
    assert lines[1] == "Nothing was sent (--dry-run)."
    assert lines[2].startswith("What leaves the machine in a review that sends: the masked text of each file below")
    assert lines[3] == ("3 file(s) found (paths, --files-from), 1 to be judged, 2 left out; 1 request(s), 1,250 "
                        "characters, about 313 tokens.")


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
        "requests": [{"file": "app/a.py", "part": "domain", "chars": 1200, "text": "from <masked> import A\n\nx = 1\n"}],
        "characters": 1250, "tokens": 313, "mask": []}


def test_a_review_with_nothing_chosen_names_every_way_to_choose():
    said = nothing_chosen()
    assert said.startswith("review reads only the files it is given, and none was")
    assert all(way in said for way in ("as paths", "--files-from -", "--all"))


def test_each_refusal_says_what_to_do():
    assert "without paths and without --files-from" in all_and_others()
    assert too_many(60, 50).startswith("60 files would be judged, more than one run judges (50): choose fewer, or raise "
                                       "--max-files")
    assert "--dry-run" in not_sendable()
