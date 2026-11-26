"""The values the layout module hands out as they are, which its contract re-exports."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Waived:
    """A finding of the layout an entry of structure.accepted accepts, which is then not reported: its rule
    (structure or test-tree), its file as shown, its message, and why."""
    rule: str
    file: str
    message: str
    why: str
