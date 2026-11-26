"""xarch review, shown: what a review would send, and what the decision model read of the files judged, in text for a
person or an agent and as one JSON document, and why one is refused. Every run opens with what review is: advisory,
never a check. A file is "doubtful here", which says some of its content may not fit its part, and nothing more: no
other part is named but in the JSON's distribution, the parts of its group whose probabilities its reading counts with
its own (`evals.placement.alike`), and the parts ruled out of its answer, with what the answer put on each."""
from __future__ import annotations

from typing import Any

from xarch.cli.reports.document import document
from xarch.cli.reports.eval_report import (
    ALIKE,
    REFUSED_AGAIN,
    VERDICTS,
    alike_lines,
    eval_documents,
    eval_lines,
    eval_plan_lines,
    key_now,
    masks,
    model_said,
    quoted,
    ruled_lines,
    sends_of,
    standing_document,
    standing_lines,
    unasked_why,
)
from xarch.modules.review.contract import (
    A_TEST,
    ALWAYS_MASKED,
    BAND,
    BY_ALL,
    BY_LIST,
    BY_PATHS,
    DISAGREE,
    EXCLUDED,
    FEWEST_SUMMED,
    GONE,
    IMPORTS,
    LARGE,
    LINK,
    MARKED_SMALL,
    MAX_CHARS,
    MIN_CHARS,
    MISSING,
    MOVED,
    NEVER,
    NO_CONTEXT,
    NOT_SOURCE,
    OUTSIDE,
    PIECE_CHARS,
    REFUSED,
    RULED_BY,
    SETTLED,
    SMALL,
    UNJUDGED,
    UNPARSABLE,
    UNPLACED,
    Acceptance,
    Accepted,
    LeftOut,
    PartRead,
    PiecesRead,
    Reading,
    Removed,
    Request,
    ReviewPlanned,
    ReviewReading,
    Sender,
    StaleAcceptance,
    Unasked,
)

ADVISORY = ("A decision model's reading of the code against the profile's words. Not a check and not a verdict: "
            "`xarch check` decides what is allowed.")
"""What review is, said first on every run, in text and in JSON."""
NOTHING_SENT = "Nothing was sent (--dry-run)."
BASED_ON = ("measured on two codebases with one reader's labels and one model version: about 7 to 10% of well-placed "
            "files read as doubtful, and about 1 in 2 to 1 in 3 doubtful files is really misplaced")
"""What the numbers of placement rest on, said with them in text and in JSON."""
TO_DO = ("Some of its content may not fit there, or all of it, or none: move only what does not fit, and if the litmus "
         "says it all belongs, leave it. In trials, about 1 in 2 to 1 in 3 files read this way was really misplaced.")
WAYS = {BY_PATHS: "paths", BY_LIST: "--files-from", BY_ALL: "--all"}
WHY = {MISSING: "not there", NOT_SOURCE: "no source file of the app's language", A_TEST: "a test: review reads the app's "
       "files only", OUTSIDE: "outside the app folder", EXCLUDED: "below a folder the profile excludes",
       UNPLACED: "in no part", NEVER: "held back by review.never", UNPARSABLE: "does not parse",
       SMALL: f"under {MIN_CHARS:,} characters", LARGE: f"over {MAX_CHARS:,} characters, never sent",
       LINK: "a link to a file outside the app, or to no source file"}
ACCEPTED_RECORD = ".xarch/accepted.json"
"""Where the files accepted are recorded, below the project's root, as a review names it."""
STALE = {GONE: "no longer there", SETTLED: "no longer reads as doubtful: there is nothing to accept"}
"""Why a file of the record is stale, for each reason but a move and a file not judged, which say more."""
CONTEXTS = {NO_CONTEXT: "nothing: the piece alone",
            IMPORTS: "the file's opening lines (those before its first piece), masked: numbers read so never compare "
                     "with numbers read without them"}

UNMEASURED = "a line not yet measured"
"""What is said of the yes line of the entries of a litmus list: a placeholder, which nothing measured."""

def _what_leaves(sends: Sender, pieced: bool = False) -> str:
    """What leaves the machine in a review that sends, to whom, and that the key alone allows it."""
    each = "each file and each piece of a file" if pieced else "each file"
    return (f"Without --dry-run, review sends to {sends.service} ({sends.at}), as the model {sends.model}, the masked "
            f"text of {each} below that is not in the cache and the question after it: nothing else of the project. "
            f"It sends whenever {sends.key} is set: the key alone allows it, and the key is {key_now(sends)}.")


