from __future__ import annotations

from typing import Protocol

from xarch.modules.layout.domain.structure import Allowed, Beside, Counterpart, Naming, Word


class Skeleton(Protocol):
    """What the architecture requires to exist, under a profile."""

    def top_level(self, profile: str) -> list[tuple[str, ...]]:
        """Every folder the layout declares outside the repeating folders, at any depth, parents before children."""
        ...

    def top_level_files(self, profile: str) -> list[tuple[str, ...]]:
        """Every file the layout declares outside the repeating folders, at any depth."""
        ...

    def each_roots(self, profile: str) -> list[tuple[str, ...]]:
        """The folder holding the instances of each repeating folder of the layout, in the order of the profile."""
        ...

    def naming(self, profile: str) -> Naming:
        """How the language of the app names a folder."""
        ...

    def each_parts(self, profile: str, root: tuple[str, ...]) -> list[tuple[tuple[str, ...], bool]]:
        """(path below an instance, is_dir) for every part that must exist in each instance of the repeating folder
        in root."""
        ...

    def when(self, profile: str, root: tuple[str, ...] | None = None) -> dict[tuple[str, ...], tuple[str, ...]]:
        """For each folder or file the layout requires only where an optional part holding it is there, that part's
        path, the deepest: both below the app root, outside the repeating folders; or, root given, both below an
        instance of the repeating folder in root."""
        ...

    def accepted(self, profile: str) -> list[Allowed]:
        """The findings of the layout the profile accepts (structure.accepted), in the order written."""
        ...

    def counterparts(self, profile: str) -> list[Counterpart]:
        """What the profile says lies with what (counterparts), in the order written."""
        ...

    def words(self, profile: str) -> list[Word]:
        """Each repeating folder of the layout as a counterpart's placeholder reads it, in the order of the profile:
        with the names the layout writes beside its instances, which structure does not count as instances either."""
        ...

    def beside(self, profile: str) -> Beside | None:
        """Where the tests sit when every test of a part sits beside the code it tests; None when the profile keeps
        them in the mirrored tests tree."""
        ...
