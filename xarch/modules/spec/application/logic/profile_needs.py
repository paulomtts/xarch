"""What the keys a profile sets need of the language's reader: every key that configures a check needs the facts of
the source that check reads (see capabilities and key_table). One walk of the key table finds those keys however deep
they sit: from the file's keys into the scope each key opens, and from there as far down as the table's scopes go,
into a mapping, each entry of a map of names (parts.<part>) and each entry of a list (docs.naming[]), which is
addressed by its index from 0 (<list>.0.<key>). A key set to false or null configures nothing, but a guard, which its
name alone configures. A key whose language does not supply one of its facts is a problem of the profile, naming the
key, the fact and what to do; one whose language supplies a fact partly is kept, and listed as approximate where the
check is run. A fact a key's check reads only when the language supplies it (see Key.when_supplied) is no problem
when it is not: the key is kept, its check reads less, and it is listed as approximate in a sentence that says so.
"""
from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from dataclasses import replace
from typing import Any

from xarch.kernel.logic.capabilities import shortfalls
from xarch.modules.spec.domain.key_table import KEYS, SLOTS
from xarch.modules.spec.domain.profile_keys import GUARD, PROFILE, SCOPES, Key
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.capabilities import FACTS, Shortfall

_NAMED = re.compile(r"\.<[^.>]*>$")
"""The end of the address of a scope whose entries the profile names (parts.<part>): a placeholder step."""


def _configured(mapping: Mapping[Any, Any], scope: str, at: str, presets: Mapping[str, Any],
                keys: tuple[Key, ...]) -> Iterator[tuple[str, Key]]:
    """Each key of the table that the mapping of the scope sets and that needs facts, with its address in the file (at
    is the mapping's address and a dot, "" for the file), in the order of the table, each followed by those of the
    scope it opens: depth first. A key the mapping does not hold, or holds as false or null, configures nothing, and
    nothing below it is walked; a guard is configured by its name alone. The file's testing, written as the name of a
    preset, is walked as the preset's mapping."""
    for key in (key for key in keys if key.scope == scope):
        value = mapping.get(key.name)
        if key.name not in mapping or (scope != GUARD and (value is None or value is False)):
            continue
        address = f"{at}{key.name}"
        if key.needs:
            yield address, key
        if scope == PROFILE and key.name == "testing" and isinstance(value, str):
            value = presets.get(value)
        for where, held in _held(value, SCOPES.get(key.opens, key.opens), address) if key.opens else ():
            yield from _configured(held, key.opens, f"{where}.", presets, keys)


def _held(value: Any, where: str, address: str) -> list[tuple[str, Mapping[Any, Any]]]:
    """The mappings a key's value holds for the scope it opens, each with its address, by the shape the scope's
    address (where) says: for one ending in [], a list, each entry by its index from 0, every entry counted; for one
    ending in a placeholder step, a mapping of names the profile chooses, each entry by its name; else the mapping
    itself. A value of another shape, and an entry that is no mapping, hold none."""
    if where.endswith("[]"):
        entries = [(f"{address}.{index}", entry) for index, entry in enumerate(value)] if isinstance(value, list) else []
    elif _NAMED.search(where):
        entries = [(f"{address}.{name}", entry) for name, entry in value.items()] if isinstance(value, Mapping) else []
    else:
        entries = [(address, value)]
    return [(found, entry) for found, entry in entries if isinstance(entry, Mapping)]


def short(document: Mapping[Any, Any], presets: Mapping[str, Any], language: Language, *,
          keys: tuple[Key, ...] = (*KEYS, *SLOTS)) -> list[Shortfall]:
    """The facts the keys the document sets need that its language supplies partly or not at all, in the order of the
    walk (see _configured); none when no language is known. keys is the table walked: every key of the format unless
    another is given."""
    if language.checked.supplies is None:
        return []
    supplies = {supply.fact: supply for supply in language.checked.supplies}
    return [read_less(found, key, language) for address, key in _configured(document, PROFILE, "", presets, keys)
            for found in shortfalls(address, key.needs, supplies)]


def read_less(found: Shortfall, key: Key, language: Language) -> Shortfall:
    """The shortfall of a fact the key's check reads only when the language supplies it, which it does not, said as
    what the check then reads less; any other as it is."""
    if found.note is not None or found.fact not in key.when_supplied:
        return found
    return replace(found, note=f"{key.without}: the language {language.checked.title} does not supply {found.fact}",
                   unread=True)


def refused(found: list[Shortfall], language: Language) -> list[str]:
    """A problem for each fact a key needs that the language does not supply."""
    return [f"{item.address}: its check reads {item.fact} ({FACTS[item.fact]}), which the language {language.name} "
            f"does not supply: drop {item.address}, or check the app with a language whose reader supplies {item.fact}"
            for item in found if item.note is None]


def approximate(found: list[Shortfall]) -> tuple[Shortfall, ...]:
    """The keys whose check reads a fact the language supplies only partly."""
    return tuple(item for item in found if item.note is not None)
