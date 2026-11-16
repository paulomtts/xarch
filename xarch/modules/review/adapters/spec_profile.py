"""What review reads of a profile, read by the spec module: the only file in review that names spec, and it names only
spec's contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.values import PartText, Words
from xarch.modules.spec.contract import LINE, ProfileRefused, ProfileResult, ProfileView


class _Spec(Protocol):
    """The little review uses of spec's controller."""

    def profile(self, location: str) -> ProfileResult: ...


class SpecWords:
    """Satisfies review's Profile port by translating spec's ProfileView."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def words(self, profile: str) -> Words:
        """Each part's line is the one the profile writes, else spec's default. A profile spec refuses raises Refused
        with spec's reason."""
        match self._spec.profile(profile):
            case ProfileView(parts=parts, never=never, mask=mask, lines=lines):
                return Words(tuple(PartText(part.name, part.shown, part.litmus, part.role, lines.get(part.name, LINE),
                                            part.name in lines) for part in parts), never, mask)
            case ProfileRefused(reason):
                raise Refused(reason)
