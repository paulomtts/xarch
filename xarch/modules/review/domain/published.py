"""The values the review module hands out as they are, which its contract re-exports: each is read outside review just
as review holds it, so there is nothing to reshape.

    Option   one option of a question with one answer out of several: its name and its description
    Choice   a question with one answer out of several options, as it is sent
    Request  what one question about one file sends: the file it is about, the part it lies in, its size and the text
             sent, masked; for a piece of a file, which (its name and kind, and the lines it spans)
    LeftOut  a file found that is not judged, and why (one of the reasons below)
    Sender   what review sends to, as the decision model's adapter says it: the service, where it answers, the model
             asked, the variable its key is read from and whether the key is set
    Reading  what the decision model read of one file: the probability on the part it sits in, against that part's line
    Unasked  a file judged whose question has no answer, and why
    PartRead how the files of one part read in a run: how many were read and how many read as doubtful
    PieceReading  what the decision model read of one piece of a file, ranked inside the file
    PiecesRead    the pieces of one file, ranked inside it: the lowest few
    EvalReading   a reading of an eval of the profile's own at or above its line, with what is said of it
    EvalRead      how an eval of the profile's own went in a run: whether it ran, and if not why, and its readings
    ExampleRead   the value an eval of the profile's own read of one of its example files
    EvalHeld      an eval of the profile's own held to its examples: the value of each, the verdict and the line

and the reasons a file is left out, the size of the smallest file judged and of the largest, how many files one run judges, the ways files
are chosen, how near its line a file is asked again, why a question has no answer, and how many files of a part a run
must read, and read as doubtful, to say anything of the part; and how pieces are cut, judged, shown and sent; what
review always masks; the
forms of a question; and the states of an eval of the profile's own, and what holds one to its examples.
"""
from __future__ import annotations

from dataclasses import dataclass

MISSING, NOT_SOURCE, A_TEST, OUTSIDE, EXCLUDED, UNPLACED, NEVER, UNPARSABLE, SMALL, LARGE, LINK = (
    "missing", "not-source", "test", "outside", "excluded", "unplaced", "never", "unparsable", "small", "large", "link")
"""Why a file found is not judged: it is not there; it is no source file of the app's language; it is a test; it lies
outside the app folder; it lies below a folder the profile excludes; it lies in no part; a path the profile says review
never sends matches it, or the file it links to; it does not parse; it is under the smallest size judged; it is over
the largest size sent; it is reached through a link to a file outside the app, or to no source file of the app's
language."""

MIN_CHARS = 800
"""The fewest characters a file judged holds: under it, a file is too small to be judged (the smallest file the trials
measured held 817)."""
MAX_CHARS = 200_000
"""The most characters a file judged holds: over it, a file is too large to be judged, and is left out and never
sent."""
MARKED_SMALL = 2000
"""The fewest characters a file judged holds not to be marked small: small files read lower for being small (in the
trials a tenth of the smallest quarter of files read as doubtful, a fiftieth of the largest)."""
MAX_FILES = 50
"""How many files one run judges at most, unless told otherwise."""
MAX_PIECED = 20
"""How many files one run judges at most when it ranks their pieces too, unless told otherwise."""
PIECE_CHARS = 1000
"""The fewest characters a piece judged holds: in the trials, half the well-placed pieces under 400 characters and over
a third of those from 400 to 1,000 read as low as misplaced ones."""
SHOWN = 3
"""How many pieces of a file are shown: the lowest, ranked."""
NO_CONTEXT, IMPORTS = "none", "imports"
"""What is sent before each piece: nothing; or the file's opening lines, those before its first piece (for most files
its docstring and imports). Numbers of the two never compare: in the trials, the context raised every one by about
0.11."""
OWN_IMPORTS, ADDRESSES, COMMENTS = "own-imports", "e-mail", "comments"
"""What review masks in every text it sends, before what the profile's review.mask hides: the dotted name each import
of the app's own code imports from, every e-mail address, and every comment, as the language's reader finds it."""
ALWAYS_MASKED = (OWN_IMPORTS, ADDRESSES, COMMENTS)
"""What review masks in every text it sends, in the order it masks them: a record of an eval or of placement held to
its examples under other masks is stale."""

BY_PATHS, BY_LIST, BY_ALL = "paths", "files-from", "all"
"""The ways files are chosen: named as paths, listed one per line, or every file of the app."""
BAND = 0.15
"""How near its part's line the first answer must put a file for it to be asked again in other orders of the options:
in the trials, reordering the options moved a file's probability by up to 0.09 in this band and almost never outside
it."""
FEWEST_SUMMED = 3
"""The fewest files of a part a run reads to say how they read: fewer say nothing of the part."""
NOT_CACHED, FAILED, REFUSED = "not-cached", "failed", "refused"
"""Why a question has no answer: it is not in the cache and nothing was sent (offline); the decision model failed
on it or on a question before it, and nothing more was sent; or the decision model refused that request alone, as its
own fault, and the rest was still sent."""


