"""xarch review, shown: what a review would send, in text for a person or an agent and as one JSON document, and why
one is refused. Every run opens with what review is: advisory, never a check."""
from __future__ import annotations

from typing import Any

from xarch.cli.reports.document import document
from xarch.modules.review.contract import (
    A_TEST,
    BY_ALL,
    BY_LIST,
    BY_PATHS,
    EXCLUDED,
    MIN_CHARS,
    MISSING,
    NOT_SOURCE,
    OUTSIDE,
    SMALL,
    UNPARSABLE,
    UNPLACED,
    LeftOut,
    Request,
    ReviewPlanned,
)

ADVISORY = ("A decision model's reading of the code against the profile's words. Not a check and not a verdict: "
            "`xarch check` decides what is allowed.")
"""What review is, said first on every run, in text and in JSON."""
NOTHING_SENT = "Nothing was sent (--dry-run)."
WHAT_LEAVES = ("What leaves the machine in a review that sends: the masked text of each file below, with the question "
               "after it, and nothing else of the project. This version of review sends nothing: --dry-run is all it "
               "does.")
WAYS = {BY_PATHS: "paths", BY_LIST: "--files-from", BY_ALL: "--all"}
WHY = {MISSING: "not there", NOT_SOURCE: "no source file of the app's language", A_TEST: "a test: review reads the app's "
       "files only", OUTSIDE: "outside the app folder", EXCLUDED: "below a folder the profile excludes",
       UNPLACED: "in no part", UNPARSABLE: "does not parse", SMALL: f"under {MIN_CHARS:,} characters"}
QUOTE = "    | "


def plan_lines(planned: ReviewPlanned) -> list[str]:
    """The header, the question every request carries, each request with the exact text it would send, then the files
    left out and why."""
    judged = len(planned.requests)
    lines = [f"review: advisory. {ADVISORY}", NOTHING_SENT, WHAT_LEAVES,
             f"{planned.found} file(s) found ({', '.join(WAYS[way] for way in planned.by)}), {judged} to be judged, "
             f"{len(planned.left_out)} left out; {judged} request(s), {planned.characters:,} characters, about "
             f"{planned.tokens:,} tokens.", "", "the question each request carries:", f"  {planned.question.ask}",
             f"  options: {len(planned.question.options)} parts, each described by its litmus test"
             + (f" (by its role only: {', '.join(planned.role_only)})" if planned.role_only else "")]
    lines += [f"    {option.name}: {option.description}" for option in planned.question.options]
    for number, item in enumerate(planned.requests, 1):
        lines += ["", f"request {number} of {judged}: {item.file} ({item.part}, {item.chars:,} characters)",
                  *_quoted(item)]
    if planned.left_out:
        lines += ["", "left out:", *(f"  {item.file}: {_why(item)}" for item in planned.left_out)]
    return lines


def plan_document(profile: str, planned: ReviewPlanned) -> str:
    """The JSON document of a dry run: every request in full, with the question once, since every request carries it."""
    content: dict[str, Any] = {
        "ok": True, "advisory": ADVISORY, "profile": profile, "dry_run": True, "sent": False,
        "selection": {"by": list(planned.by), "found": planned.found, "judged": len(planned.requests),
                      "left_out": [{"file": i.file, "why": i.why, "chars": i.chars} for i in planned.left_out]},
        "question": {"ask": planned.question.ask, "role_only": list(planned.role_only),
                     "options": [{"name": o.name, "description": o.description} for o in planned.question.options]},
        "requests": [{"file": r.file, "part": r.part, "chars": r.chars, "text": r.text} for r in planned.requests],
        "characters": planned.characters, "tokens": planned.tokens}
    return document(content)


def nothing_chosen() -> str:
    """Why a review with no file chosen is refused, naming every way to choose."""
    return ("review reads only the files it is given, and none was: name them as paths (files, or folders for the "
            "files below them), pipe a list with --files-from - (one path per line, such as the output of "
            "`git diff --name-only main`), or take every file of the app with --all")


def all_and_others() -> str:
    return "--all takes every file of the app: give it without paths and without --files-from"


def too_many(chosen: int, cap: int) -> str:
    return (f"{chosen} files would be judged, more than one run judges ({cap}): choose fewer, or raise --max-files; "
            "nothing was sent")


def not_sendable() -> str:
    return "this version of review sends nothing yet: run it with --dry-run to see what it would send"


def _quoted(item: Request) -> list[str]:
    return [f"{QUOTE}{line}".rstrip() for line in item.text.splitlines()]


def _why(item: LeftOut) -> str:
    return f"{WHY[item.why]} ({item.chars:,})" if item.why == SMALL else WHY[item.why]
