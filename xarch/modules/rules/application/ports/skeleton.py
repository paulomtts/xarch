from __future__ import annotations

from typing import Protocol

from xarch.modules.rules.domain.values import Parts


class Skeleton(Protocol):
    """The folder names the architecture gives meaning to, under a profile."""

    def parts(self, profile: str) -> Parts: ...
