"""Placement held to its examples: the docs' example files lying in a part (well placed by construction) and the
examples the profile writes for it, each asked placement's question once. A part passes when each clean example of its
own reads at or above its line, each flagged example lying in it reads below it, and every example of another part
reads below its line on it (a deliberate claim, read from the same answer at no extra cost). A part with no example of
its own is measured elsewhere only. The examples are short snippets, and short files read lower: this is a sanity
check of the litmus texts, not a way to set lines. A record of it is stale when the question (the parts and their
texts), the lines or the examples change, or another model is asked."""
from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from xarch.modules.review.domain.published import (
    ALWAYS_MASKED,
    CALIBRATED,
    DISAGREE,
    ELSEWHERE,
    PASSED,
    STALE,
    UNCALIBRATED,
    UNHELD,
    Choice,
    PartHeld,
    PartRead,
    PlacementHeld,
    PlacementStanding,
    Reading,
)
from xarch.modules.review.domain.values import CodeFile, PartText

Read = tuple[CodeFile, dict[str, float]]
"""An example placement was asked of, with the probability its answer puts on each part."""


def held_as(question: Choice, parts: tuple[PartText, ...], examples: tuple[tuple[CodeFile, ...], ...],
            roots: tuple[str, ...] = (), mask: tuple[str, ...] = ()) -> str:
    """The hash of what placement is held to its examples as: its question in order, each part's line, every example
    by its path, part and code, and what decides how their text is masked (what review always masks, the import names
    of the apps masked, roots, and the texts mask hides)."""
    canonical = json.dumps({"ask": question.ask, "options": [[o.name, o.description] for o in question.options],
                            "masked": list(ALWAYS_MASKED), "roots": list(roots), "mask": list(mask),
                            "lines": [[part.name, part.line] for part in parts],
                            "examples": [[[e.file, e.part, e.text] for e in side] for side in examples]},
                           ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verdicts(parts: tuple[PartText, ...], clean: tuple[Read, ...], flagged: tuple[Read, ...]) -> tuple[PartHeld, ...]:
    """Each part held to the examples, in the profile's order (see the module); what crossed is the first example
    that did."""
    found: list[PartHeld] = []
    for part in parts:
        own = [read for read in clean if read[0].part == part.name]
        wrong = [read for read in flagged if read[0].part == part.name]
        if not own and not wrong:
            found.append(PartHeld(part.name, ELSEWHERE))
            continue
        crossed = [*(f"clean example {e.file} reads {p.get(part.name, 0.0):.2f}, below its line {part.line:.2f}"
                     for e, p in own if p.get(part.name, 0.0) < part.line),
                   *(f"flagged example {e.file} reads {p.get(part.name, 0.0):.2f}, not below its line {part.line:.2f}"
                     for e, p in wrong if p.get(part.name, 0.0) >= part.line),
                   *(f"example {e.file} of {e.part} reads {p.get(part.name, 0.0):.2f} on it, not below its line "
                     f"{part.line:.2f}" for e, p in clean if e.part != part.name and p.get(part.name, 0.0) >= part.line)]
        found.append(PartHeld(part.name, DISAGREE if crossed else PASSED, crossed[0] if crossed else "",
                              len(own) + len(wrong)))
    return tuple(found)


def standing(record: PlacementHeld | None, held: str, model: str) -> PlacementStanding:
    """How placement stands against its record: CALIBRATED with each part as held, when the record is of what it is
    held as now and by the model asked; else UNCALIBRATED or STALE, with why."""
    if record is None:
        return PlacementStanding(UNCALIBRATED, UNHELD)
    if record.held != held:
        return PlacementStanding(STALE, "its parts, their texts, their lines or its examples changed since it was held "
                                        "to its examples")
    if record.model != model:
        return PlacementStanding(STALE, f"it was held to its examples by {record.model}, and {model} is asked now")
    return PlacementStanding(CALIBRATED, "", record.parts)


def undoubted(readings: tuple[Reading, ...], stood: PlacementStanding) -> tuple[Reading, ...]:
    """The readings, a file of a part whose examples disagree never marked doubtful."""
    disagree = {part.part for part in stood.parts if part.verdict == DISAGREE}
    return tuple(replace(item, doubtful=False) if item.part in disagree else item for item in readings)


def marked(parts: tuple[PartRead, ...], stood: PlacementStanding) -> tuple[PartRead, ...]:
    """How the files of each part read, each with how the part stood when placement was held to its examples."""
    held = {part.part: part.verdict for part in stood.parts}
    return tuple(replace(part, held=held.get(part.part, "")) for part in parts)
