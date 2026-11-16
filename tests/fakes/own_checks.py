"""In-memory implementation of spec's OwnChecks port. Not an adapter: a test double only."""
from __future__ import annotations

from xarch.profile_values.checks import ChecksHeld


class FakeOwnChecks:
    """Satisfies spec's OwnChecks: what holding a profile's own checks finds, fixed per location (none found and no
    check, for a location not given)."""

    def __init__(self, held: dict[str, ChecksHeld] | None = None):
        self._held = dict(held or {})

    def held(self, location: str, app: str) -> ChecksHeld:
        return self._held.get(location, ChecksHeld((), 0))
