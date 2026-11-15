"""In-memory implementation of scaffold's Skeleton port. Not an adapter: a test double only."""
from __future__ import annotations


class FakeSkeleton:
    """Satisfies scaffold's Skeleton: the same entries, kinds, docs and files under every profile."""

    def __init__(self, top_level: list[tuple[tuple[str, ...], bool]],
                 kinds: dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]] | None = None,
                 docs: list[tuple[tuple[str, ...], str]] | None = None,
                 files: list[tuple[tuple[str, ...], str]] | None = None):
        self._top, self._kinds, self._docs = list(top_level), dict(kinds or {}), list(docs or [])
        self._files = list(files or [])

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]:
        return list(self._top)

    def kinds(self, profile: str) -> dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]]:
        return dict(self._kinds)

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        return list(self._docs)

    def files(self, profile: str, app: str) -> list[tuple[tuple[str, ...], str]]:
        """Each file's text is its template with `<app>` replaced by the app folder's name."""
        return [(path, text.replace("<app>", app)) for path, text in self._files]
