"""The doubtful files a person read and found fine, accepted: an acceptance is tied to a hash of the file's code, so
that any change to the code brings the file back as doubtful, with what was said of it before. The hash is of the text
review sends for the file (masked, its comments cut), made blind to what an edit of comments alone changes there:
cutting a comment keeps its line, empty, so the lines are cut at each line feed, each loses the whitespace at its end,
a line left empty is dropped, and the rest are joined with line feeds before the SHA-256 of their UTF-8 is taken.
Docstrings are code here. A file accepted is stale in the record when, in a run that found it (or in any run that
read every file), it is gone, lies in another part, no longer reads as doubtful, or is not judged; review never edits
the record itself."""
from __future__ import annotations

import hashlib
from dataclasses import replace

from xarch.modules.review.domain.published import (
    GONE,
    MISSING,
    MOVED,
    SETTLED,
    UNJUDGED,
    UNPLACED,
    Acceptance,
    LeftOut,
    Reading,
    StaleAcceptance,
)
from xarch.modules.review.domain.values import AcceptedFile, CodeFile


def digest(text: str) -> str:
    """The hash of the text review sends for a file, blind to blank lines and to whitespace at the end of a line."""
    kept = [line.rstrip() for line in text.split("\n")]
    return hashlib.sha256("\n".join(line for line in kept if line).encode("utf-8")).hexdigest()


def reads_as(reading: Reading) -> str:
    """The part outside the group of the file's own part that its answer, once parts are ruled out, puts most on (the
    first in the profile's order on a tie; "" when there is none)."""
    out = {item.part for item in reading.ruled_out} | {reading.part, *reading.alike}
    others = [(name, probability) for name, probability in reading.distribution if name not in out]
    return max(others, key=lambda found: found[1])[0] if others else ""


def accepted(readings: tuple[Reading, ...], digests: dict[str, str],
             record: dict[str, AcceptedFile]) -> tuple[Reading, ...]:
    """The readings, each doubtful one the record names in its part marked: accepted, and no longer doubtful, when its
    code hashes as it did then (digests, by file); accepted before when it changed since."""
    found: list[Reading] = []
    for item in readings:
        entry = record.get(item.file)
        if not item.doubtful or entry is None or entry.part != item.part:
            found.append(item)
        elif entry.code == digests.get(item.file):
            found.append(replace(item, doubtful=False, accepted=Acceptance(entry.why, entry.reads_as)))
        else:
            found.append(replace(item, accepted_before=Acceptance(entry.why, entry.reads_as)))
    return tuple(found)


def stale(record: dict[str, AcceptedFile], judged: tuple[CodeFile, ...], left_out: tuple[LeftOut, ...],
          readings: tuple[Reading, ...], every: bool) -> tuple[StaleAcceptance, ...]:
    """Each file of the record that is stale, by file: one this run found, judged or left out, and with every, one it
    did not find (gone); a file judged whose question has no answer is not judged stale."""
    parts = {file.file: file.part for file in judged}
    left = {item.file: item.why for item in left_out}
    read = {item.file: item for item in readings}
    found: list[StaleAcceptance] = []
    for file, entry in sorted(record.items()):
        if file in left:
            why = left[file]
            found.append(StaleAcceptance(file, entry.part, GONE) if why == MISSING else
                         StaleAcceptance(file, entry.part, MOVED) if why == UNPLACED else
                         StaleAcceptance(file, entry.part, UNJUDGED, why))
        elif file in parts and parts[file] != entry.part:
            found.append(StaleAcceptance(file, entry.part, MOVED, parts[file]))
        elif file in read and not read[file].doubtful and read[file].accepted is None:
            found.append(StaleAcceptance(file, entry.part, SETTLED))
        elif file not in parts and every:
            found.append(StaleAcceptance(file, entry.part, GONE))
    return tuple(found)
