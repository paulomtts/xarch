"""The evals of the profile's own, shown: how each stands in a review (it runs only once held to its examples, as it is
written now, by the model asked; else why not and what to run), its readings at or above its line with what to do, and
`xarch review calibrate`, which holds them to their examples and records the verdict, in text and as JSON."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from xarch.cli.reports.document import document
from xarch.modules.review.contract import (
    CALIBRATED,
    DISAGREE,
    ELSEWHERE,
    FAILED,
    GAP,
    NOT_CACHED,
    PLACEMENT,
    REFUSED,
    SCORE,
    YES_NO,
    Calibrated,
    CalibrationPlanned,
    EvalHeld,
    EvalRead,
    PlacementHeld,
    PlacementStanding,
    Sender,
    Unasked,
)

UNKNOWN = "how often it reads well-written code as flagged is not known"
"""What an eval's numbers rest on: its examples only, written to be clear."""
REWORD = "make it one short rule about what the text shows; add a clean example of the case it must not catch"
"""What to do about an eval whose examples failed."""
CALIBRATION = ("review calibrate (experimental): holds the evals of the profile's own to their examples, with the model review asks: "
               "an eval runs in a review only once it passed, as it is written now")
PLACEMENT_ONLY = ("review calibrate (experimental): holds placement to its examples, part by part, with the model review asks: a sanity "
                  "check of the litmus texts, which never fails the calibration")
PLACEMENT_RULE = ("placement held part by part: a part's clean examples at or above its line, every example claimed for "
                  "it from elsewhere below it; a part whose examples disagree is said, and fails nothing")
FORMS = {YES_NO: "yes or no, read as the probability of yes", SCORE: "a score of 0 to 4, read as its expected level "
         "over 4"}
CHOICE_READ = "a choice, read as the probability of the options flagged, the mean of two orders of the options"
QUOTE = "    | "
UNSEEN = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f\u2028\u2029]")
"""The characters a terminal does not show as themselves, or acts on (a line feed and a tab are shown as they are)."""
SANITY = ("the examples are short, and short files read lower for being short: a sanity check of the litmus texts, not "
          "a way to set lines")
VERDICTS = {DISAGREE: "examples disagree", ELSEWHERE: "measured elsewhere only: no example of its own"}
UNASKED = {NOT_CACHED: "not in the cache, and --offline sends nothing",
           FAILED: "not answered: the decision model failed, and nothing more was sent",
           REFUSED: "not answered: the decision model refused this request alone, and the rest was still sent"}
REFUSED_AGAIN = "a request refused alone is refused again as it is: read what the decision model said of it"
"""What to do about a request the decision model refused alone."""


def _to_run(name: str) -> str:
    """The command that holds an eval to its examples."""
    return f"xarch review calibrate --eval {name}"


def eval_lines(evals: tuple[EvalRead, ...]) -> list[str]:
    """How each eval of the profile's own went in a review: each that ran with its readings and what to do about each;
    each that did not, with why and what to run."""
    if not evals:
        return []
    lines = ["", "evals of the profile's own"]
    for item in evals:
        if item.state != CALIBRATED:
            lines.append(f"  {item.asked}   not run: {item.state}: {item.why}; run `{_to_run(item.asked)}`")
            continue
        lines.append(f"  {item.asked}   calibrated: held to {item.flagged} flagged and {item.clean} clean examples by "
                     f"{item.model}, line {item.line:.2f}; asked of {item.read}; {UNKNOWN}")
        for reading in item.readings:
            where = f"{reading.file}:{reading.line}" if reading.line else reading.file
            lines += [f"    {where} {reading.name}   {reading.value:.2f}".rstrip(), f"      {reading.message}",
                      f"      what to do: {reading.fix}. A reading is a reason to look, not a finding."]
        if not item.read:
            lines.append("    asked of nothing: no file judged holds what it reads in its scope")
        elif not item.readings:
            lines.append("    nothing it was asked of reads at or above its line")
    return lines


def eval_plan_lines(evals: tuple[EvalRead, ...]) -> list[str]:
    """How each eval of the profile's own stands in a dry run: the question of each that would run; why each other
    would not, and what to run."""
    if not evals:
        return []
    lines = ["", "evals of the profile's own"]
    for item in evals:
        if item.state != CALIBRATED:
            lines.append(f"  {item.asked}   would not run: {item.state}: {item.why}; run `{_to_run(item.asked)}`")
        else:
            lines += [f"  {item.asked}   would run (line {item.line:.2f}): {item.ask}",
                      f"    answered as {FORMS.get(item.form, CHOICE_READ)}"]
    return lines


def eval_documents(evals: tuple[EvalRead, ...]) -> list[dict[str, Any]]:
    """Each eval of the profile's own, as the JSON of a review gives it."""
    return [{"id": item.asked, "state": item.state, "why": item.why or None,
             "run": _to_run(item.asked) if item.state != CALIBRATED else None,
             "line": item.line if item.state == CALIBRATED else None, "ask": item.ask, "form": item.form,
             "examples": {"flagged": item.flagged, "clean": item.clean}, "model": item.model or None,
             "asked": item.read,
             "readings": [{"file": r.file, "line": r.line, "name": r.name or None, "value": r.value,
                           "message": r.message, "fix": r.fix} for r in item.readings]} for item in evals]


