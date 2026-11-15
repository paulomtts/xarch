"""How a refusal to write over files names the ones that already exist."""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

SHOWN = 3
"""How many taken paths a refusal names before it counts the rest."""


def taken_phrase(taken: Sequence[Path]) -> str:
    """The files, as a phrase ending in the verb ("a, b and 2 more already exist"), or "" when there are none."""
    if not taken:
        return ""
    names = [path.as_posix() for path in taken]
    verb = "exists" if len(names) == 1 else "exist"
    shown = ", ".join(names[:SHOWN]) + (f" and {len(names) - SHOWN} more" if len(names) > SHOWN else "")
    return f"{shown} already {verb}"
