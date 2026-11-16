from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.review.domain.values import Answer


class Answers(Protocol):
    """The answers kept in a folder, each under its key, holding no text of the code and no question."""

    def ready(self, folder: Path) -> None:
        """Nothing when answers can be kept in the folder, made or not yet; raises Refused, naming it, when it is no
        folder or is a link."""
        ...

    def get(self, folder: Path, key: str) -> Answer | None:
        """The answer kept under the key; None when there is none, none that can be read, or one reached through a
        link."""
        ...

    def put(self, folder: Path, key: str, answer: Answer) -> None:
        """Keep the answer under the key, creating the folder, in place of a link there rather than through it; raises
        Refused, naming the folder, when it cannot be written."""
        ...