def quoted(text: str) -> list[str]:
    """A text sent, as the text output quotes it: line by line, each character a terminal would not show as itself
    written as its code (\\x1b, \\u2028), so that what is sent is what is seen."""
    seen = UNSEEN.sub(lambda found: f"\\x{ord(found.group()):02x}" if ord(found.group()) < 256
                      else f"\\u{ord(found.group()):04x}", text)
    return [f"{QUOTE}{line}".rstrip() for line in seen.split("\n")[:-1 if seen.endswith("\n") else None]]


def model_said(asked: str, answered_by: tuple[str, ...]) -> str:
    """The model asked, and the versions that answered when they are not that one alone."""
    if answered_by in ((), (asked,)):
        return f"Model {asked}"
    return f"Model {asked}, answered by {', '.join(answered_by)}"


def calibration_lines(done: Calibrated, record: str) -> list[str]:
    """Each eval held to its examples: its verdict and line, the value of each example, and what to do when it failed;
    then where the record is, and what had no answer."""
    placed = done.placement is not None or any(item.asked == PLACEMENT for item in done.unasked)
    lines = [CALIBRATION if done.held or not placed else PLACEMENT_ONLY,
             f"{model_said(done.sends.model, done.answered_by)}. Asked {done.sent}, from cache "
                          f"{done.cached}."]
    if done.sent:
        lines.append(f"Sent {done.sent} request(s) to {done.sends.service} ({done.sends.at}): "
                     f"{done.input_tokens:,} input tokens, {done.output_tokens:,} output tokens.")
    if not done.held and done.placement is None and not done.unasked:
        return [*lines, "", "nothing to calibrate: the profile writes no eval of its own and has no example"]
    if done.placement is not None:
        lines += ["", *_placement_lines(done.placement)]
    for item in done.held:
        lines += ["", *_held(item)]
    if done.record is not None:
        lines += ["", f"recorded in {record}: commit it, so that every review reads the same verdicts"]
    if done.unasked:
        lines += ["", f"unanswered ({len(done.unasked)}): the calibration is incomplete (exit 3), and an eval with an "
                      "example unanswered is not recorded", *(_unasked(item) for item in done.unasked)]
        lines += [f"  the decision model said: {done.failure}"] if done.failure else []
        lines += [f"  {REFUSED_AGAIN}"] if any(item.why == REFUSED for item in done.unasked) else []
    return lines


def _placement_lines(held: PlacementHeld) -> list[str]:
    """Placement held to its examples: each part's verdict, and what crossed where its examples disagree."""
    lines = [f"placement   held to the docs' examples and the profile's own, by {held.answered or held.model}; {SANITY}"]
    for part in held.parts:
        said = VERDICTS.get(part.verdict, f"passed ({part.examples} example(s) of its own)")
        lines.append(f"  {part.part}   {said}" + (f": {part.crossed}; read its litmus against the example, and the "
                                                    "example against the litmus" if part.crossed else ""))
    return lines


def standing_lines(stood: PlacementStanding) -> list[str]:
    """How placement stands, held to its examples, as a review says it under placement."""
    if stood.state != CALIBRATED:
        return [f"  held to its examples: no: {stood.state}: {stood.why}; run `{_to_run('placement')}`"]
    disagree = sum(part.verdict == DISAGREE for part in stood.parts)
    lines = [f"  held to its examples: yes, {disagree} of {len(stood.parts)} parts disagree; {SANITY}"]
    lines += [f"  placement of {part.part}: examples disagree ({part.crossed}): its files are read, never marked "
              "doubtful" for part in stood.parts if part.verdict == DISAGREE]
    return lines


def standing_document(stood: PlacementStanding) -> dict[str, Any]:
    """How placement stands, held to its examples, as the JSON of a review gives it."""
    return {"state": stood.state, "why": stood.why or None,
            "parts": [{"part": part.part, "verdict": part.verdict, "crossed": part.crossed or None,
                       "examples": part.examples} for part in stood.parts]}


def _held(item: EvalHeld) -> list[str]:
    if not item.complete:
        return [f"{item.asked}   not held: some of its examples have no answer (see unanswered)"]
    line = "written in the profile" if item.by_hand else "set from the examples"
    said = (f"passed: line {item.line:.2f} ({line})" if item.passed
            else f"failed: {item.crossed}: {REWORD}")
    lines = [f"{item.asked}   {said}"]
    lines += [f"  {'flagged' if example.flagged else 'clean  '}  {example.path}   {example.value:.2f}"
              for example in item.examples]
    return lines


def _unasked(item: Unasked) -> str:
    kind = f"{item.example} example " if item.example else ""
    return f"  {item.asked}: {kind}{item.file}{f' ({item.piece})' if item.piece else ''}: {unasked_why(item)}"


