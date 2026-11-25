"""What the structure rules work on: something that must exist below the root, and a repeating folder with what each
of its instances holds."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Requirement:
    """Something that must exist below the root: owner is who is incomplete without it (e.g. "app" or
    "app/modules/docs"), and shown how it is named when missing (e.g. "kernel/" or "application/controller" and its ending);
    when, the folder below the root of the optional part it lies in, the deepest: it must exist only where that folder
    does; () for always."""
    owner: str
    path: tuple[str, ...]
    is_dir: bool
    shown: str
    when: tuple[str, ...] = ()


@dataclass(frozen=True)
class Repeated:
    """A repeating folder: root, the folder holding its instances; parts, (path below an instance, is_dir) for what
    every instance holds; instances, the folders found in root; when, for each part path that lies in an optional part,
    that part's path below an instance, the deepest: it is required only in an instance that holds that part."""
    root: tuple[str, ...]
    parts: Iterable[tuple[tuple[str, ...], bool]]
    instances: Iterable[str]
    when: Mapping[tuple[str, ...], tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class Naming:
    """How the language of the app names a folder: what a name may be (a regular expression), and how a name private
    to its folder starts; "" for either: the language does not say."""
    names: str = ""
    private: str = ""


@dataclass(frozen=True)
class Beside:
    """Where the tests sit when every test of a part sits beside the code it tests (testing.beside): the patterns of a
    test file's name, matched against the file name alone with `*` for any text, and the folders below the tests root
    whose tests stay there (each tier's `folder`, and the fakes' folder)."""
    files: tuple[str, ...]
    kept: tuple[tuple[str, ...], ...]
