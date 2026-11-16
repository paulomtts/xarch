from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.values import CodeFile, Words


class Profile(Protocol):
    """What review reads of a profile: its parts, as placement offers them, and what review may send."""

    def words(self, profile: str) -> Words:
        """The words of the profile at location profile; raises Refused for one that cannot be used."""
        ...

    def examples(self, profile: str) -> tuple[tuple[CodeFile, ...], tuple[CodeFile, ...]]:
        """The files placement is held to, of the profile at location profile: the clean ones and the flagged ones,
        each a file by its path below the app, in the part that path lies in ("" for none), with its code and its
        imports; raises Refused for one that cannot be used."""
        ...