def unasked_why(item: Unasked) -> str:
    """Why a question has no answer, with what the decision model said of it when it refused it alone."""
    return f"{UNASKED[item.why]}: {item.said}" if item.said else UNASKED[item.why]


def calibration_document(done: Calibrated, record: str) -> str:
    """The JSON document of a calibration."""
    return document({
        "ok": True, "experimental": True, "calibrated": [{"id": item.asked, "complete": item.complete, "passed": item.passed,
                                    "line": item.line if item.complete else None, "line_by_hand": item.by_hand,
                                    "crossed": item.crossed or None,
                                    "examples": [{"path": example.path, "flagged": example.flagged,
                                                  "value": example.value} for example in item.examples]}
                                   for item in done.held],
        "placement": None if done.placement is None else {
            "model": done.placement.model, "answered_by": done.placement.answered,
            "parts": [{"part": part.part, "verdict": part.verdict, "crossed": part.crossed or None,
                       "examples": part.examples} for part in done.placement.parts]},
        "passed": done.passed, "complete": done.complete, "record": record if done.record is not None else None,
        "model": done.sends.model, "answered_by": list(done.answered_by), "sends": sends_of(done.sends),
        "sent": {"calls": done.sent, "cached": done.cached, "input_tokens": done.input_tokens,
                 "output_tokens": done.output_tokens},
        "unanswered": [{"id": item.asked, "file": item.file, "kind": item.example or None, "why": item.why,
                        "name": item.piece or None, "said": item.said or None}
                       for item in done.unasked],
        "failure": done.failure or None})


def calibration_plan_lines(planned: CalibrationPlanned) -> list[str]:
    """What a calibration would send: to whom, then each request with the exact text it would send."""
    cached = sum(item.cached for item in planned.requests)
    own = [name for name in planned.evals if name != PLACEMENT]
    rules = ([f"held to pass by every flagged example above every clean one, by {GAP} on the mean"] if own else []) + (
        [PLACEMENT_RULE] if PLACEMENT in planned.evals else [])
    lines = [CALIBRATION if own or not planned.evals else PLACEMENT_ONLY,
             "Nothing was sent (--dry-run), and nothing was recorded.",
             f"Without --dry-run, calibrate sends to {planned.sends.service} ({planned.sends.at}), as the model "
             f"{planned.sends.model}, the masked text of each thing each eval reads in its examples that is not in the "
             f"cache, and its question: nothing else of the project. It sends whenever {planned.sends.key} is set: the "
             f"key alone allows it, and the key is {key_now(planned.sends)}.",
             f"evals: {', '.join(planned.evals) or 'none'}; {len(planned.requests)} request(s), "
             f"{planned.characters:,} characters, about {planned.tokens:,} tokens; {cached} in the cache already"
             + "".join(f"; {rule}" for rule in rules)]
    for number, item in enumerate(planned.requests, 1):
        kept = ", in the cache: not sent" if item.cached else ""
        what = f" {item.piece} (lines {item.lines[0]}-{item.lines[1]})" if item.piece else ""
        lines += ["", f"request {number} of {len(planned.requests)}: {item.asked}, {item.example} example {item.file}{what}, "
                      f"{item.chars:,} characters{kept}", *quoted(item.text)]
    return lines


def calibration_plan_document(planned: CalibrationPlanned) -> str:
    """The JSON document of a calibration's dry run: every request in full."""
    return document({
        "ok": True, "experimental": True, "dry_run": True, "sent": False, "evals": list(planned.evals),
        "requests": [{"id": r.asked, "example": r.file, "kind": r.example, "part": r.part or None,
                      "name": r.piece or None, "first": r.lines[0] or None,
                      "last": r.lines[1] or None, "chars": r.chars, "cached": r.cached, "text": r.text, "body": r.body}
                     for r in planned.requests],
        "characters": planned.characters, "tokens": planned.tokens, "mask": list(planned.mask),
        "sends": sends_of(planned.sends)})


def unknown_evals(names: tuple[str, ...], known: tuple[str, ...]) -> str:
    """The refusal of a calibration asked for evals the profile does not write."""
    return (f"no eval of the profile's own named {', '.join(names)}: "
            + (f"use {', '.join(known)}" if known else "the profile writes none under evals"))


def shown_from(record: Path, cwd: Path) -> str:
    """The record's path as the command shows it: from the folder it ran in when it lies below it."""
    return record.relative_to(cwd).as_posix() if record.is_relative_to(cwd) else record.as_posix()


def key_now(sends: Sender) -> str:
    """Whether the key is set now, and when it is set but cannot be used, why; never the key."""
    if sends.unusable:
        return f"set now but cannot be used: {sends.unusable}"
    return "set now" if sends.keyed else "not set now"


def sends_of(sends: Sender) -> dict[str, Any]:
    """What a run sends to, as JSON: the service, where it answers, the model, the variable of the key, whether it
    is set, and why the key set cannot be used (null when it can, or none is set); never the key."""
    return {"name": sends.service, "at": sends.at, "model": sends.model, "key": sends.key, "keyed": sends.keyed,
            "unusable": sends.unusable or None}
