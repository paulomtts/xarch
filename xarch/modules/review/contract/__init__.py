"""What the review module promises: an advisory reading of chosen files against the profile's words, by a decision
model; never a check, and never a change to what `check` finds."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.review.domain.published import (
    A_TEST,
    BAND,
    BY_ALL,
    BY_LIST,
    BY_PATHS,
    EXCLUDED,
    FAILED,
    FEWEST_SUMMED,
    IMPORTS,
    MARKED_SMALL,
    MAX_FILES,
    MAX_PIECED,
    MIN_CHARS,
    MISSING,
    NEVER,
    NO_CONTEXT,
    NOT_CACHED,
    NOT_SOURCE,
    OUTSIDE,
    PIECE_CHARS,
    SHOWN,
    SMALL,
    UNPARSABLE,
    UNPLACED,
    Choice,
    LeftOut,
    Option,
    PartRead,
    PieceReading,
    PiecesRead,
    Reading,
    Request,
    Sender,
    Unasked,
)

__all__ = ["A_TEST", "BAND", "BY_ALL", "BY_LIST", "BY_PATHS", "EXCLUDED", "FAILED", "FEWEST_SUMMED", "IMPORTS",
           "MARKED_SMALL", "MAX_FILES", "MAX_PIECED", "MIN_CHARS", "MISSING", "NEVER", "NO_CONTEXT", "NOT_CACHED",
           "NOT_SOURCE", "OUTSIDE", "PIECE_CHARS", "SHOWN", "SMALL", "UNPARSABLE", "UNPLACED", "Choice", "LeftOut",
           "Option", "PartRead", "PieceReading", "PiecesRead", "Reading", "Request", "Sender", "Unasked", "Review",
           "ReviewPlanned", "ReviewReading", "NothingChosen", "AllAndOthers", "AllInPieces", "TooManyFiles",
           "KeyMissing", "ReviewRefused", "ReviewResult"]


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
    would send to, in how many other orders of the options a file whose answer is near its line is asked again, and
    when the pieces of the files are asked of too (each request of a piece says which), what the question of a piece
    asks ("" when they are not) and what is sent before each piece."""
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


@dataclass(frozen=True)
class ReviewReading:
    """What the decision model read of the files judged: how they were chosen (BY_PATHS, BY_LIST, BY_ALL) and how
    many were found; a reading of each file answered, the most doubtful first; the files left out and why; the files
    judged with no answer, and why; what was sent to; how many questions were sent this run and how many answers were
    read from the cache; the tokens the questions sent cost; how the decision model failed, when it did ("" when it
    did not), which stopped the sending; the parts the question describes by their role alone; and how the files of
    each part read, in the profile's order; and, when pieces were asked for, the pieces of each file judged, ranked
    inside it."""
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
