"""In-memory implementation of layout's Skeleton port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.modules.layout.domain.errors import ProfileUnusable
from xarch.modules.layout.domain.structure import Allowed, Beside, Counterpart, Naming, Word


class FakeSkeleton:
    """Satisfies layout's Skeleton: the same top-level folders and repeating folders under every profile; repeats
    holds, by the folder of each repeating folder, the parts every instance of it holds; and how the language names
    a folder (the language says nothing unless given); where the tests sit under testing.beside (None: they mirror the
    app); when, by None for the top level or the folder of a repeating folder, the optional part each path required
    there lies in (none unless given); the findings structure.accepted accepts (none unless given); the counterparts,
    and the repeating folders as their placeholders read them (none unless given); a profile refused raises
    ProfileUnusable with its reason."""

    def __init__(self, top_level: list[tuple[str, ...]],
                 repeats: dict[tuple[str, ...], list[tuple[tuple[str, ...], bool]]] | None = None,
                 top_files: list[tuple[str, ...]] | None = None, naming: Naming = Naming(),
                 refused: dict[str, str] | None = None, beside: Beside | None = None,
                 when: dict[tuple[str, ...] | None, dict[tuple[str, ...], tuple[str, ...]]] | None = None,
                 accepted: list[Allowed] | None = None, counterparts: list[Counterpart] | None = None,
                 words: list[Word] | None = None):
        self._top, self._repeats = list(top_level), dict(repeats or {})
        self._files, self._naming, self._refused = list(top_files or []), naming, dict(refused or {})
        self._beside, self._when, self._accepted = beside, dict(when or {}), list(accepted or [])
        self._counterparts, self._words = list(counterparts or []), list(words or [])

    def counterparts(self, profile: str) -> list[Counterpart]:
        return list(self._counterparts)

    def words(self, profile: str) -> list[Word]:
        return list(self._words)

    def accepted(self, profile: str) -> list[Allowed]:
        return list(self._accepted)

    def when(self, profile: str, root: tuple[str, ...] | None = None) -> dict[tuple[str, ...], tuple[str, ...]]:
        return dict(self._when.get(root, {}))

    def naming(self, profile: str) -> Naming:
        return self._naming

    def top_level_files(self, profile: str) -> list[tuple[str, ...]]:
        return list(self._files)

    def top_level(self, profile: str) -> list[tuple[str, ...]]:
        return list(self._top)

    def each_roots(self, profile: str) -> list[tuple[str, ...]]:
        if profile in self._refused:
            raise ProfileUnusable(self._refused[profile])
        return list(self._repeats)

    def each_parts(self, profile: str, root: tuple[str, ...]) -> list[tuple[tuple[str, ...], bool]]:
        return list(self._repeats[root])

    def beside(self, profile: str) -> Beside | None:
        return self._beside
