from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.values import Words


class Profile(Protocol):
    """What review reads of a profile: its parts, as placement offers them, and what review may send."""

    def words(self, profile: str) -> Words:
        """The words of the profile at location profile; raises Refused for one that cannot be used."""
        ...
