"""xarch review, shown: what a review would send, and what the decision model read of the files judged, in text for a
person or an agent and as one JSON document, and why one is refused. Every run opens with what review is: advisory,
never a check. A file is "doubtful here" and nothing more: no other part is named but in the JSON's distribution."""
from __future__ import annotations

from typing import Any

from xarch.cli.reports.document import document
from xarch.modules.review.contract import (
    A_TEST,
    BAND,
    BY_ALL,
    BY_LIST,
    BY_PATHS,
    EXCLUDED,
    FAILED,
    MIN_CHARS,
    MISSING,
    NEVER,
    NOT_CACHED,
    NOT_SOURCE,
    OUTSIDE,
    SMALL,
    UNPARSABLE,
    UNPLACED,
    LeftOut,
    Reading,
    Request,
    ReviewPlanned,
    ReviewReading,
    Sender,
    Unasked,
)

ADVISORY = ("A decision model's reading of the code against the profile's words. Not a check and not a verdict: "
            "`xarch check` decides what is allowed.")
"""What review is, said first on every run, in text and in JSON."""
NOTHING_SENT = "Nothing was sent (--dry-run)."
BASED_ON = ("measured on two codebases with one reader's labels and one model version: about 7 to 10% of well-placed "
            "files read as doubtful, and about 1 in 2 to 1 in 3 doubtful files is really misplaced")
"""What the numbers of placement rest on, said with them in text and in JSON."""
TO_DO = ("If the litmus says it belongs, leave it. In trials, about 1 in 2 to 1 in 3 files read this way was really "
         "misplaced.")
UNASKED = {NOT_CACHED: "not in the cache, and --offline sends nothing",
           FAILED: "not answered: the decision model failed, and nothing more was sent"}
WAYS = {BY_PATHS: "paths", BY_LIST: "--files-from", BY_ALL: "--all"}
WHY = {MISSING: "not there", NOT_SOURCE: "no source file of the app's language", A_TEST: "a test: review reads the app's "
       "files only", OUTSIDE: "outside the app folder", EXCLUDED: "below a folder the profile excludes",
       UNPLACED: "in no part", NEVER: "held back by review.never", UNPARSABLE: "does not parse",
       SMALL: f"under {MIN_CHARS:,} characters"}
MASKED = ("masked in each text: the dotted name each import of the app's own code imports from, and every e-mail "
          "address, always; and what review.mask hides")
QUOTE = "    | "


def _what_leaves(sends: Sender) -> str:
    """What leaves the machine in a review that sends, to whom, and that the key alone allows it."""
    now = "set" if sends.keyed else "not set"
    return (f"Without --dry-run, review sends to {sends.service} ({sends.at}), as the model {sends.model}, the masked "
            "text of each file below that is not in the cache and the question after it: nothing else of the project. "
            f"It sends whenever {sends.key} is set: the key alone allows it, and the key is {now} now.")


def plan_lines(planned: ReviewPlanned) -> list[str]:
    """The header, the question every request carries, each request with the exact text it would send, then the files
    left out and why."""
    judged = len(planned.requests)
    cached = sum(item.cached for item in planned.requests)
    lines = [f"review: advisory. {ADVISORY}", NOTHING_SENT, _what_leaves(planned.sends),
             f"{planned.found} file(s) found ({', '.join(WAYS[way] for way in planned.by)}), {judged} to be judged, "
             f"{len(planned.left_out)} left out; {judged} request(s), {planned.characters:,} characters, about "
             f"{planned.tokens:,} tokens; {cached} in the cache already.", *_reasked(planned.reorders), "",
             "the question each request carries:",
             f"  {planned.question.ask}",
             f"  options: {len(planned.question.options)} parts, each described by its litmus test"
             + (f" (by its role only: {', '.join(planned.role_only)})" if planned.role_only else "")]
    lines += [f"    {option.name}: {option.description}" for option in planned.question.options]
    lines += ["", f"{MASKED}: {', '.join(planned.mask)}" if planned.mask else f"{MASKED}: nothing more"]
    for number, item in enumerate(planned.requests, 1):
        kept = ", in the cache: not sent" if item.cached else ""
        lines += ["", f"request {number} of {judged}: {item.file} ({item.part}, {item.chars:,} characters{kept})",
                  *_quoted(item)]
    if planned.left_out:
        lines += ["", "left out:", *(f"  {item.file}: {_why(item)}" for item in planned.left_out)]
    return lines


def _reasked(reorders: int) -> list[str]:
    """What a dry run cannot count: the questions asked again of a file whose answer is near its line."""
    if not reorders:
        return []
    return [f"A file whose answer falls within {BAND:.2f} of its part's line is asked again in {reorders} other "
            f"order(s) of the options and read on the mean: up to {reorders} more request(s) for each such file."]


def plan_document(profile: str, planned: ReviewPlanned) -> str:
    """The JSON document of a dry run: every request in full, with the question once, since every request carries it."""
    content: dict[str, Any] = {
        "ok": True, "advisory": ADVISORY, "profile": profile, "dry_run": True, "sent": False,
        "selection": {"by": list(planned.by), "found": planned.found, "judged": len(planned.requests),
                      "left_out": [_left_out(item) for item in planned.left_out]},
        "question": {"ask": planned.question.ask, "role_only": list(planned.role_only),
                     "options": [{"name": o.name, "description": o.description} for o in planned.question.options]},
        "requests": [{"file": r.file, "part": r.part, "chars": r.chars, "cached": r.cached, "text": r.text,
                      "body": r.body} for r in planned.requests],
        "characters": planned.characters, "tokens": planned.tokens, "reorders": planned.reorders,
        "mask": list(planned.mask),
        "sends": _sends(planned.sends)}
    return document(content)


