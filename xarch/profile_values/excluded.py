"""The folders below the app that are not its source, as the profile names them."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Excluded:
    """A folder below the app that is not its source, and why: no check reads it.

    path: below the app folder, e.g. ("architectures", "examples")
    reason: one line, shown in the enforcement section
    """
    path: tuple[str, ...]
    reason: str