def plan_lines(planned: ReviewPlanned) -> list[str]:
    """The header, the question every request carries, each request with the exact text it would send, then the files
    left out and why."""
    asked = len(planned.requests)
    judged = sum(not item.piece and not item.asked for item in planned.requests)
    cached = sum(item.cached for item in planned.requests)
    lines = [f"review (experimental): advisory. {ADVISORY}", NOTHING_SENT, _what_leaves(planned.sends, bool(planned.piece_ask)),
             f"{planned.found} file(s) found ({', '.join(WAYS[way] for way in planned.by)}), {judged} to be judged, "
             f"{len(planned.left_out)} left out; {asked} request(s), {planned.characters:,} characters, about "
             f"{planned.tokens:,} tokens; {cached} in the cache already.", *_reasked(planned.reorders), "",
             "the question each request carries:",
             f"  {planned.question.ask}",
             f"  options: {len(planned.question.options)} parts, each described by its litmus test"
             + (f" (by its role only: {', '.join(planned.role_only)})" if planned.role_only else "")]
    lines += [f"    {option.name}: {option.description}" for option in planned.question.options]
    if planned.litmus:
        lines += [f"the yes-or-no questions of the parts whose litmus is a list, each asked of a file of its part in the "
                  f"request of placement's question, an entry answering yes at {planned.yes_line:.2f} or above "
                  f"({UNMEASURED}):",
                  *(f"  {name} ({entry.mode}): {entry.ask}" for name, _, entry in planned.litmus)]
    if planned.piece_ask:
        lines += [f"  a request of a piece of a file asks instead: {planned.piece_ask}",
                  f"  sent before each piece: {CONTEXTS[planned.context]}"]
    lines += ["", masks(planned.mask), *alike_lines(planned.alike), *ruled_lines(),
              f"accepted: {planned.accepted} file(s) in {ACCEPTED_RECORD}"]
    lines += [f"held back by review.never: {', '.join(planned.never)}"] if planned.never else []
    lines += [f"  {pattern}: matched nothing this run (a path of review.never is read below the app, without its "
              "folder's name)" for pattern in planned.unmatched]
    for number, item in enumerate(planned.requests, 1):
        kept = ", in the cache: not sent" if item.cached else ""
        what = (f"eval {item.asked}: {item.piece or 'the file whole'} (lines {item.lines[0]}-{item.lines[1]}, "
                if item.asked and item.piece else f"eval {item.asked}: the file whole (" if item.asked
                else f"piece {item.piece} ({item.kind}, lines {item.lines[0]}-{item.lines[1]}, " if item.piece else "(")
        lines += ["", f"request {number} of {asked}: {item.file} {what}{item.part}, {item.chars:,} characters{kept})",
                  *([f"  questions: {', '.join(item.questions)}"] if len(item.questions) > 1 else []), *_quoted(item)]
    lines += eval_plan_lines(planned.evals)
    if planned.left_out:
        lines += ["", "left out:", *(f"  {item.file}: {_why(item)}" for item in planned.left_out)]
    return lines


def _reasked(reorders: int) -> list[str]:
    """What a dry run cannot count: the questions asked again of a file whose answer is near its line."""
    if not reorders:
        return []
    return [f"The request of a file whose answer is not in the cache carries the question in {reorders} other order(s) "
            f"of the options too, each a question of its own, read on the mean only when its answer falls within "
            f"{BAND:.2f} of its part's line."]