def reading_lines(read: ReviewReading) -> list[str]:
    """The header, then the files doubtful here, the most doubtful first, each with what to do; the files that read as
    placed, lowest first; the files left out and why; and those with no answer, and why."""
    judged = len(read.readings) + len(read.unasked)
    lines = [f"review: advisory. {ADVISORY}",
             f"Model {read.sends.model}. {read.found} file(s) found ({', '.join(WAYS[way] for way in read.by)}), "
             f"{judged} judged, {len(read.left_out)} left out. Asked {read.sent}, from cache {read.cached}."]
    if read.sent:
        lines.append(f"Sent {read.sent} request(s) to {read.sends.service} ({read.sends.at}): "
                     f"{read.input_tokens:,} input tokens, {read.output_tokens:,} output tokens.")
    doubtful = [item for item in read.readings if item.doubtful]
    placed = [item for item in read.readings if not item.doubtful]
    lines += ["", "placement: doubtful here (probability on the part the file sits in, below that part's line)",
              f"  based on: {BASED_ON}"]
    for item in doubtful:
        lines += [_reading(item),
                  f"      what to do: read it against the litmus of {item.part} (`xarch where {item.file}`). {TO_DO}"]
    if not doubtful:
        lines.append("  no file judged reads as doubtful here")
    if placed:
        lines += ["", "placement: reads as placed (lowest first)", *(_reading(item) for item in placed)]
    if read.role_only:
        lines += ["", f"parts the question describes by their role only, having no litmus: {', '.join(read.role_only)}"]
    if read.left_out:
        lines += ["", "left out:", *(f"  {item.file}: {_why(item)}" for item in read.left_out)]
    if read.unasked:
        lines += ["", f"unanswered ({len(read.unasked)}): the review is incomplete (exit 3)",
                  *(f"  {item.file}: {UNASKED[item.why]}" for item in read.unasked)]
        lines += [f"  the decision model said: {read.failure}"] if read.failure else []
        lines.append("  what to do: run it again once the cache holds the answers, or without --offline with the key "
                     "set; what was answered is kept and not asked again")
    return lines


def reading_document(profile: str, read: ReviewReading) -> str:
    """The JSON document of a review: every file answered with the probability of each part, the files left out and
    those with no answer, and what was sent to."""
    content: dict[str, Any] = {
        "ok": True, "advisory": ADVISORY, "profile": profile, "dry_run": False, "complete": read.complete,
        "model": read.sends.model,
        "selection": {"by": list(read.by), "found": read.found, "judged": len(read.readings) + len(read.unasked),
                      "left_out": [_left_out(item) for item in read.left_out]},
        "placement": {"calibration": {"state": "measured", "evidence": BASED_ON},
                      "role_only": list(read.role_only), "files": [_file(item) for item in read.readings]},
        "sends": _sends(read.sends),
        "sent": {"calls": read.sent, "cached": read.cached, "input_tokens": read.input_tokens,
                 "output_tokens": read.output_tokens},
        "unanswered": [_unasked(item) for item in read.unasked], "failure": read.failure or None}
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


def no_key(variable: str) -> str:
    """Why a review that would send is refused when the key is not set, and what to run instead."""
    return (f"no key: set {variable}, or run --dry-run to see what would be sent, or --offline to use cached answers "
            "only")


def _quoted(item: Request) -> list[str]:
    return [f"{QUOTE}{line}".rstrip() for line in item.text.splitlines()]


def _why(item: LeftOut) -> str:
    if item.why == SMALL:
        return f"{WHY[item.why]} ({item.chars:,})"
    return f"{WHY[item.why]} ({item.pattern})" if item.pattern else WHY[item.why]


def _reading(item: Reading) -> str:
    line = f"line {item.line:.2f}, set by the profile" if item.by_hand else f"line {item.line:.2f}"
    orders = f"   the mean of {item.orders} orders of the options" if item.orders > 1 else ""
    return f"  {item.file}   {item.part}   {item.probability:.2f} ({line})   {item.chars:,} chars{orders}"


def _file(item: Reading) -> dict[str, Any]:
    return {"file": item.file, "part": item.part, "probability": item.probability, "line": item.line,
            "line_by_hand": item.by_hand, "doubtful": item.doubtful, "chars": item.chars, "orders": item.orders, "model": item.model,
            "distribution": dict(item.distribution)}


def _left_out(item: LeftOut) -> dict[str, Any]:
    return {"file": item.file, "why": item.why, "chars": item.chars, "pattern": item.pattern or None}


def _unasked(item: Unasked) -> dict[str, Any]:
    return {"file": item.file, "why": item.why}


def _sends(sends: Sender) -> dict[str, Any]:
    return {"name": sends.service, "at": sends.at, "model": sends.model, "key": sends.key, "keyed": sends.keyed}
