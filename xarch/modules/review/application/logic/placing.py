"""Placement held to its examples: the docs' example files lying in a part (well placed by construction) and the
examples the profile writes for it, each asked placement's question once. A part passes when each clean example of its
own reads at or above its line, each flagged example lying in it reads below it, and every example of another part
reads below its line on it (a deliberate claim, read from the same answer at no extra cost). A part with no example of
its own is measured elsewhere only. A part one file cannot tell apart from others is held with the other parts of its
group as one: each reading on it is the sum over the group, and an example of another part of its group claims nothing
of it. Each example is read as a file of the app is, once the parts whose `holds` it would break are ruled out of its
answer. The examples are short snippets, and short files read lower: this is a sanity check of the litmus texts, not a
way to set lines. A record of it is stale when the question (the parts and their texts), the lines, the groups, the
examples or the rules that rule parts out of an answer change, or another model is asked."""
from __future__ import annotations

import hashlib
import json
from dataclasses import replace

from xarch.modules.review.application.logic.doubt import on_part
from xarch.modules.review.domain.published import (
    ALWAYS_MASKED,
    CALIBRATED,
    DISAGREE,
    ELSEWHERE,
    PASSED,
    RULED_BY,
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
    """The hash of what placement is held to its examples as: its question in order, each part's line, the groups of
    parts read alike (no word of them when there are none, so that a record held before a profile could write them
    stands), every example by its path, part and code, what decides how their text is masked (what review always
    masks, the import names of the apps masked, roots, and the texts mask hides), and the rules by which parts are
    ruled out of an answer (RULED_BY), so that a record held before review ruled any out is stale."""
    held = {"ask": question.ask, "options": [[o.name, o.description] for o in question.options],
            "masked": list(ALWAYS_MASKED), "roots": list(roots), "mask": list(mask), "ruled_out": list(RULED_BY),
            "lines": [[part.name, part.line] for part in parts],
            "examples": [[[e.file, e.part, e.text] for e in side] for side in examples]}
    alike = groups(parts)
    canonical = json.dumps(held | ({"alike": [list(group) for group in alike]} if alike else {}), ensure_ascii=False,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def groups(parts: tuple[PartText, ...]) -> tuple[tuple[str, ...], ...]:
    """The groups of parts read alike, each once, its parts in the profile's order, in the order of its first part."""
    found: dict[frozenset[str], tuple[str, ...]] = {}
    for part in parts:
        if part.alike:
            members = {part.name, *part.alike}
            found.setdefault(frozenset(members), tuple(item.name for item in parts if item.name in members))
    return tuple(found.values())


def verdicts(parts: tuple[PartText, ...], clean: tuple[Read, ...], flagged: tuple[Read, ...]) -> tuple[PartHeld, ...]:
    """Each part held to the examples, in the profile's order (see the module), with the other parts of its group;
    what crossed is the first example that did."""
    found: list[PartHeld] = []
    for part in parts:
        own = [read for read in clean if read[0].part == part.name]
        wrong = [read for read in flagged if read[0].part == part.name]
        if not own and not wrong:
            found.append(PartHeld(part.name, ELSEWHERE, alike=part.alike))
            continue
        group = {part.name, *part.alike}
        summed = f" summed with {', '.join(part.alike)}" if part.alike else ""
        crossed = [*(f"clean example {e.file} reads {_on(p, part):.2f}{summed}, below its line {part.line:.2f}"
                     for e, p in own if _on(p, part) < part.line),
                   *(f"flagged example {e.file} reads {_on(p, part):.2f}{summed}, not below its line {part.line:.2f}"
                     for e, p in wrong if _on(p, part) >= part.line),
                   *(f"example {e.file} of {e.part} reads {_on(p, part):.2f} on it{summed}, not below its line "
                     f"{part.line:.2f}" for e, p in clean if e.part not in group and _on(p, part) >= part.line)]
        found.append(PartHeld(part.name, DISAGREE if crossed else PASSED, crossed[0] if crossed else "",
                              len(own) + len(wrong), part.alike))
    return tuple(found)


def _on(probabilities: dict[str, float], part: PartText) -> float:
    """The probability an example's answer puts on a part, with the other parts of its group."""
    return on_part(tuple(probabilities.items()), part.name, part.alike)


def standing(record: PlacementHeld | None, held: str, model: str) -> PlacementStanding:
    """How placement stands against its record: CALIBRATED with each part as held, when the record is of what it is
    held as now and by the model asked; else UNCALIBRATED or STALE, with why."""
    if record is None:
        return PlacementStanding(UNCALIBRATED, UNHELD)
    if record.held != held:
        return PlacementStanding(STALE, "its parts, their texts, their lines, the parts read alike, its examples or "
                                        "the rules that rule parts out of an answer changed since it was held to its "
                                        "examples")
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