def plan_document(profile: str, planned: ReviewPlanned) -> str:
    """The JSON document of a dry run: every request in full, with the question once, since every request carries it."""
    content: dict[str, Any] = {
        "ok": True, "experimental": True, "advisory": ADVISORY, "profile": profile, "dry_run": True, "sent": False,
        "selection": {"by": list(planned.by), "found": planned.found, "judged": len(planned.requests),
                      "left_out": [_left_out(item) for item in planned.left_out]},
        "question": {"ask": planned.question.ask, "role_only": list(planned.role_only),
                     "options": [{"name": o.name, "description": o.description} for o in planned.question.options],
                     "litmus": {"yes_line": planned.yes_line, "measured": False, "questions": [
                         {"name": name, "part": part, "label": entry.label, "mode": entry.mode, "ask": entry.ask}
                         for name, part, entry in planned.litmus]} if planned.litmus else None},
        "requests": [{"file": r.file, "part": r.part, "chars": r.chars, "cached": r.cached, "text": r.text,
                      "body": r.body, "piece": r.piece or None, "kind": r.kind or None,
                      "first": r.lines[0] if r.piece else None, "last": r.lines[1] if r.piece else None,
                      "eval": r.asked or None, "questions": list(r.questions) or None}
                     for r in planned.requests],
        "evals": eval_documents(planned.evals),
        "pieces": bool(planned.piece_ask), "piece_question": planned.piece_ask or None, "context": planned.context,
        "characters": planned.characters, "tokens": planned.tokens, "reorders": planned.reorders,
        "masked": list(ALWAYS_MASKED), "mask": list(planned.mask),
        "never": [{"path": pattern, "matched": pattern not in planned.unmatched} for pattern in planned.never],
        "alike": [list(group) for group in planned.alike], "ruled_out_by": list(RULED_BY), "accepted": planned.accepted,
        "sends": sends_of(planned.sends)}
    return document(content)


def reading_lines(read: ReviewReading) -> list[str]:
    """The header, then the files doubtful here, the most doubtful first, each with what to do; the files that read as
    placed, lowest first; what small means, when a file is; how the files of each part read; the files left out and
    why; and those with no answer, and why."""
    judged = len(read.readings) + sum(not item.piece and not item.asked for item in read.unasked)
    lines = [f"review (experimental): advisory. {ADVISORY}",
             f"{model_said(read.sends.model, read.answered_by)}. {read.found} file(s) found ({', '.join(WAYS[way] for way in read.by)}), "
             f"{judged} judged, {len(read.left_out)} left out. Asked {read.sent}, from cache {read.cached}."]
    if read.sent:
        lines.append(f"Sent {read.calls} request(s) to {read.sends.service} ({read.sends.at}): "
                     f"{read.input_tokens:,} input tokens, {read.output_tokens:,} output tokens.")
    disagreeing = {part.part for part in read.calibration.parts if part.verdict == DISAGREE}
    doubtful = [item for item in read.readings if item.doubtful]
    accepted = [(item, item.accepted) for item in read.readings if item.accepted is not None]
    placed = [item for item in read.readings
              if not item.doubtful and item.accepted is None and item.part not in disagreeing]
    unlined = [item for item in read.readings
               if not item.doubtful and item.accepted is None and item.part in disagreeing]
    lines += ["", "placement: doubtful here: some of a file's content may not fit the part it sits in (probability on "
                  "that part, below its line)",
              f"  based on: {BASED_ON}"]
    for item in doubtful:
        lines += [*_reading(item), *_before(item),
                  f"      what to do: read it against the litmus of {item.part} (`xarch where {item.file}`). {TO_DO}"]
    if not read.readings and judged:
        lines.append(f"  none of the {judged} file(s) judged was answered")
    elif not doubtful:
        answered = f" ({len(read.readings)} of {judged} answered)" if len(read.readings) < judged else ""
        lines.append(f"  no file judged reads as doubtful here{answered}")
    lines.append(f"  accepted: {read.accepted} file(s) in {ACCEPTED_RECORD}, {len(accepted)} of them read as accepted "
                 "this run")
    lines += standing_lines(read.calibration)
    if accepted:
        lines += ["", "placement: accepted (doubtful here, and accepted by a person who read it; its code as it was then)",
                  *(line for item, said in accepted for line in _accepted(item, said))]
    lines += _stale(read.stale)
    if placed:
        lines += ["", "placement: reads as placed (lowest first)", *(line for item in placed for line in _reading(item))]
    for part in sorted({item.part for item in unlined}):
        lines += ["", f"placement: not read against a line: the examples of {part} disagree (lowest first)",
                  *(line for item in unlined if item.part == part for line in _reading(item))]
    for pieces in read.pieces:
        lines += ["", *_pieces(pieces)]
    if any(item.small for item in read.readings):
        lines += ["", f"small: under {MARKED_SMALL:,} characters; small files read lower for being small (in trials, a "
                      "tenth of the smallest quarter of files read as doubtful, a fiftieth of the largest)"]
    lines += eval_lines(read.evals)
    if read.parts:
        lines += ["", "parts (read this run)", *(line for part in read.parts for line in _part(part))]
    if read.role_only:
        lines += ["", f"parts the question describes by their role only, having no litmus: {', '.join(read.role_only)}"]
    if read.left_out:
        lines += ["", "left out:", *(f"  {item.file}: {_why(item)}" for item in read.left_out)]
    if read.unasked:
        lines += ["", f"unanswered ({len(read.unasked)}): the review is incomplete (exit 3)",
                  *(f"  {item.file}{_of(item)}: {unasked_why(item)}" for item in read.unasked)]
        lines += [f"  the decision model said: {read.failure}"] if read.failure else []
        lines += [f"  {REFUSED_AGAIN}"] if any(item.why == REFUSED for item in read.unasked) else []
        lines.append("  what to do: run it again once the cache holds the answers, or without --offline with the key "
                     "set; what was answered is kept and not asked again")
    return lines


