"""The parts of a profile read by the spec module: the only file in review that names spec, and it names only spec's
contract."""
from __future__ import annotations

from typing import Protocol

from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.values import PartText
from xarch.modules.spec.contract import ProfileRefused, ProfileResult, ProfileView


class _Spec(Protocol):
    """The little review uses of spec's controller."""

    def profile(self, location: str) -> ProfileResult: ...


class SpecParts:
    """Satisfies review's Parts port by translating spec's ProfileView."""

    def __init__(self, spec: _Spec):
        self._spec = spec

    def parts(self, profile: str) -> tuple[PartText, ...]:
        """A profile spec refuses raises Refused with spec's reason."""
        match self._spec.profile(profile):
            case ProfileView(parts=parts):
                return tuple(PartText(part.name, part.shown, part.litmus, part.role) for part in parts)
            case ProfileRefused(reason):
                raise Refused(reason)
