from __future__ import annotations

from collections.abc import Mapping

EACH = "<module>"


def matches(path: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
    if len(path) < len(pattern):
        return False
    return all(step == EACH or step == found for step, found in zip(pattern, path))


def part_of(path: tuple[str, ...], patterns: Mapping[str, tuple[str, ...]]) -> str | None:
    found = [(len(pattern), part) for part, pattern in patterns.items() if matches(path, pattern)]
    return max(found)[1] if found else None


def instance_of(path: tuple[str, ...], pattern: tuple[str, ...]) -> str | None:
    if EACH not in pattern or not matches(path, pattern):
        return None
    return path[pattern.index(EACH)]
