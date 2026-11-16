"""What `xarch profile explain` says of the words a check is written in, read from the vocabulary the rule and the
engine read: the categories of words, a word by its address (`filters.public`, `kinds.class`), what it applies to, the
nearest addresses to one that does not exist, whether a rule uses a word (so that a check xarch has can be its
example), and the rules a key of the profile expands to.
"""
from __future__ import annotations

from collections.abc import Iterable
from difflib import get_close_matches
from string import Formatter

from xarch.modules.rules.domain.rule import Rule
from xarch.modules.rules.domain.vocabulary import (
    FIELDS,
    FILTERS,
    KINDS,
    QUANTIFIERS,
    SLOTS,
    TARGETS,
    VARIABLES,
    Filter,
    Kind,
    Quantifier,
    Slot,
    TargetKind,
    Variable,
)

Word = Kind | Filter | TargetKind | Variable | Quantifier
"""A word of the vocabulary."""

CATEGORIES: dict[str, tuple[Word, ...]] = {"kinds": KINDS, "quantifiers": QUANTIFIERS, "targets": TARGETS,
                                           "filters": FILTERS, "variables": VARIABLES}
"""Every category of words, by the address it is explained at, in the order a check is read."""
MEANINGS = {
    "kinds": "what a check reads (read, through, then_through): the kinds of fact a file says, each with the "
             "fields it carries",
    "quantifiers": "what a check does with what it keeps: may_not, may_only, must_reach, must_be_reached",
    "targets": "what a kept fact is compared with (may_not, may_only, must_reach.targets)",
    "filters": "what must be true of a file or a fact (in.where, keep, except, cases.when, through_only); "
               "`not <filter>` holds where the filter does not",
    "variables": "what a message or a fix prints of a finding, written {<variable>}",
}
"""What each category holds, in a line."""
NEAREST = 3
SLOTTED = "checks"
"""The first step of the address of a slot of a check: checks.keep."""


def word_at(address: str) -> tuple[str, Word] | None:
    """The category and the word at an address, `<category>.<name>`; None when there is none."""
    category, _, name = address.strip().strip(".").partition(".")
    return next(((category, word) for word in CATEGORIES.get(category, ()) if word.name == name), None)


def category_at(address: str) -> str:
    """The category an address names on its own, "" for none."""
    typed = address.strip().strip(".")
    return typed if typed in CATEGORIES else ""


def addresses() -> list[str]:
    return [*CATEGORIES, *(f"{category}.{word.name}" for category, words in CATEGORIES.items() for word in words),
            *(f"{SLOTTED}.{slot.name}" for slot in SLOTS)]


def slot_at(address: str) -> Slot | None:
    """The slot of a check at an address, `checks.<slot>`; None when there is none."""
    prefix, _, name = address.strip().strip(".").partition(".")
    return next((slot for slot in SLOTS if slot.name == name), None) if prefix == SLOTTED else None


def nearest(typed: str) -> tuple[str, ...]:
    """The addresses closest to one that does not exist: those that read like it, by the whole address or by the
    name alone; else the categories."""
    known = addresses()
    close = get_close_matches(typed.strip().strip("."), known, n=NEAREST, cutoff=0.6)
    if close:
        return tuple(close)
    name = typed.strip().strip(".").rpartition(".")[2]
    by_name = {word.name: f"{category}.{word.name}" for category, words in CATEGORIES.items() for word in words}
    close = get_close_matches(name, list(by_name), n=NEAREST, cutoff=0.6)
    return tuple(by_name[found] for found in close) if close else tuple(CATEGORIES)


def applies(word: Word) -> tuple[str, ...]:
    """The kinds of fact a word applies to; every kind for a quantifier, none for a kind."""
    if isinstance(word, Kind):
        return ()
    if isinstance(word, Quantifier):
        return tuple(kind.name for kind in KINDS)
    return tuple(kind.name for kind in KINDS if word.applies_to(kind))


def fields(kind: Kind) -> tuple[tuple[str, str, str], ...]:
    """The fields of a kind of fact: each name, what it is, and the filter that must hold for the fact to carry it
    ("" when it always does)."""
    return tuple((name, FIELDS[name], kind.sometimes.get(name, "")) for name in (*kind.fields, *kind.sometimes))


def needs(kind: Kind) -> tuple[str, ...]:
    """The facts of the source a kind needs of the language, those of its fields included."""
    return tuple(dict.fromkeys((*kind.needs, *(need for listed in kind.field_needs.values() for need in listed))))


def uses(rule: Rule, category: str, name: str) -> bool:
    """Whether a rule is written with the word."""
    match category:
        case "kinds":
            return name in (*rule.facts, *rule.links, *rule.spread)
        case "quantifiers":
            return rule.quantifier == name
        case "targets":
            return any(match.kind == name for match in rule.targets)
        case "filters":
            conditions = (*rule.scope.where, *rule.keep, *rule.exempt, *rule.via,
                          *(rule.roots.where if rule.roots else ()), *(c for s in rule.sayings for c in s.when))
            return any(condition.name == name for condition in conditions)
        case "variables":
            return name in _variables(rule)
    return False


def _variables(rule: Rule) -> set[str]:
    return {found for s in rule.sayings for text in (s.message, s.fix) for _, found, _, _ in Formatter().parse(text)
            if found} | {once for s in rule.sayings for once in s.once}


def keyed(rules: Iterable[Rule], address: str) -> list[Rule]:
    """The rules a key of the profile expands to: those whose key is that address, or matches it with any part or
    tier in place of the one it names (parts.names for parts.<part>.names), each once."""
    typed = address.strip().strip(".")
    found: list[Rule] = []
    for rule in rules:
        keys = [key.strip() for key in rule.key.split(";")] if rule.key else []
        if any(typed in (key, _general(key)) for key in keys) and rule not in found:
            found.append(rule)
    return found


def _general(key: str) -> str:
    """A key with the part or tier it names left out: parts.services.names as parts.names."""
    steps = key.split(".")
    return ".".join((steps[0], *steps[2:])) if steps[0] in ("parts", "tiers") and len(steps) > 2 else key
