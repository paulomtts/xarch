from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.values import PartText


class Parts(Protocol):
    """The parts of a profile, as placement offers them."""

    def parts(self, profile: str) -> tuple[PartText, ...]:
        """The parts of the profile at location profile, in its order; raises Refused for one that cannot be used."""
        ...
