from __future__ import annotations

from typing import Protocol

from xarch.modules.rules.domain.values import Profile, Standing


class Profiles(Protocol):
    """The architecture in force at a location (a bundled name or a path), in the checker's terms."""

    def profile(self, location: str) -> Profile: ...

    def standing(self, location: str, app: str) -> Standing:
        """The guards the profile leaves off, and those the bundled profile it is, or is compared with, leaves off too,
        and the files `init` would write now beside an app folder named app, in the profile's order."""
        ...
