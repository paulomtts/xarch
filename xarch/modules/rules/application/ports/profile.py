from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.outcomes import Known, Standing
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import KeyFacts, Reviewed


class Profiles(Protocol):
    """The architecture in force at a location (a bundled name or a path), in the checker's terms."""

    def profile(self, location: str) -> Profile: ...

    def standing(self, location: str, app: str) -> Standing:
        """The guards the profile leaves off, and those the bundled profile it is, or is compared with, leaves off too,
        and the files `init` would write now beside an app folder named app, in the profile's order."""
        ...

    def known(self, app: Path) -> Known:
        """The profiles the project holding the app folder knows: the one in force, if one is configured, and the
        bundled ones; raises ProfileUnusable when the one configured cannot be chosen or loaded."""
        ...

    def key(self, address: str) -> KeyFacts:
        """What the format says of the key at address; nothing for an address of no key; raises ProfileUnusable when
        the format cannot be explained."""
        ...

    def reviewed(self, app: Path, target: str | None, against: str | None = None) -> Reviewed:
        """The profile target names (a bundled name or a path), else the one configured for the project holding the
        app folder, checked but for its own checks, and compared with the profile against names when it is given;
        raises Unloaded with every problem when it does not load, NoProfile when none is given or configured, and
        ProfileUnusable when it cannot be chosen or against does not load."""
        ...
