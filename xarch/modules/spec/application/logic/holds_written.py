"""What a part's `holds` says: the kinds of definition its files may define at the top level, each with its settings.

    holds: {classes: {names, immutable, built_by}, functions: {names}, records: {names, immutable},
            exceptions: {names}}

A kind is written `{}` for no setting; `records` or `exceptions` beside `classes`, which already allows them, is
written only to give it a setting. `holds` written as one word, the form before 0.3.0, is refused with the map that
allows the same, from the table of retired names; so is a setting written under a kind that does not take it.
"""
from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Any

from xarch.kernel.logic.targets import NAME_PATTERN
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of, retired_value
from xarch.modules.spec.domain.profile_keys import (
    PART,
    PART_HOLDS_CLASSES,
    PART_HOLDS_EXCEPTIONS,
    PART_HOLDS_FUNCTIONS,
    PART_HOLDS_RECORDS,
)
from xarch.modules.spec.domain.published import KINDS, Held

SCOPES = {"classes": PART_HOLDS_CLASSES, "functions": PART_HOLDS_FUNCTIONS, "records": PART_HOLDS_RECORDS,
          "exceptions": PART_HOLDS_EXCEPTIONS}
"""The scope of the settings each kind takes."""
EXAMPLES = {"classes": '{names: "*Service"}', "functions": '{names: "is_*"}', "records": "{immutable: true}",
            "exceptions": '{names: "*Error"}'}
"""A map of settings each kind may be written with, as its refusal shows one."""
IMMUTABLE = {"classes": "whether every class of the part, but an exception, is an immutable record",
             "records": "whether every record of the part is an immutable record"}
"""What `immutable` says under each kind that takes it."""
NARROWER = ("records", "exceptions")
"""The kinds every class covers too."""


def holds(value: Any, where: str, declared: Collection[str], problems: list[str], *,
          words: Collection[str]) -> tuple[Held, ...]:
    """The kinds the `holds` of the part at where lists, each with its settings, in the order of KINDS; none when it
    is refused, each problem added to problems; words are the profile's, which a part a setting names never takes."""
    at = f"{where}.holds"
    retired = retired_value(PART, "holds", value) if isinstance(value, str) else ""
    if retired:
        problems.append(f"{at}: {value!r}: {retired}")
        return ()
    if not isinstance(value, Mapping):
        problems.append(f"{at}: must be a map of kinds, such as {{classes: {{}}}}")
        return ()
    if not value:
        problems.append(f"{at}: lists no kind: list the kinds the part may hold, or drop holds to allow every kind")
        return ()
    problems += [f"{at}: no kind {str(name)!r}: use {', '.join(sorted(KINDS))}" for name in value if name not in KINDS]
    return tuple(held for kind in KINDS if kind in value
                 for held in _kind(kind, value[kind], "classes" in value, f"{at}.{kind}", declared, problems, words))


def _kind(kind: str, settings: Any, beside_classes: bool, at: str, declared: Collection[str],
          problems: list[str], words: Collection[str]) -> tuple[Held, ...]:
    """The kind with the settings written for it, at its address; none when it is no map."""
    if not isinstance(settings, Mapping):
        problems.append(f"{at}: must be a map of its settings, {{}} for none, such as {EXAMPLES[kind]}")
        return ()
    known = names_of(SCOPES[kind])
    problems += ck.unknown_keys(settings, known, at, SCOPES[kind])
    if kind in NARROWER and beside_classes and not settings:
        problems.append(f"{at}: says nothing beside classes, which already allows {kind}: give it a setting, or drop it")
    names = _patterns(settings["names"], f"{at}.names", problems) if "names" in settings else ()
    immutable = _immutable(settings, kind, at, problems) if "immutable" in known else False
    built_by = tuple(ck.part_names(settings["built_by"], declared, f"{at}.built_by", problems, words=words)) \
        if "built_by" in known and "built_by" in settings else ()
    return (Held(kind, names, immutable, built_by),)


def _immutable(settings: Mapping[Any, Any], kind: str, at: str, problems: list[str]) -> bool:
    value = settings.get("immutable", False)
    if isinstance(value, bool):
        return value
    problems.append(f"{at}.immutable: must be true or false: {IMMUTABLE[kind]}")
    return False


def _patterns(value: Any, where: str, problems: list[str]) -> tuple[str, ...]:
    """The name patterns written, one or a list of them."""
    items = [value] if isinstance(value, str) else value
    if not isinstance(items, list) or not items or items == [""]:
        problems.append(f"{where}: must be a name pattern with `*` for any text, such as *Service, or a list of them")
        return ()
    bad = [item for item in items if not isinstance(item, str) or not NAME_PATTERN.fullmatch(item)]
    problems += [f"{where}: {item!r} is not a name pattern: write it with no space, `@`, `/` or `:`, `*` standing for "
                 "any text" for item in bad]
    return () if bad else tuple(items)
