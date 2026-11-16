"""What the keys a profile sets need of the language's reader: every key that configures a check needs the facts of
the source that check reads (see capabilities and key_table). A key set to false configures nothing. A key whose
language does not supply one of its facts is a problem of the profile, naming the key, the fact and what to do; one
whose language supplies a fact partly is kept, and listed as approximate where the check is run.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

from xarch.kernel.logic.capabilities import shortfalls
from xarch.modules.spec.application.logic.key_lookup import keys_of
from xarch.modules.spec.domain.profile_keys import GUARD, PART, PROFILE, TESTING, TIER, Key
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.capabilities import FACTS, Shortfall

def _configured(document: Mapping[Any, Any], presets: Mapping[str, Any]) -> Iterator[tuple[str, Key]]:
    """Each key the document sets that needs facts, with its address in the file, in the order of the file's scopes:
    the file, its parts, its tiers, its testing (a preset by what the preset holds), its guards, each with the keys of
    its own map that need facts and are set."""
    yield from _set(document, keys_of(PROFILE), "")
    for scope, held in ((PART, "parts"), (TIER, "tiers")):
        entries = document.get(held)
        for name, value in entries.items() if isinstance(entries, Mapping) else ():
            if isinstance(value, Mapping):
                yield from _set(value, keys_of(scope), f"{held}.{name}.")
    testing = document.get("testing")
    testing = presets.get(testing) if isinstance(testing, str) else testing
    if isinstance(testing, Mapping):
        yield from _set(testing, keys_of(TESTING), "testing.")
    guards = document.get("guards")
    for key in keys_of(GUARD) if isinstance(guards, Mapping) else ():
        if key.name in guards:
            yield f"guards.{key.name}", key
            held = guards[key.name]
            for nested in _guard_keys(key.name) if isinstance(held, Mapping) else ():
                if nested.needs and held.get(nested.name) not in (None, False):
                    yield f"guards.{key.name}.{nested.name}", nested


def _guard_keys(name: str) -> tuple[Key, ...]:
    return keys_of(f"{GUARD}.{name}")


def _set(mapping: Mapping[Any, Any], keys: tuple[Key, ...], prefix: str) -> Iterator[tuple[str, Key]]:
    for key in keys:
        if key.needs and key.name in mapping and mapping[key.name] is not False:
            yield f"{prefix}{key.name}", key


def short(document: Mapping[Any, Any], presets: Mapping[str, Any], language: Language) -> list[Shortfall]:
    """The facts the keys the document sets need that its language supplies partly or not at all; none when no
    language is known."""
    if language.checked.supplies is None:
        return []
    supplies = {supply.fact: supply for supply in language.checked.supplies}
    return [found for address, key in _configured(document, presets)
            for found in shortfalls(address, key.needs, supplies)]


def refused(found: list[Shortfall], language: Language) -> list[str]:
    """A problem for each fact a key needs that the language does not supply."""
    return [f"{item.address}: its check reads {item.fact} ({FACTS[item.fact]}), which the language {language.name} "
            f"does not supply: drop {item.address}, or check the app with a language whose reader supplies {item.fact}"
            for item in found if item.note is None]


def approximate(found: list[Shortfall]) -> tuple[Shortfall, ...]:
    """The keys whose check reads a fact the language supplies only partly."""
    return tuple(item for item in found if item.note is not None)
