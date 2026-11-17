from __future__ import annotations

from collections.abc import Mapping


def cycles(wraps: Mapping[str, frozenset[str]]) -> tuple[tuple[str, ...], ...]:
    found: list[tuple[str, ...]] = []
    for start in sorted(wraps):
        for path in _walks(start, wraps, (start,)):
            ring = _rotated(path)
            if ring not in found:
                found.append(ring)
    return tuple(found)


def _walks(at: str, wraps: Mapping[str, frozenset[str]], path: tuple[str, ...]) -> list[tuple[str, ...]]:
    closed = []
    for next_one in sorted(wraps.get(at, frozenset())):
        if next_one == path[0]:
            closed.append(path)
        elif next_one not in path:
            closed += _walks(next_one, wraps, path + (next_one,))
    return closed


def _rotated(path: tuple[str, ...]) -> tuple[str, ...]:
    first = path.index(min(path))
    return path[first:] + path[:first]
