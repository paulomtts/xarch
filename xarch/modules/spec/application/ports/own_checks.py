from __future__ import annotations

from typing import Protocol

from xarch.profile_values.checks import ChecksHeld


class OwnChecks(Protocol):
    """The checks a profile writes itself held to their examples, by the module that knows what their words mean."""

    def held(self, location: str, app: str) -> ChecksHeld:
        """What holding the checks of the profile at location to their examples finds, the app being the package app
        names; a profile whose checks cannot be made, or that cannot be used, has that as its problems."""
        ...
