"""Where a profile comes from."""
from __future__ import annotations

from collections.abc import Collection
from pathlib import Path

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import ArchitectureSource


def source_of(location: str | Path, bundled: Collection[str]) -> ArchitectureSource:
    """A bare name (no folder, no suffix) is a bundled architecture; anything else is a path to a file."""
    if ArchitectureSource.names_a_file(location):
        return ArchitectureSource(str(location), bundled=False)
    if location not in bundled:
        raise InvalidArchitecture(str(location), [f"no bundled architecture '{location}': use one of "
                                                  f"{', '.join(bundled)}, or a path to a .yaml or .json file"])
    return ArchitectureSource(location, bundled=True)
