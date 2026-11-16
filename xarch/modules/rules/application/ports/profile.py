from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.rules.domain.published import KeyFacts, Reviewed
from xarch.modules.rules.domain.values import Profile, Standing


class Profiles(Protocol):
    """The architecture in force at a location (a bundled name or a path), in the checker's terms."""

    def profile(self, location: str) -> Profile: ...

    def standing(self, location: str, app: str) -> Standing:
        """The guards the profile leaves off, and those the bundled profile it is, or is compared with, leaves off too,
        and the files `init` would write now beside an app folder named app, in the profile's order."""
        ...

    def known(self, app: Path) -> tuple[str, ...]:
        """The profiles the project holding the app folder knows, the one in force first."""
        ...

    def key(self, address: str) -> KeyFacts:
        """What the format says of the key at address; nothing for an address of no key."""
        ...

    def reviewed(self, app: Path, target: str | None) -> Reviewed:
        """The profile target names (a bundled name or a path), else the one configured for the project holding the
        app folder, checked but for its own checks; raises Unloaded with every problem when it does not load,
        NoProfile when none is given or configured, and ProfileUnusable when it cannot be chosen."""
        ...