def reading_document(profile: str, read: ReviewReading) -> str:
    """The JSON document of a review: every file answered with the probability of each part, the files left out and
    those with no answer, and what was sent to."""
    content: dict[str, Any] = {
        "ok": True, "experimental": True, "advisory": ADVISORY, "profile": profile, "dry_run": False, "complete": read.complete,
        "model": read.sends.model, "answered_by": list(read.answered_by),
        "selection": {"by": list(read.by), "found": read.found,
                      "judged": len(read.readings) + sum(not item.piece and not item.asked for item in read.unasked),
                      "left_out": [_left_out(item) for item in read.left_out]},
        "placement": {"calibration": {"state": "measured", "evidence": BASED_ON,
                                      "examples": standing_document(read.calibration)},
                      "role_only": list(read.role_only), "files": [_file(item) for item in read.readings],
                      "parts": [_part_read(part) for part in read.parts],
                      "accepted": {"recorded": read.accepted, "stale": [
                          {"file": item.file, "part": item.part, "why": item.why, "now": item.now or None}
                          for item in read.stale]}},
        "pieces": [_pieces_read(pieces) for pieces in read.pieces],
        "evals": eval_documents(read.evals),
        "sends": sends_of(read.sends),
        "sent": {"calls": read.calls, "answers": read.sent, "cached": read.cached, "input_tokens": read.input_tokens,
                 "output_tokens": read.output_tokens},
        "unanswered": [_unasked(item) for item in read.unasked], "failure": read.failure or None}
    return document(content)


def nothing_chosen() -> str:
    """Why a review with no file chosen is refused, naming every way to choose."""
    return ("review reads only the files it is given, and none was: name them as paths (files, or folders for the "
            "files below them), pipe a list with --files-from - (one path per line, such as the output of "
            "`git diff --name-only main`), or take every file of the app with --all")


def all_in_pieces() -> str:
    return ("--pieces ranks the pieces of files already chosen, never of every file: a sweep over pieces is noise (in "
            "trials about a third of the pieces of good files read low); name the files, or drop --pieces")


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
    return quoted(item.text)


def _why(item: LeftOut) -> str:
    if item.why in (SMALL, LARGE):
        return f"{WHY[item.why]} ({item.chars:,})"
    return f"{WHY[item.why]} ({item.pattern})" if item.pattern else WHY[item.why]


def _reading(item: Reading) -> list[str]:
    """A file's reading on a line, and under it the parts ruled out of its answer, by rule, each with the probability
    the answer put on it."""
    line = f"line {item.line:.2f}, set by the profile" if item.by_hand else f"line {item.line:.2f}"
    small = ", small" if item.small else ""
    alike = f"   summed with {', '.join(item.alike)} ({ALIKE})" if item.alike else ""
    orders = f"   the mean of {item.orders} orders of the options" if item.orders > 1 else ""
    ruled = [f"      ruled out by {rule}: "
             + ", ".join(f"{out.part} {out.probability:.2f}" for out in item.ruled_out if out.by == rule)
             for rule in dict.fromkeys(out.by for out in item.ruled_out)]
    return [f"  {item.file}   {item.part}   {item.probability:.2f} ({line})   {item.chars:,} chars{small}{alike}{orders}",
            *_litmus(item), *ruled]


def _litmus(item: Reading) -> list[str]:
    """What the entries of the litmus list of a file's part read, on a line under its reading; none for any other."""
    if item.litmus_holds is None:
        return []
    said = "holds" if item.litmus_holds else "does not hold"
    return [f"      litmus: {said} (an entry answers yes at {item.yes_line:.2f} or above, {UNMEASURED}): "
            + ", ".join(f"{entry.label} ({entry.mode}) {entry.yes:.2f} {'yes' if entry.said_yes else 'no'}"
                        for entry in item.litmus)]


