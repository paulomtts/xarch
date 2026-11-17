from __future__ import annotations

from collections.abc import Iterable

from app.profile_values.language import Language


def shortfall(needed: Iterable[str], language: Language) -> frozenset[str]:
    return frozenset(needed) - language.facts


def approximated(needed: Iterable[str], language: Language) -> frozenset[str]:
    return frozenset(needed) & language.approximate


def unsupplied_keys(keys: dict[str, frozenset[str]], language: Language) -> tuple[str, ...]:
    return tuple(sorted(key for key, facts in keys.items() if shortfall(facts, language)))
