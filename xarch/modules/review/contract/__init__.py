"""What the review module promises: an advisory reading of chosen files against the profile's words, by a decision
model; never a check, and never a change to what `check` finds."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.review.domain.published import (
    A_TEST,
    ALWAYS_MASKED,
    BAND,
    BY_ALL,
    BY_LIST,
    BY_PATHS,
    CALIBRATED,
    CHOOSE,
    CLEAN,
    DISAGREE,
    ELSEWHERE,
    EXCLUDED,
    FAILED,
    FAILED_EXAMPLES,
    FEWEST_EXAMPLES,
    FEWEST_SUMMED,
    FLAGGED,
    GAP,
    GONE,
    HOLDS,
    IMPORTS,
    LARGE,
    LINK,
    MARKED_SMALL,
    MAX_CHARS,
    MAX_FILES,
    MAX_PIECED,
    MIN_CHARS,
    MISSING,
    MOVED,
    NEVER,
    NO_CONTEXT,
    NOT_CACHED,
    NOT_SOURCE,
    OUTSIDE,
    PASSED,
    PIECE_CHARS,
    PLACEMENT,
    REFUSED,
    RULED_BY,
    SCORE,
    SETTLED,
    SHOWN,
    SMALL,
    STALE,
    UNCALIBRATED,
    UNHELD,
    UNJUDGED,
    UNPARSABLE,
    UNPLACED,
    YES_NO,
    Acceptance,
    Choice,
    EvalHeld,
    EvalRead,
    EvalReading,
    ExampleRead,
    HeldExample,
    LeftOut,
    LitmusRead,
    Option,
    PartHeld,
    PartRead,
    PieceReading,
    PiecesRead,
    PlacementHeld,
    PlacementStanding,
    Reading,
    Request,
    RuledOut,
    Sender,
    StaleAcceptance,
    Unasked,
)
from xarch.profile_values.litmus import Litmus

__all__ = ["A_TEST", "ALWAYS_MASKED", "BAND", "BY_ALL", "BY_LIST", "BY_PATHS", "EXCLUDED", "FAILED", "FEWEST_SUMMED", "IMPORTS",
           "LARGE", "LINK",
           "MARKED_SMALL", "MAX_CHARS", "MAX_FILES", "MAX_PIECED", "MIN_CHARS", "MISSING", "NEVER", "NO_CONTEXT", "NOT_CACHED",
           "NOT_SOURCE", "OUTSIDE", "PIECE_CHARS", "REFUSED", "SHOWN", "SMALL", "UNPARSABLE", "UNPLACED", "Choice", "LeftOut",
           "LitmusRead", "Litmus",
           "Option", "PartRead", "PieceReading", "PiecesRead", "Reading", "Request", "Sender", "Unasked", "Review",
           "ReviewPlanned", "ReviewReading", "NothingChosen", "AllAndOthers", "AllInPieces", "TooManyFiles",
           "KeyMissing", "ReviewRefused", "ReviewResult", "CALIBRATED", "CHOOSE", "FAILED_EXAMPLES", "GAP", "SCORE",
           "STALE", "UNCALIBRATED", "YES_NO", "EvalHeld", "EvalRead", "EvalReading", "ExampleRead", "Calibrate",
           "CalibrationPlanned", "Calibrated", "UnknownEvals", "CalibrateResult", "FLAGGED", "CLEAN", "PASSED", "DISAGREE",
           "ELSEWHERE", "PLACEMENT", "PartHeld", "PlacementHeld", "PlacementStanding", "UNHELD", "FEWEST_EXAMPLES",
           "HeldExample", "HOLDS", "RULED_BY", "RuledOut", "GONE", "MOVED", "SETTLED", "UNJUDGED", "Acceptance",
           "StaleAcceptance", "Accept", "FileAccepted", "Accepted", "Removed", "NoReason", "NotJudged", "NotAnswered",
           "NotDoubtful", "NotRecorded", "AcceptResult"]


@dataclass(frozen=True)
class Review:
    """Review the files at paths and at those listed (both given from cwd, from the folder holding app or from app, a
    folder standing for the files below it), or, with every, every file of the app. profile is the architecture in
    force, tests the tests root (None: none). With dry_run nothing is sent: the Result says what would be. With
    offline nothing is sent either, and only the answers kept are read. One run judges at most max_files files (None:
    MAX_FILES, or MAX_PIECED with pieces). cache is the folder the answers are kept in, given in full (None: the
    project's own). With pieces, the pieces of each file judged are ranked inside it too, context saying what is sent
    before each (NO_CONTEXT or IMPORTS)."""
    paths: tuple[Path, ...]
    listed: tuple[Path, ...]
    every: bool
    cwd: Path
    app: Path
    profile: str
    tests: Path | None = None
    dry_run: bool = False
    max_files: int | None = None
    offline: bool = False
    cache: Path | None = None
    pieces: bool = False
    context: str = NO_CONTEXT


@dataclass(frozen=True)
class ReviewPlanned:
    """What a review would send, and nothing sent: how the files were chosen (BY_PATHS, BY_LIST, BY_ALL), how many
    were found, the request each file judged would send, the files left out and why, the question each request
    carries, the parts it describes by their role alone, the characters and about how many tokens the requests
    would send in all, the texts the profile says review hides, which no request holds, what a review that sends
    would send to, in how many other orders of the options the request of a file carries the question too (read only
    when its answer is near its line; each request says the names of the questions it carries), and
    when the pieces of the files are asked of too (each request of a piece says which), what the question of a piece
    asks ("" when they are not) and what is sent before each piece; how each eval of the profile's own stands (the
    requests of each that runs say which); the paths of review.never in force, in the profile's order, and those of
    them that matched no file found this run; the groups of parts read alike, a file of each read on the sum of
    the group's probabilities, each its parts in the profile's order; how many files the record of accepted files
    names; each yes-or-no question a file of a part whose litmus is a list of two entries or more is asked in its
    request, by its name, with the part and the entry it asks; and the line at or above which an entry answers yes."""
    by: tuple[str, ...]
    found: int
    requests: tuple[Request, ...]
    left_out: tuple[LeftOut, ...]
    question: Choice
    role_only: tuple[str, ...]
    characters: int
    tokens: int
    mask: tuple[str, ...]
    sends: Sender
    reorders: int = 0
    piece_ask: str = ""
    context: str = NO_CONTEXT
    evals: tuple[EvalRead, ...] = ()
    never: tuple[str, ...] = ()
    unmatched: tuple[str, ...] = ()
    alike: tuple[tuple[str, ...], ...] = ()
    accepted: int = 0
    litmus: tuple[tuple[str, str, Litmus], ...] = ()
    yes_line: float = 0.5


@dataclass(frozen=True)
class ReviewReading:
    """What the decision model read of the files judged: how they were chosen (BY_PATHS, BY_LIST, BY_ALL) and how
    many were found; a reading of each file answered, the most doubtful first; the files left out and why; the files
    judged with no answer, and why; what was sent to; how many questions were sent this run and how many answers were
    read from the cache; the tokens the questions sent cost; how the decision model failed, when it did ("" when it
    did not), which stopped the sending; the parts the question describes by their role alone; and how the files of
    each part read, in the profile's order; and, when pieces were asked for, the pieces of each file judged, ranked
    inside it; how each eval of the profile's own went, in the profile's order: those that do not run with why,
    those that ran with their readings; how placement stands held to its examples; the model versions that gave
    the answers read, asked or kept, each once, sorted; how many files the record of accepted files names (a doubtful
    file of them whose code is as it was then reads as accepted, and is not doubtful); and the files of the record
    that are stale, judged only for the files this run found (and, with every file, for every file), by file; and how
    many requests the decision model answered, a request of placement carrying the question in each order it may be
    read in (None: one per question sent)."""
    by: tuple[str, ...]
    found: int
    readings: tuple[Reading, ...]
    left_out: tuple[LeftOut, ...]
    unasked: tuple[Unasked, ...]
    sends: Sender
    sent: int
    cached: int
    input_tokens: int
    output_tokens: int
    failure: str
    role_only: tuple[str, ...]
    parts: tuple[PartRead, ...] = ()
    pieces: tuple[PiecesRead, ...] = ()
    evals: tuple[EvalRead, ...] = ()
    calibration: PlacementStanding = PlacementStanding(UNCALIBRATED, UNHELD)
    answered_by: tuple[str, ...] = ()
    accepted: int = 0
    stale: tuple[StaleAcceptance, ...] = ()
    requests_sent: int | None = None

    @property
    def calls(self) -> int:
        """How many requests the decision model answered."""
        return self.sent if self.requests_sent is None else self.requests_sent

    @property
    def complete(self) -> bool:
        """Whether every file judged has its answer."""
        return not self.unasked


@dataclass(frozen=True)
class NothingChosen:
    """No file was chosen, and nothing was read."""


@dataclass(frozen=True)
class AllAndOthers:
    """Every file of the app was asked for with paths or a list as well, and nothing was read."""


@dataclass(frozen=True)
class AllInPieces:
    """Every file of the app was asked for in pieces, which would be noise, and nothing was read."""


@dataclass(frozen=True)
class TooManyFiles:
    """More files would be judged (chosen) than one run judges (cap), and nothing was sent."""
    chosen: int
    cap: int


@dataclass(frozen=True)
class KeyMissing:
    """A question would be sent and the key of the decision model's service is not set in variable: nothing was
    sent."""
    variable: str


@dataclass(frozen=True)
class ReviewRefused:
    """The files or the profile could not be read; reason is safe to show as it is."""
    reason: str


ReviewResult = (ReviewPlanned | ReviewReading | NothingChosen | AllAndOthers | AllInPieces | TooManyFiles | KeyMissing
                | ReviewRefused)


@dataclass(frozen=True)
class Calibrate:
    """Hold the evals of the profile's own named (every one, with none) to their examples, for the app folder app and
    the architecture in force profile, recording each in the project. With dry_run nothing is sent and nothing
    recorded: the Result says what would be sent. With offline nothing is sent either, and only the answers kept are
    read. cache is the folder the answers are kept in, given in full (None: the project's own)."""
    cwd: Path
    app: Path
    profile: str
    evals: tuple[str, ...] = ()
    dry_run: bool = False
    offline: bool = False
    cache: Path | None = None


@dataclass(frozen=True)
class CalibrationPlanned:
    """What holding the evals to their examples would send, and nothing sent: the request about each thing each eval
    reads in each example file (each says its eval, and the example by its path below the app), in each order of the
    options it is asked in; the evals it would hold, by id; the characters and about how many tokens they would send;
    the texts the profile says review hides; what it would send to; each example review.never holds back, never sent;
    the evals it leaves with too few examples to be held, each by id with the kind it is short of, nothing of
    which would be sent; and, when placement would be held, the groups of parts it would hold as one, each its parts
    in the profile's order."""
    requests: tuple[Request, ...]
    evals: tuple[str, ...]
    characters: int
    tokens: int
    mask: tuple[str, ...]
    sends: Sender
    held_back: tuple[HeldExample, ...] = ()
    too_few: tuple[tuple[str, str], ...] = ()
    alike: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class Calibrated:
    """The evals held to their examples: each, in the profile's order; the record written (None when no eval had every
    answer, and nothing was written); the questions with no answer, and why; what was sent to; how many questions were
    sent and how many answers were read from the cache; the tokens the questions sent cost; how the decision model
    failed, when it did ("" when it did not); and placement held to its examples, each part's verdict (None when it was
    not asked for, has no example, or some example has no answer); and the model versions that gave the answers read,
    asked or kept, each once, sorted; and each example review.never holds back, never sent. A part whose examples
    disagree does not fail the calibration: it is said, and review then never marks its files doubtful."""
    held: tuple[EvalHeld, ...]
    record: Path | None
    unasked: tuple[Unasked, ...]
    sends: Sender
    sent: int
    cached: int
    input_tokens: int
    output_tokens: int
    failure: str
    placement: PlacementHeld | None = None
    answered_by: tuple[str, ...] = ()
    held_back: tuple[HeldExample, ...] = ()

    @property
    def complete(self) -> bool:
        """Whether every eval, and placement, has every answer."""
        return not self.unasked

    @property
    def passed(self) -> bool:
        """Whether every eval held passed."""
        return all(item.passed for item in self.held)


@dataclass(frozen=True)
class UnknownEvals:
    """Evals were asked for by ids the profile writes no eval of its own of (names), and nothing was sent; known are
    the ids it writes."""
    names: tuple[str, ...]
    known: tuple[str, ...]


CalibrateResult = CalibrationPlanned | Calibrated | UnknownEvals | KeyMissing | ReviewRefused


@dataclass(frozen=True)
class Accept:
    """Accept the doubtful files at paths (given as a review takes them), each read from the answers kept in the cache
    (None: the project's own) and never sent, for why, a person's reason, recording each in the project; or, with
    remove, take the files at paths out of the record. app is the app folder, profile the architecture in force, tests
    the tests root (None: none)."""
    paths: tuple[Path, ...]
    cwd: Path
    app: Path
    profile: str
    why: str = ""
    remove: bool = False
    tests: Path | None = None
    cache: Path | None = None


@dataclass(frozen=True)
class FileAccepted:
    """A file accepted: the file, as review shows it; the part it lies in; and the part it reads as, the one outside
    its own part's group its answer put most on ("" for none)."""
    file: str
    part: str
    reads_as: str


@dataclass(frozen=True)
class Accepted:
    """The files accepted, in the order found, for why; and the record they were written to."""
    files: tuple[FileAccepted, ...]
    why: str
    record: Path


@dataclass(frozen=True)
class Removed:
    """The files taken out of the record of accepted files, in the order found; and the record."""
    files: tuple[str, ...]
    record: Path


@dataclass(frozen=True)
class NoReason:
    """A file was to be accepted with no reason given (none, or one of whitespace alone), and nothing was recorded."""


@dataclass(frozen=True)
class NotJudged:
    """Files were to be accepted that review does not judge, each with why it is left out, and nothing was
    recorded."""
    files: tuple[LeftOut, ...]


@dataclass(frozen=True)
class NotAnswered:
    """Files were to be accepted whose answer is not in the cache (accepting sends nothing), and nothing was
    recorded."""
    files: tuple[str, ...]


@dataclass(frozen=True)
class NotDoubtful:
    """Files were to be accepted that do not read as doubtful, each as it reads: there is nothing to accept, and
    nothing was recorded."""
    readings: tuple[Reading, ...]


@dataclass(frozen=True)
class NotRecorded:
    """Files were to be taken out of the record of accepted files that it does not name, and nothing was changed."""
    files: tuple[str, ...]


AcceptResult = (Accepted | Removed | NoReason | NotJudged | NotAnswered | NotDoubtful | NotRecorded | NothingChosen
                | TooManyFiles | ReviewRefused)
