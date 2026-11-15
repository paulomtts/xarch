"""What the structure rules work on: something that must exist below the root, and a repeating folder with what each
of its instances holds."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Requirement:
    """Something that must exist below the root: owner is who is incomplete without it (e.g. "app" or
    "app/modules/docs"), and shown how it is named when missing (e.g. "kernel/" or "application/controller" and its ending)."""
    owner: str
    path: tuple[str, ...]
    is_dir: bool
    shown: str


@dataclass(frozen=True)
class Repeated:
    """A repeating folder: root, the folder holding its instances; parts, (path below an instance, is_dir) for what
    every instance holds; instances, the folders found in root."""
    root: tuple[str, ...]
    parts: Iterable[tuple[tuple[str, ...], bool]]
    instances: Iterable[str]


@dataclass(frozen=True)
class Naming:
    """How the language of the app names a folder: what a name may be (a regular expression), and how a name private
    to its folder starts; "" for either: the language does not say."""
    names: str = ""
    private: str = ""

