"""Looking keys up in the table of every key of the profile format."""
from __future__ import annotations

import re

from xarch.modules.spec.application.logic.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import HELD, Key

_PLACEHOLDER = re.compile(r"\.?<[^>]*>|\[\]")


def plain(address: str) -> str:
    """The address as a person types it: without the placeholder steps and `[]`, parts.<part>.may_import being
    parts.may_import."""
    return _PLACEHOLDER.sub("", address)


def shown(key: Key) -> str:
    """The address of a key as a person reads it: plain, but a slot of an entry of a map of ids keeps the id's step,
    evals.<id>.ask, since a key of the map itself (evals.placement) may sit beside the entries."""
    return key.address if key.scope in HELD else plain(key.address)


def keys_of(scope: str) -> tuple[Key, ...]:
    """The keys of a scope, or the slots of an entry of a map of ids (see HELD)."""
    return tuple(key for key in (*KEYS, *SLOTS) if key.scope == scope)


def names_of(scope: str) -> set[str]:
    return {key.name for key in keys_of(scope)}


def required_of(scope: str) -> tuple[str, ...]:
    return tuple(key.name for key in keys_of(scope) if key.required)
