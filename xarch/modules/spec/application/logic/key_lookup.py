"""Looking keys up in the table of every key of the profile format."""
from __future__ import annotations

import re

from xarch.modules.spec.domain.profile_keys import KEYS, Key

_PLACEHOLDER = re.compile(r"\.?<[^>]*>|\[\]")


def plain(address: str) -> str:
    """The address as a person types it: without the placeholder steps and `[]`, parts.<part>.may_import being
    parts.may_import."""
    return _PLACEHOLDER.sub("", address)


def keys_of(scope: str) -> tuple[Key, ...]:
    return tuple(key for key in KEYS if key.scope == scope)


def names_of(scope: str) -> set[str]:
    return {key.name for key in keys_of(scope)}


def required_of(scope: str) -> tuple[str, ...]:
    return tuple(key.name for key in keys_of(scope) if key.required)
