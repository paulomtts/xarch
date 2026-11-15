"""In-memory implementation of scaffold's Skeleton port. Not an adapter: a test double only."""
from __future__ import annotations


class FakeSkeleton:
    """Satisfies scaffold's Skeleton: the same entries, kinds and docs under every profile."""

    def __init__(self, top_level: list[tuple[tuple[str, ...], bool]],
                 kinds: dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]] | None = None,
                 docs: list[tuple[tuple[str, ...], str]] | None = None):
        self._top, self._kinds, self._docs = list(top_level), dict(kinds or {}), list(docs or [])

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return list(self._top)

    def kinds(self, profile: str) -> dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]]:
        return dict(self._kinds)

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        return list(self._docs)
