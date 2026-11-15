from __future__ import annotations

from typing import Protocol


class Skeleton(Protocol):
    """What to build: (path, is_dir) for every entry, parents before children."""

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]: ...

    def package_file(self, profile: str) -> str:
        """The name of the file the language of the app has stand for each folder, which every folder of the skeleton
        holds."""
        ...

    def language(self, profile: str) -> str:
        """How the language of the app is named."""
        ...

    def reserved(self, profile: str) -> frozenset[str]:
        """The words no name of an instance may be."""
        ...

    def kinds(self, profile: str) -> dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]]:
        """Every folder of the layout that declares `each:`, by its path written with '/': the folder below the
        root, and what each instance of it holds."""
        ...

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        """(path below the folder holding the app, text) for every project doc."""
        ...

    def files(self, profile: str, app: str) -> list[tuple[tuple[str, ...], str | bytes]]:
        """(path below the folder holding the app, content) for every other project file, for an app folder called
        app: text, or bytes for a file that is copied as it is. A path may lie inside the app folder."""
        ...
