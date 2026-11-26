"""The values the layout module hands out as they are, which its contract re-exports."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Waived:
    """A finding of the layout an entry of the profile accepts, which is then not reported: its rule (structure,
    test-tree or counterpart), its file as shown, its message, why, and the key of the entry (structure.accepted, or
    counterparts.<id>.accepted)."""
    rule: str
    file: str
    message: str
    why: str
    key: str = "structure.accepted"
