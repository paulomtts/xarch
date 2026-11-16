from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from xarch.profile_values.checks import WrittenCheck


class CheckFormat(Protocol):
    """How a profile's checks are written as text: what `profile explain` shows of a rule, so that a check xarch has
    reads as one a profile could write."""

    def written(self, checks: Mapping[str, WrittenCheck]) -> str:
        """The checks as the `checks` of a profile, each under its id, with its examples when it has any."""
        ...
