"""Whether a key of the profile is one the engine expands to rules when a profile sets it: one of the keys the book's
rules are keyed by (see expansion.KEYS), on any part or tier. A key that expands to no rule in a profile is either one
that profile sets nowhere, when the engine expands it, or one a check of xarch's own reads."""
from __future__ import annotations

from xarch.modules.rules.application.logic.expansion import KEYS
from xarch.modules.rules.application.logic.explained import general


def expands(address: str) -> bool:
    """Whether the engine expands the key at address to rules when a profile sets it (on any part or tier, for a key
    that names one)."""
    return general(address.strip().strip(".")) in KEYS
