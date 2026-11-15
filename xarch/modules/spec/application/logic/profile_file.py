"""Which loader reads a profile file, and where a profile comes from.

The format version the file starts with decides: `xarch: 2` is read by profile_v2. A profile in format 1 is not read at
all: it is refused with the command that converts it, whatever else it holds. A file with no version, or any other, is
refused too.
"""
from __future__ import annotations

from collections.abc import Callable, Collection, Mapping
from pathlib import Path
from typing import Any

from xarch.modules.spec.application.logic.profile_v2 import parse_v2
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Architecture, ArchitectureSource

VERSION = 2
"""The one format version this xarch reads."""
MIGRATE = "xarch profile migrate"


def parse_profile(document: Any, source: str, has_file: Callable[[str], bool],
                  folder_files: Callable[[str], tuple[str, ...] | None] | None = None,
                  presets: Mapping[str, Any] | None = None, bundled: Collection[str] = ()) -> Architecture:
    """The architecture the document describes; raises InvalidArchitecture listing every problem. See parse_v2 for what
    the arguments are."""
    written = f"`xarch: {VERSION}`"
    if not isinstance(document, Mapping):
        raise InvalidArchitecture(source, [f"must be a mapping of keys, starting with {written}"])
    if "xarch" not in document:
        raise InvalidArchitecture(source, [f"missing format version: start the file with {written}"])
    version = document["xarch"]
    if type(version) is int and version == 1:
        raise InvalidArchitecture(source, [f"format 1 is no longer read: run `{MIGRATE} {source}` to convert it to "
                                           f"format {VERSION}"])
    if type(version) is int and version == VERSION:
        return parse_v2(document, source, has_file, folder_files, presets, bundled)
    raise InvalidArchitecture(source, [f"unknown format version {version!r}: this xarch reads {written}"])


def source_of(location: str | Path, bundled: Collection[str]) -> ArchitectureSource:
    """A bare name (no folder, no suffix) is a bundled architecture; anything else is a path to a file."""
    path = Path(location)
    if isinstance(location, Path) or len(path.parts) != 1 or path.suffix:
        return ArchitectureSource(str(location), bundled=False)
    if location not in bundled:
        raise InvalidArchitecture(str(location), [f"no bundled architecture '{location}': use one of "
                                                  f"{', '.join(bundled)}, or a path to a .yaml or .json file"])
    return ArchitectureSource(location, bundled=True)
