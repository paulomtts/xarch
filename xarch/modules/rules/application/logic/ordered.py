"""The order a check gives its violations in: by file, then line (a whole file first), then rule."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation


def ordered(found: Iterable[Violation]) -> tuple[Violation, ...]:
    """By file, then line (a whole file first), then rule; stable for the rest."""
    return tuple(sorted(found, key=lambda v: (v.file, v.line, v.rule)))
