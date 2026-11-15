"""The values of converting a profile from format 1: what the old file says, and the files the converted folder
copies."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

Tree = dict[str, "Tree | None"]


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


@dataclass(frozen=True)
class Copy:
    """A file of the converted folder: where it goes, the file next to the old profile it is read from, and whether its
    example placeholders are rewritten."""
    destination: str
    source: str
    rewritten: bool = False


@dataclass(frozen=True)
class Conversion:
    """A conversion, written or, on a dry run, only planned: the folder, the converted profile in it, each file of the
    folder in the order written (its path in it, the file next to the old profile it is read from, None for the
    profile, and how many example placeholders were rewritten in it), what now means something else, what has no form
    in format 2 and is to be written by hand, and whether nothing was written."""
    folder: Path
    profile: Path
    files: tuple[tuple[str, str | None, int], ...]
    changes: tuple[str, ...]
    by_hand: tuple[str, ...]
    dry_run: bool