def _pieces(read: PiecesRead) -> list[str]:
    """The pieces of a file, ranked inside it only, each with its lines and number, and what to do; or why they are
    not ranked."""
    small = (f"; {read.too_small} piece(s) under {PIECE_CHARS:,} characters not judged" if read.too_small else "")
    if read.judged < 2:
        return [f"pieces of {read.file}: nothing to rank ({read.judged} judged{small})"]
    if not read.answered:
        return [f"pieces of {read.file}: not ranked: some of its {read.judged} pieces judged have no answer (see "
                "unanswered)"]
    context = ("; each sent after the file's opening lines, which raises every number: never compare these with "
               "numbers read without them" if read.context == IMPORTS else "")
    alike = f"; each read on {read.part} summed with {', '.join(read.alike)} ({ALIKE})" if read.alike else ""
    lines = [f"pieces of {read.file} (ranked inside this file only: the lowest {len(read.lowest)} of {read.judged} "
             f"judged{small}{context}{alike})"]
    lines += [f"  {item.rank}. {item.name}   {item.kind}   lines {item.lines[0]}-{item.lines[1]}   "
              f"{item.probability:.2f}   {item.chars:,} chars" for item in read.lowest]
    lines.append(f"      what to do: read the first one against the litmus of {read.part} (`xarch where {read.file}`). "
                 "A low number here is a reason to look, not a finding: in good files about a third of pieces read "
                 "this low.")
    return lines


def _part(part: PartRead) -> list[str]:
    """How the files of a part read, and, when so many read as doubtful, what that usually means and what to do."""
    line = f"line {part.line:.2f}, set by the profile" if part.by_hand else f"line {part.line:.2f}"
    held = f"; placement {VERDICTS[part.held]}" if part.held in VERDICTS else ""
    line += held
    if not part.summed:
        return [f"  {part.part}   {part.read} file(s) read: too few to say anything of the part (fewer than "
                f"{FEWEST_SUMMED}){held}"]
    said = [f"  {part.part}   {part.read} files read   {part.doubtful} doubtful   {line}"]
    if part.noted:
        said.append(f"      {part.doubtful} of its {part.read} files read as doubtful, more than a quarter, which "
                    "usually means its litmus does not describe them: read the litmus (`xarch where` on one of its "
                    "files) before the files; if the litmus and the files are right, set "
                    f"evals.placement.lines.{part.part} in the profile")
    return said


def _file(item: Reading) -> dict[str, Any]:
    return {"file": item.file, "part": item.part, "probability": item.probability, "line": item.line,
            "line_by_hand": item.by_hand, "doubtful": item.doubtful, "chars": item.chars, "small": item.small,
            "orders": item.orders, "model": item.model, "alike": list(item.alike),
            "distribution": dict(item.distribution),
            "ruled_out": [{"part": out.part, "by": out.by, "probability": out.probability} for out in item.ruled_out],
            "accepted": _acceptance(item.accepted), "accepted_before": _acceptance(item.accepted_before),
            "litmus": None if item.litmus_holds is None else {
                "holds": item.litmus_holds, "yes_line": item.yes_line, "measured": False,
                "entries": [{"label": entry.label, "mode": entry.mode, "yes": entry.yes, "answered_yes": entry.said_yes}
                            for entry in item.litmus]}}


def _acceptance(said: Acceptance | None) -> dict[str, str] | None:
    return {"why": said.why, "reads_as": said.reads_as} if said is not None else None


def _before(item: Reading) -> list[str]:
    """What was said of a doubtful file accepted before its code changed."""
    if item.accepted_before is None:
        return []
    return [f"      accepted before, changed since: it read as {item.accepted_before.reads_as or 'no other part'} "
            f"then; why: {item.accepted_before.why}",
            f"      read it again: if it still belongs, accept it again (`xarch review accept {item.file} --why "
            "\"...\"`)"]


def _accepted(item: Reading, said: Acceptance) -> list[str]:
    """A file accepted, as it reads, with what was said of it."""
    return [*_reading(item), f"      accepted: it read as {said.reads_as or 'no other part'} then; why: {said.why}"]


