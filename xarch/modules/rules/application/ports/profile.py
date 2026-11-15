from __future__ import annotations

from typing import Protocol

from xarch.modules.rules.domain.values import Profile


class Profiles(Protocol):
    """The architecture in force at a location (a bundled name or a path), in the checker's terms."""

    def profile(self, location: str) -> Profile: ...
