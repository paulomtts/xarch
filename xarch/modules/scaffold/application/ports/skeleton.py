from __future__ import annotations

from typing import Protocol

from xarch.modules.scaffold.domain.values import Language


class Skeleton(Protocol):
    """What to build: (path, is_dir) for every entry, parents before children."""

    def top_level(self, profile: str) -> list[tuple[tuple[str, ...], bool]]: ...

    def language(self, profile: str) -> Language:
        """The language of the app: how it is named, the file it has stand for each folder, and the words no name of
        an instance may be."""
        ...

    def default_app(self) -> str:
        """The app folder that is read when none is given or recorded, which needs no record."""
        ...

    def kinds(self, profile: str) -> dict[str, tuple[tuple[str, ...], list[tuple[tuple[str, ...], bool]]]]:
        """Every folder of the layout that declares `each:`, by the word one instance of it is called: the folder
        below the root, and what each instance of it holds."""
        ...

    def docs(self, profile: str) -> list[tuple[tuple[str, ...], str]]:
        """(path below the folder holding the app, text) for every project doc."""
        ...

    def files(self, profile: str, app: str) -> list[tuple[tuple[str, ...], str | bytes]]:
        """(path below the folder holding the app, content) for every other project file, for an app folder called
        app: text, or bytes for a file that is copied as it is. A path may lie inside the app folder."""
        ...