def _stale(stale: tuple[StaleAcceptance, ...]) -> list[str]:
    """The files of the record that are stale, each with why, and the command that takes them out of it."""
    if not stale:
        return []
    return ["", f"accepted, stale ({len(stale)}): {ACCEPTED_RECORD} names them, and review never edits it",
            *(f"  {item.file} (accepted in {item.part}): {_stale_why(item)}" for item in stale),
            f"  what to do: xarch review accept --remove {' '.join(item.file for item in stale)}"]


def _stale_why(item: StaleAcceptance) -> str:
    if item.why == MOVED:
        return f"lies in {item.now} now" if item.now else "lies in no part now"
    if item.why == UNJUDGED:
        return f"not judged now ({WHY.get(item.now, item.now)})"
    return STALE[item.why]


def accepted_lines(done: Accepted, record: str) -> list[str]:
    """The files accepted, each with what it reads as, the reason, and where they are recorded."""
    return [f"review accept (experimental): {len(done.files)} file(s) accepted, nothing sent",
            *(f"  {item.file}   {item.part}   reads as {item.reads_as or 'no other part'}" for item in done.files),
            f"  why: {done.why}",
            f"recorded in {record}: commit it; a review reads each as accepted while its code is as it is now, and any "
            "change to its code brings it back as doubtful"]


def accepted_document(done: Accepted, record: str) -> str:
    return document({"ok": True, "experimental": True, "accepted": [
        {"file": item.file, "part": item.part, "reads_as": item.reads_as or None} for item in done.files],
        "why": done.why, "record": record})


def removed_lines(done: Removed, record: str) -> list[str]:
    return [f"review accept --remove (experimental): {len(done.files)} file(s) taken out of {record}",
            *(f"  {file}" for file in done.files)]


def removed_document(done: Removed, record: str) -> str:
    return document({"ok": True, "experimental": True, "removed": list(done.files), "record": record})


def no_reason() -> str:
    return ("accept needs a reason, which the record keeps: give --why \"<what you read, and why the file belongs "
            "where it is>\"")


def not_judged(files: tuple[LeftOut, ...]) -> str:
    return "; ".join(f"{item.file} is not judged by review ({_why(item)}): only a file review judges can be accepted"
                     for item in files)


def not_answered(files: tuple[str, ...]) -> str:
    return "; ".join(f"{file} has no answer in the cache, and accept sends nothing: run `xarch review {file}` first, "
                     "then accept it" for file in files)


def not_doubtful(readings: tuple[Reading, ...]) -> str:
    return "; ".join(f"{item.file} does not read as doubtful ({item.probability:.2f} on {item.part}, line "
                     f"{item.line:.2f}): there is nothing to accept" for item in readings)


def not_recorded(files: tuple[str, ...]) -> str:
    return "; ".join(f"{file} is not in {ACCEPTED_RECORD}: there is nothing to take out" for file in files)


def accept_nothing() -> str:
    return ("accept takes the files to accept, named as paths: `xarch review accept <file> --why \"...\"`, or "
            "`xarch review accept --remove <file>`")


def _pieces_read(read: PiecesRead) -> dict[str, Any]:
    return {"file": read.file, "part": read.part, "judged": read.judged, "too_small": read.too_small,
            "context": read.context, "answered": read.answered, "alike": list(read.alike),
            "lowest": [{"rank": item.rank, "kind": item.kind, "name": item.name, "first": item.lines[0],
                        "last": item.lines[1], "chars": item.chars, "probability": item.probability,
                        "distribution": dict(item.distribution)} for item in read.lowest]}


def _part_read(part: PartRead) -> dict[str, Any]:
    return {"part": part.part, "read": part.read, "doubtful": part.doubtful, "line": part.line,
            "line_by_hand": part.by_hand, "summed": part.summed, "litmus_note": part.noted,
            "examples": part.held or None}


def _left_out(item: LeftOut) -> dict[str, Any]:
    return {"file": item.file, "why": item.why, "chars": item.chars, "pattern": item.pattern or None}


def _unasked(item: Unasked) -> dict[str, Any]:
    return {"file": item.file, "why": item.why, "piece": item.piece or None, "eval": item.asked or None,
            "said": item.said or None}


def _of(item: Unasked) -> str:
    """What of a file a question with no answer is about: a piece, or what an eval reads."""
    if item.asked:
        return f" (eval {item.asked}{f': {item.piece}' if item.piece else ''})"
    return f" (piece {item.piece})" if item.piece else ""
