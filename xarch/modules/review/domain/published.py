"""The values the review module hands out as they are, which its contract re-exports: each is read outside review just
as review holds it, so there is nothing to reshape.

    Option   one option of a question with one answer out of several: its name and its description
    Choice   a question with one answer out of several options, as it is sent
    Request  what one question about one file sends: the file it is about, the part it lies in, its size and the text
             sent, masked
    LeftOut  a file found that is not judged, and why (one of the reasons below)

and the reasons a file is left out, the size of the smallest file judged, how many files one run judges, and the ways files are chosen.
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
    characters the file holds; and the text sent, the file's text masked."""
    file: str
    part: str
    chars: int
    text: str


@dataclass(frozen=True)
class LeftOut:
    """A file found that is not judged: the file, as `check` shows it, why (one of the reasons above), how many
    characters it holds (0 when it was not read), and, for one review never sends, the path of the profile that
    matched it ("" for any other)."""
    file: str
    why: str
    chars: int = 0
    pattern: str = ""
