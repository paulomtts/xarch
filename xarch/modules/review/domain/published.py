"""The values the review module hands out as they are, which its contract re-exports: each is read outside review just
as review holds it, so there is nothing to reshape.

    Option   one option of a question with one answer out of several: its name and its description
    Choice   a question with one answer out of several options, as it is sent
    Request  what one question about one file sends: the file it is about, the part it lies in, its size and the text
             sent, masked
    LeftOut  a file found that is not judged, and why (one of the reasons below)
    Sender   what review sends to, as the decision model's adapter says it: the service, where it answers, the model
             asked, the variable its key is read from and whether the key is set
    Reading  what the decision model read of one file: the probability on the part it sits in, against that part's line
    Unasked  a file judged whose question has no answer, and why

and the reasons a file is left out, the size of the smallest file judged, how many files one run judges, the ways files
are chosen, how near its line a file is asked again, and why a question has no answer.
"""
from __future__ import annotations

from dataclasses import dataclass

MISSING, NOT_SOURCE, A_TEST, OUTSIDE, EXCLUDED, UNPLACED, NEVER, UNPARSABLE, SMALL = (
    "missing", "not-source", "test", "outside", "excluded", "unplaced", "never", "unparsable", "small")
"""Why a file found is not judged: it is not there; it is no source file of the app's language; it is a test; it lies
outside the app folder; it lies below a folder the profile excludes; it lies in no part; a path the profile says review
never sends matches it; it does not parse; it is under the smallest size judged."""

MIN_CHARS = 800
"""The fewest characters a file judged holds: under it, a file is too small to be judged (the smallest file the trials
measured held 817)."""
MAX_FILES = 50
"""How many files one run judges at most, unless told otherwise."""

BY_PATHS, BY_LIST, BY_ALL = "paths", "files-from", "all"
"""The ways files are chosen: named as paths, listed one per line, or every file of the app."""
BAND = 0.15
"""How near its part's line the first answer must put a file for it to be asked again in other orders of the options:
in the trials, reordering the options moved a file's probability by up to 0.09 in this band and almost never outside
it."""
NOT_CACHED, FAILED = "not-cached", "failed"
"""Why a question has no answer: it is not in the cache and nothing was sent (offline); or the decision model failed
on it or on a question before it, and nothing more was sent."""


@dataclass(frozen=True)
class Option:
    """One option of a question with one answer out of several: its name and its description."""
    name: str
    description: str


@dataclass(frozen=True)
class Choice:
    """A question with one answer out of several: what it asks and its options, in the order they are sent."""
    ask: str
    options: tuple[Option, ...]


@dataclass(frozen=True)
class Request:
    """What one question about one file sends: the file, as `check` shows it; the part it lies in; how many
    characters the file holds; the text sent, the file's text masked; whether its answer is in the cache already, so
    that it is not sent; and the body the service receives, as JSON text, the key left out (it travels apart)."""
    file: str
    part: str
    chars: int
    text: str
    cached: bool = False
    body: str = ""


@dataclass(frozen=True)
class Sender:
    """What review sends to, as the decision model's adapter says it: the service by name, where it answers, the
    model asked, the variable of the environment its key is read from, and whether that key is set now. Review's own
    code names no service."""
    service: str
    at: str
    model: str
    key: str
    keyed: bool


@dataclass(frozen=True)
class Reading:
    """What the decision model read of one file: the file, as `check` shows it; the part it sits in; how many
    characters it holds; the probability on that part; the line below which it is doubtful there; whether it is; the
    probability on each part, in the profile's order, the mean over the orders of the options it was asked in; the
    model version that answered first; whether the profile sets the part's line by hand; and in how many orders of the
    options it was asked."""
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


@dataclass(frozen=True)
class Unasked:
    """A file judged whose question has no answer: the file, as `check` shows it, and why (NOT_CACHED or FAILED)."""
    file: str
    why: str


@dataclass(frozen=True)
class LeftOut:
    """A file found that is not judged: the file, as `check` shows it, why (one of the reasons above), how many
    characters it holds (0 when it was not read), and, for one review never sends, the path of the profile that
    matched it ("" for any other)."""
    file: str
    why: str
    chars: int = 0
    pattern: str = ""
