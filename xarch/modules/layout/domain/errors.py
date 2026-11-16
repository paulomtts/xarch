from __future__ import annotations

from xarch.kernel.errors import DomainError


class ProfileUnusable(DomainError):
    """The profile cannot give the skeleton the structure is checked against; reason says why, as the spec module put
    it."""
