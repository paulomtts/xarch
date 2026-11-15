"""Which architecture is in force.

An architecture is named by a location: a bundled name such as "web", or a path to an architecture file. A path
configured in a pyproject.toml is relative to the folder holding that file; one given on the command line, to the
current folder.
"""
from __future__ import annotations

from collections.abc import Collection
from pathlib import Path

from xarch.modules.spec.domain.errors import NoProfile, UnknownProfile
from xarch.modules.spec.domain.values import Configured


def is_path(location: str) -> bool:
    """Whether a location names a file rather than a bundled architecture: it has a folder or a suffix."""
    path = Path(location)
    return len(path.parts) != 1 or bool(path.suffix)


def choose(override: str | None, configured: Configured | None, bundled: Collection[str]) -> str:
    """The location in force: an explicit override, else the configured one; raises NoProfile when there is neither."""
    if override is not None:
        return _checked(override, None, bundled)
    if configured is not None:
        return _checked(configured.name, configured.source, bundled)
    raise NoProfile(bundled)


def _checked(location: str, source: Path | None, bundled: Collection[str]) -> str:
    if is_path(location):
        return str(source.parent / location) if source is not None else location
    if location not in bundled:
        raise UnknownProfile(location, bundled, source)
    return location

