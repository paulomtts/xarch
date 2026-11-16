"""The values of converting a profile from format 1: what the old file says, and each file the converted folder
copies."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

Tree = dict[str, "Tree | None"]


@dataclass(frozen=True)
class Copy:
    """A file of the converted folder: where it goes, the file next to the old profile it is read from, and whether its
    example placeholders are rewritten."""
    destination: str
    source: str
    rewritten: bool = False


@dataclass(frozen=True)
class OldPart:
    name: str
    path: tuple[str, ...]
    role: str
    litmus: str
    entry: bool
    untested: str


@dataclass(frozen=True)
class OldProfile:
    """What a profile in format 1 says. layout is the tree with the repeating folder as `*` and None for a file;
    singular is the repeating folder's word; notes are by layout path; the rest is as written, or None when absent."""
    name: str
    layout: Tree
    singular: str
    parts: dict[str, OldPart]
    notes: dict[tuple[str, ...], str]
    raw: Mapping[str, Any]
    extra: tuple[str, ...] = field(default_factory=tuple)

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)
