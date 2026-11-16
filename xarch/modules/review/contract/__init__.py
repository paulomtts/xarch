"""What the review module promises: an advisory reading of chosen files against the profile's words, by a decision
model; never a check, and never a change to what `check` finds."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.modules.review.domain.published import (
    A_TEST,
    BY_ALL,
    BY_LIST,
    BY_PATHS,
    EXCLUDED,
    MAX_FILES,
    MIN_CHARS,
    MISSING,
    NEVER,
    NOT_SOURCE,
    OUTSIDE,
    SMALL,
    UNPARSABLE,
    UNPLACED,
    Choice,
    LeftOut,
    Option,
    Request,
)

__all__ = ["A_TEST", "BY_ALL", "BY_LIST", "BY_PATHS", "EXCLUDED", "MAX_FILES", "MIN_CHARS", "MISSING", "NEVER",
           "NOT_SOURCE", "OUTSIDE", "SMALL", "UNPARSABLE", "UNPLACED", "Choice", "LeftOut", "Option", "Request",
           "Review", "ReviewPlanned", "NothingChosen", "AllAndOthers", "TooManyFiles", "NotSendable",
           "ReviewRefused", "ReviewResult"]


@dataclass(frozen=True)
class Review:
    """Review the files at paths and at those listed (both given from cwd, from the folder holding app or from app, a
    folder standing for the files below it), or, with every, every file of the app. profile is the architecture in
    force, tests the tests root (None: none). With dry_run nothing is sent: the Result says what would be. One run
    judges at most max_files files."""
    paths: tuple[Path, ...]
    listed: tuple[Path, ...]
    every: bool
    cwd: Path
    app: Path
    profile: str
    tests: Path | None = None
    dry_run: bool = False
    max_files: int = MAX_FILES


@dataclass(frozen=True)
class ReviewPlanned:
    """What a review would send, and nothing sent: how the files were chosen (BY_PATHS, BY_LIST, BY_ALL), how many
    were found, the request each file judged would send, the files left out and why, the question each request
    carries, the parts it describes by their role alone, the characters and about how many tokens the requests
    would send in all, and the texts the profile says review hides, which no request holds."""
    by: tuple[str, ...]
    found: int
    requests: tuple[Request, ...]
    left_out: tuple[LeftOut, ...]
    question: Choice
    role_only: tuple[str, ...]
    characters: int
    tokens: int
    mask: tuple[str, ...] = ()


@dataclass(frozen=True)
class NothingChosen:
    """No file was chosen, and nothing was read."""


@dataclass(frozen=True)
class AllAndOthers:
    """Every file of the app was asked for with paths or a list as well, and nothing was read."""


@dataclass(frozen=True)
class TooManyFiles:
    """More files would be judged (chosen) than one run judges (cap), and nothing was sent."""
    chosen: int
    cap: int


@dataclass(frozen=True)
class NotSendable:
    """A review that would send was asked for, and there is nothing to send it with: nothing was sent."""


@dataclass(frozen=True)
class ReviewRefused:
    """The files or the profile could not be read; reason is safe to show as it is."""
    reason: str


ReviewResult = ReviewPlanned | NothingChosen | AllAndOthers | TooManyFiles | NotSendable | ReviewRefused
