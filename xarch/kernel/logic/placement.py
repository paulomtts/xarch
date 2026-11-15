"""Where a path sits among named path patterns, and which places a rule's target reaches.

A pattern is a path whose one `*` step stands for any name: an instance's of the repeating folder it sits in. A path
sits in the pattern it lies in, the deepest when patterns nest, with `*` capturing the name; what lies below the
pattern is the place's sub-path. A path is compared as Python names it: no `.py` on its file, and a package's
`__init__` is the package itself.

A target names a part, a scope and an optional path below the part. Scope "own" reaches the part in the importer's
instance, "any" in any instance, "none" a part outside the instances. EVERYTHING reaches every
place, including the places no part claims.

A part may always import itself: its own instance for a part inside a repeating folder, the part for one outside. A rule
never says so; `with_itself` adds it to the row of the part.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Literal

EACH = "*"
EVERYTHING = "*"

Scope = Literal["own", "any", "none"]


@dataclass(frozen=True)
class Repeat:
    """A repeating folder: the word one instance of it is called by, and the folder it repeats in."""
    word: str
    root: tuple[str, ...]


@dataclass(frozen=True)
class Target:
    """What a part may import: a part, or EVERYTHING; the instance it is in; and optionally only a path below it."""
    part: str
    scope: Scope = "none"
    sub: tuple[str, ...] = ()


@dataclass(frozen=True)
class Place:
    """Where a path sits: the part claiming it (None if none does), the instance `*` captured, and the path below."""
    part: str | None
    instance: str | None = None
    sub: tuple[str, ...] = ()


def root_of(pattern: tuple[str, ...]) -> tuple[str, ...] | None:
    """The folder the pattern's repeating step sits in; None when the pattern has none."""
    return pattern[:pattern.index(EACH)] if EACH in pattern else None


def repeat_of(repeats: Iterable[Repeat], pattern: tuple[str, ...]) -> Repeat | None:
    """The repeating folder a pattern lies in."""
    root = root_of(pattern)
    return next((repeat for repeat in repeats if repeat.root == root), None) if root is not None else None


def python_steps(path: tuple[str, ...]) -> tuple[str, ...]:
    """A path as Python names it: no .py on its file, and a package's __init__ is the package itself."""
    if path and path[-1].endswith(".py"):
        path = path[:-1] + (path[-1].removesuffix(".py"),)
    return path[:-1] if path and path[-1] == "__init__" else path


def place_of(patterns: Mapping[str, tuple[str, ...]], path: tuple[str, ...]) -> Place:
    """The place of a path among patterns, by name; Place(None) when no pattern claims it."""
    steps = python_steps(path)
    best = Place(None)
    depth = -1
    for name, raw in patterns.items():
        pattern = python_steps(raw)
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


def matches(pattern: tuple[str, ...], path: tuple[str, ...]) -> bool:
    """Whether a path is exactly the pattern, `*` standing for any name."""
    pattern, steps = python_steps(pattern), python_steps(path)
    return len(pattern) == len(steps) and all(
        step != EACH and want in (EACH, step) for want, step in zip(pattern, steps))


def reaches(target: Target, source: Place, place: Place) -> bool:
    """Whether target, in the rules of the part at source, allows importing what sits at place."""
    if target.part == EVERYTHING:
        return True
    if place.part is None or target.part != place.part or place.sub[:len(target.sub)] != target.sub:
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
