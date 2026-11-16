"""Where a path sits among named path patterns, and which places a rule's target reaches.

A pattern is a path whose one `*` step stands for any name: an instance's of the repeating folder it sits in. A path
sits in the pattern it lies in, the deepest when patterns nest, with `*` capturing the name; what lies below the
pattern is the place's sub-path. A path is compared as its language names it (see Marks): no ending on its file, and
the file that stands for a folder is the folder itself.

A target names a part, a scope, an optional path below the part and an optional name pattern. Scope "own" reaches the
part in the importer's instance, "any" in any instance, "none" a part outside the instances. EVERYTHING reaches every
place, including the places no part claims. A target with a name pattern reaches only a name imported from the place
that the pattern matches (`*` stands for any text, the rest is matched as written), never the place as a whole.

A part may always import itself: its own instance for a part inside a repeating folder, the part for one outside. A rule
never says so; `with_itself` adds it to the row of the part.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from xarch.kernel.placement import EACH, EVERYTHING, Marks, Place, Repeat, Target


@dataclass(frozen=True)
class Excluded:
    """A folder below the app that is not its source, and why: no check reads it.

    path: below the app folder, e.g. ("architectures", "examples")
    reason: one line, shown in the enforcement section
    """
    path: tuple[str, ...]
    reason: str


def root_of(pattern: tuple[str, ...]) -> tuple[str, ...] | None:
    """The folder the pattern's repeating step sits in; None when the pattern has none."""
    return pattern[:pattern.index(EACH)] if EACH in pattern else None


def repeat_of(repeats: Iterable[Repeat], pattern: tuple[str, ...]) -> Repeat | None:
    """The repeating folder a pattern lies in."""
    root = root_of(pattern)
    return next((repeat for repeat in repeats if repeat.root == root), None) if root is not None else None


def module_steps(path: tuple[str, ...], marks: Marks) -> tuple[str, ...]:
    """A path as the language names it: no ending on its file, and the file that stands for its folder is the folder."""
    if path and path[-1].endswith(marks.extension):
        path = path[:-1] + (path[-1].removesuffix(marks.extension),)
    stem = marks.package_file.removesuffix(marks.extension)
    return path[:-1] if path and stem and path[-1] == stem else path


def place_of(patterns: Mapping[str, tuple[str, ...]], path: tuple[str, ...], marks: Marks) -> Place:
    """The place of a path among patterns, by name; Place(None) when no pattern claims it."""
    steps = module_steps(path, marks)
    best = Place(None)
    depth = -1
    for name, raw in patterns.items():
        pattern = module_steps(raw, marks)
        if len(steps) < len(pattern) or len(pattern) <= depth:
            continue
        instance = None
        for want, step in zip(pattern, steps):
            if want == EACH and step != EACH:
                instance = step
            elif want != step or step == EACH:
                break
        else:
            best, depth = Place(name, instance, steps[len(pattern):]), len(pattern)
    return best


def name_matches(pattern: str, name: str) -> bool:
    """Whether a name matches a pattern in which `*` stands for any text and every other character for itself."""
    return re.fullmatch(".*".join(re.escape(piece) for piece in pattern.split("*")), name) is not None


def reaches(target: Target, source: Place, place: Place, name: str | None = None) -> bool:
    """Whether target, in the rules of the part at source, allows importing what sits at place: the name imported
    from it, None when the place is imported as a whole, which a target with a name pattern never allows."""
    if target.part == EVERYTHING:
        return True
    if place.part is None or target.part != place.part or place.sub[:len(target.sub)] != target.sub:
        return False
    if target.names and (name is None or not name_matches(target.names, name)):
        return False
    match target.scope:
        case "own":
            return source.instance is not None and source.instance == place.instance
        case "any":
            return place.instance is not None
        case _:
            return place.instance is None


def with_itself(name: str, pattern: tuple[str, ...], row: Iterable[Target]) -> tuple[Target, ...]:
    """The targets a part may import: itself first, then its row; just the row when it says EVERYTHING, which holds
    the part already."""
    targets = tuple(row)
    if any(target.part == EVERYTHING for target in targets):
        return targets
    return (Target(name, "own" if EACH in pattern else "none"), *targets)
