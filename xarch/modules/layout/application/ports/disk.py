from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from xarch.modules.layout.domain.structure import Requirement


class Disk(Protocol):
    """What the layout asks of the disk below a root."""

    def present(self, root: Path, required: Iterable[Requirement]) -> set[Requirement]:
        """The required folders and files that exist below root, each as the kind it must be."""
        ...

    def instances(self, root: Path, each: tuple[str, ...]) -> list[str]:
        """The names of the folders inside the repeating folder each of root that the disk shows (none it hides); []
        if there is none."""
        ...

    def below(self, root: Path, each: tuple[str, ...]) -> list[tuple[str, ...]]:
        """Every folder at any depth inside the repeating folder each of root that the disk shows (none it hides), as its
        path below it; [] if there is none."""
        ...