CHOOSE, YES_NO, SCORE = "choice", "yes-no", "score"
"""The forms of a question: one option out of several (placement's); yes or no; a level of a score, 0 to 4."""
CALIBRATED, UNCALIBRATED, FAILED_EXAMPLES, STALE = "calibrated", "uncalibrated", "failed", "stale"
"""The states of an eval of the profile's own: held to its examples, by the model asked, as it is written now, so that
it runs; never held to them; held to them and failed; held to them as it was written before, or by another model.
Only a calibrated eval runs."""
FLAGGED, CLEAN = "flagged", "clean"
"""The kinds of example of an eval of the profile's own: code it must read as the fault, and code it must not."""
PASSED, DISAGREE, ELSEWHERE = "passed", "disagree", "elsewhere"
"""How a part of placement stands, held to its examples: they agree with its litmus; they disagree (its files are read
but never marked doubtful); it has no example of its own, and is measured elsewhere only."""
PLACEMENT = "placement"
"""The id of placement, the eval review always asks, among the evals calibrate holds to their examples."""
UNHELD = "it was never held to its examples"
"""Why an eval, or placement, is uncalibrated."""
FEWEST_EXAMPLES = 2
"""How few flagged examples, and how few clean ones, an eval of the profile's own is held to at the least, as the
profile's format asks of `evals.<id>.examples`: one that review.never leaves with fewer is not held."""
GAP = 0.4
"""How far above the mean of an eval's clean examples the mean of its flagged ones must read for it to pass: the
weakest checks that passed the trials read +0.42 and +0.46, the one that failed +0.21."""


@dataclass(frozen=True)
class Option:
    """One option of a question with one answer out of several: its name and its description."""
    name: str
    description: str


@dataclass(frozen=True)
class Choice:
    """A question with one answer out of several: what it asks, its options, in the order they are sent, and its
    form: CHOOSE (one of the options), YES_NO (the options `yes` and `no`) or SCORE (the levels `0` to `4`)."""
    ask: str
    options: tuple[Option, ...]
    form: str = CHOOSE


@dataclass(frozen=True)
class Request:
    """What one question about one file, or one piece of it, sends: the file, as `check` shows it; the part it lies in;
    how many characters the text sent holds; the text sent, masked; whether its answer is in the cache
    already, so that it is not sent; the body the service receives, as JSON text, the key left out (it travels
    apart); and, for a piece, its name, its kind and the lines it spans ("" and (0, 0) for a whole file); and, for a
    question of an eval of the profile's own, its id ("" for placement's), the piece being what it reads (a whole file
    named ""), and, for one about an example of the eval, FLAGGED or CLEAN, the kind of example ("" for a file of the
    app)."""
    file: str
    part: str
    chars: int
    text: str
    cached: bool = False
    body: str = ""
    piece: str = ""
    kind: str = ""
    lines: tuple[int, int] = (0, 0)
    asked: str = ""
    example: str = ""


@dataclass(frozen=True)
class Sender:
    """What review sends to, as the decision model's adapter says it: the service by name, where it answers, the
    model asked, the variable of the environment its key is read from, whether that key is set now, and why the key
    set cannot be used ("" when it can, or none is set), in words that hold none of it. Review's own code names no
    service."""
    service: str
    at: str
    model: str
    key: str
    keyed: bool
    unusable: str = ""


@dataclass(frozen=True)
class Reading:
    """What the decision model read of one file: the file, as `check` shows it; the part it sits in; how many
    characters it holds; the probability on that part; the line below which it is doubtful there; whether it is; the
    probability on each part, in the profile's order, the mean over the orders of the options it was asked in; the
    model version that answered first; whether the profile sets the part's line by hand; and in how many orders of the
    options it was asked; and whether it holds fewer than MARKED_SMALL characters."""
    file: str
    part: str
    chars: int
    probability: float
    line: float
    doubtful: bool
    distribution: tuple[tuple[str, float], ...]
    model: str
    by_hand: bool = False
    orders: int = 1
    small: bool = False


@dataclass(frozen=True)
class Unasked:
    """A file judged whose question has no answer: the file, as `check` shows it, why (NOT_CACHED, FAILED or
    REFUSED), the piece of it whose question it is ("" for the whole file), the eval of the profile's own that asks it
    ("" for placement), for an example a calibration asks of, FLAGGED or CLEAN, the kind of example ("" for a file of
    the app), and, when it was REFUSED, what the decision model said of it ("" otherwise)."""
    file: str
    why: str
    piece: str = ""
    asked: str = ""
    example: str = ""
    said: str = ""


@dataclass(frozen=True)
class LeftOut:
    """A file found that is not judged: the file, as `check` shows it, why (one of the reasons above), how many
    characters it holds (0 when it was not read), and, for one review never sends, the path of the profile that
    matched it ("" for any other)."""
    file: str
    why: str
    chars: int = 0
    pattern: str = ""


