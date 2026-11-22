"""Looking keys up in the table of every key of the profile format."""
from __future__ import annotations

import re

from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import HELD, PROFILE, RETIRED, SCOPES, Key, Retired

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


def retired(scope: str, name: str) -> str:
    """The fixed text of the entry of the table of retired names for the name in the scope; "" when it has none."""
    return next((entry.text for entry in RETIRED if entry.scope == scope and entry.name == name), "")


def retired_at(address: str) -> str:
    """The fixed text of the entry of the table of retired names at an address as a person types it: plain, with or
    without placeholders (parts.tier and parts.<part>.tier), the bare name for a key of the file, and for a slot of an
    entry of a map of ids the id's placeholder or any id in its step; "" when no entry is there. A rule id has no
    address."""
    written = address.strip().strip(".")
    return next((entry.text for entry in RETIRED if _at(entry, plain(written), written)), "")


def _at(entry: Retired, typed: str, written: str) -> bool:
    """Whether the entry's address is the one typed (plain) or written (as typed, placeholders kept)."""
    if entry.scope == PROFILE:
        return typed == entry.name
    if entry.scope in HELD:
        return written == f"{entry.scope}.{entry.name}" or of_an_entry(typed, entry.scope, entry.name)
    return entry.scope in SCOPES and typed == plain(f"{SCOPES[entry.scope]}.{entry.name}")


def of_an_entry(typed: str, scope: str, name: str) -> bool:
    """Whether a typed address is the name's in the scope of an entry of a map of ids (see HELD) under an id of the
    entry: the map's address, an id that is no key of the map, and the name."""
    holder, _, last = typed.rpartition(".")
    above, _, entry = holder.rpartition(".")
    held = HELD.get(scope, "")
    return last == name and above == SCOPES.get(held, "") and bool(entry) and entry not in names_of(held)