@dataclass(frozen=True)
class PartRead:
    """How the files of one part read in a run: the part; how many of its files were read and how many read as
    doubtful; its line, and whether the profile sets it by hand; whether enough were read to say anything of the
    part (FEWEST_SUMMED); whether so many read as doubtful (at least logic's FEWEST_NOTED, and more than a quarter of
    those read) that its litmus may not describe them; and how the part stood when placement was held to its
    examples (PASSED, DISAGREE or ELSEWHERE; "" when placement is not calibrated)."""
    part: str
    read: int
    doubtful: int
    line: float
    by_hand: bool
    summed: bool
    noted: bool
    held: str = ""


@dataclass(frozen=True)
class PieceReading:
    """What the decision model read of one piece of a file: its rank inside the file (1 the lowest); its kind and its
    name, as the language's reader names them (Class.method for a method; the names joined for small pieces merged);
    the lines it spans; how many characters it holds; the probability on the part its file sits in; and the
    probability on each part, in the profile's order."""
    rank: int
    kind: str
    name: str
    lines: tuple[int, int]
    chars: int
    probability: float
    distribution: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class PiecesRead:
    """The pieces of one file, ranked inside it only: the file, as `check` shows it; the part it sits in; how many of
    its pieces were judged and how many were too small to be; what was sent before each (NO_CONTEXT or IMPORTS); the
    lowest SHOWN of those judged, ranked, none when fewer than two were judged (nothing to rank); and whether every
    piece judged has its answer (the ranking is given only then)."""
    file: str
    part: str
    judged: int
    too_small: int
    context: str
    lowest: tuple[PieceReading, ...]
    answered: bool = True


@dataclass(frozen=True)
class EvalReading:
    """A reading of an eval of the profile's own at or above its line: the file, as `check` shows it; the first line
    of what was read (0 for a file whole); its name (Class.method for a method, "" for a file whole); the value read;
    and the eval's message and fix, filled in."""
    file: str
    line: int
    name: str
    value: float
    message: str
    fix: str


@dataclass(frozen=True)
class EvalRead:
    """How an eval of the profile's own went in a run: its id; its state (CALIBRATED, UNCALIBRATED, FAILED_EXAMPLES or
    STALE); why it did not run, in a few words ("" when it ran); the line a reading is listed from (0 when it has
    none); how many flagged and clean examples it was held to, and by which model; how many things it was asked of;
    its readings at or above the line, the highest first; and its question and the question's form."""
    asked: str
    state: str
    why: str = ""
    line: float = 0.0
    flagged: int = 0
    clean: int = 0
    model: str = ""
    read: int = 0
    readings: tuple[EvalReading, ...] = ()
    ask: str = ""
    form: str = CHOOSE


@dataclass(frozen=True)
class ExampleRead:
    """The value an eval of the profile's own read of one of its example files: the file, by its path below the app;
    whether it is a flagged example; and its value, the highest of what the eval read in it."""
    path: str
    flagged: bool
    value: float


@dataclass(frozen=True)
class EvalHeld:
    """An eval of the profile's own held to its examples: its id; the value of each example file, flagged ones first;
    whether it passed; the line it reads from (written, else set from the examples); what crossed when it did not
    pass ("" when it passed); whether every example has its answer (none of it is recorded otherwise); whether the
    profile writes the line; and whether review.never left it with too few examples to be held (nothing of it is then
    sent, and it fails, crossed saying which kind is short)."""
    asked: str
    examples: tuple[ExampleRead, ...]
    passed: bool
    line: float
    crossed: str = ""
    complete: bool = True
    by_hand: bool = False
    too_few: bool = False


@dataclass(frozen=True)
class HeldExample:
    """An example review.never holds back, never sent: the eval it is of (placement's id for placement), its kind
    (flagged or clean), its path below the app, and the path of never that matched it."""
    asked: str
    example: str
    file: str
    pattern: str


@dataclass(frozen=True)
class PartHeld:
    """A part of placement held to its examples: the part; PASSED, DISAGREE or ELSEWHERE; what crossed when its
    examples disagree ("" else); and how many examples of its own it was held to."""
    part: str
    verdict: str
    crossed: str = ""
    examples: int = 0


@dataclass(frozen=True)
class PlacementHeld:
    """Placement held to its examples, as recorded and as a run reads it: the hash of what it was held as (the
    question, the lines and the examples); the model asked; the model version that answered; and each part, in the
    profile's order."""
    held: str
    model: str
    answered: str
    parts: tuple[PartHeld, ...]


@dataclass(frozen=True)
class PlacementStanding:
    """How placement stands in a run, held to its examples: CALIBRATED, UNCALIBRATED or STALE, why when it is not
    calibrated, and each part as it was held (none unless calibrated)."""
    state: str
    why: str = ""
    parts: tuple[PartHeld, ...] = ()
