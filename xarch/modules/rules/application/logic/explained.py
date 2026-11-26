"""What `xarch profile explain` says of the words a check is written in, read from the vocabulary the rule and the
engine read: the categories of words, a word by its address (`filters.public`, `kinds.class`), what it applies to, the
nearest addresses to one that does not exist, whether a rule uses a word (so that a check xarch has can be its
example), and the rules a key of the profile expands to.
"""
from __future__ import annotations

from collections.abc import Iterable
from difflib import get_close_matches

from xarch.modules.rules.domain.outcomes import Known
from xarch.modules.rules.domain.published import CHECKS, Slot
from xarch.modules.rules.domain.rule import OwnCheck, Rule
from xarch.modules.rules.domain.vocabulary import (
    FACT,
    FIELDS,
    FILE,
    FILTERS,
    KINDS,
    QUANTIFIERS,
    SLOTS,
    TARGET,
    TARGETS,
    VARIABLES,
    Filter,
    Kind,
    Quantifier,
    TargetKind,
    Variable,
    WordFacets,
)
from xarch.modules.rules.domain.worked import WORKED

Word = Kind | Filter | TargetKind | Variable | Quantifier
"""A word of the vocabulary."""

CATEGORIES: dict[str, tuple[Word, ...]] = {"kinds": KINDS, "quantifiers": QUANTIFIERS, "targets": TARGETS,
                                           "filters": FILTERS, "variables": VARIABLES}
"""Every category of words, by the address it is explained at, in the order a check is read."""
MEANINGS = {
    "kinds": "what a check reads (read, through, then_through): the kinds of fact a file says, each with the "
             "fields it carries",
    "quantifiers": "what a check does with what it keeps: may_not, may_only, must_reach, must_be_reached, at_most, "
                   "at_least",
    "targets": "what a kept fact is compared with (may_not, may_only, must_reach.targets)",
    "filters": "what must be true of a file or a fact (in.where, keep, except, cases.when, through_only); "
               "`not <filter>` holds where the filter does not",
    "variables": "what a message or a fix prints of a finding, written {<variable>}",
}
"""What each category holds, in a line."""
NEAREST = 3


def word_at(address: str) -> tuple[str, Word] | None:
    """The category and the word at an address, `<category>.<name>`; None when there is none."""
    category, _, name = address.strip().strip(".").partition(".")
    return next(((category, word) for word in CATEGORIES.get(category, ()) if word.name == name), None)


def category_at(address: str) -> str:
    """The category an address names on its own, "" for none."""
    typed = address.strip().strip(".")
    return typed if typed in CATEGORIES else ""


def _addresses() -> list[str]:
    return [*CATEGORIES, *(f"{category}.{word.name}" for category, words in CATEGORIES.items() for word in words),
            *(f"{CHECKS}.{slot.name}" for slot in SLOTS)]


def slot_at(address: str) -> Slot | None:
    """The slot of a check at an address, `checks.<slot>`; None when there is none."""
    prefix, _, name = address.strip().strip(".").partition(".")
    return next((slot for slot in SLOTS if slot.name == name), None) if prefix == CHECKS else None


def names_words(address: str) -> bool:
    """Whether an address is one of the words a check is written in: its first step is `checks` or a category."""
    first = address.strip().strip(".").partition(".")[0]
    return first == CHECKS or first in CATEGORIES


def close(typed: str) -> tuple[str, ...]:
    """The addresses of words that read like one that does not exist, by the whole address or by the name alone;
    none when none does."""
    found = get_close_matches(typed.strip().strip("."), _addresses(), n=NEAREST, cutoff=0.6)
    if found:
        return tuple(found)
    name = typed.strip().strip(".").rpartition(".")[2]
    by_name = {word.name: f"{category}.{word.name}" for category, words in CATEGORIES.items() for word in words}
    return tuple(by_name[found] for found in get_close_matches(name, list(by_name), n=NEAREST, cutoff=0.6))


def nearest(typed: str) -> tuple[str, ...]:
    """The addresses closest to one that does not exist: those that read like it (see close); else the categories."""
    return close(typed) or tuple(CATEGORIES)


ABOUT = {FILE: "the file a fact is in", FACT: "the fact", TARGET: "the target a fact reaches"}
"""What a filter asks about, as it is said."""


NO_RULE = "it expands to no rule of the engine here: the profile does not set it, or it is checked by a check of its own"
"""Why a key the engine does not expand shows no rule."""


def no_rule(read_by: str) -> str:
    """Why a key shows no rule: NO_RULE, or, for a key another command than `check` alone reads, that one."""
    return f"check makes no rule of it: only xarch {read_by} reads what it says" if read_by else NO_RULE


def facets(word: Word) -> WordFacets:
    """What the word says besides its name and meaning, as its category has it."""
    match word:
        case Kind():
            return WordFacets(side=word.side, fields=_fields(word), needs=_needs(word), verb=word.verb)
        case Filter():
            return WordFacets(about=word.about, side=word.side, value=word.value, needs=word.facts)
        case TargetKind():
            return WordFacets(side=word.side, value=word.values)
        case Variable():
            return WordFacets(side=word.side)
    return WordFacets()


def about(word: Word) -> str:
    """What a word asks about, as it is said; "" for a word that asks about nothing."""
    return ABOUT.get(facets(word).about, "")


def slot_meaning(slot: Slot) -> str:
    """What a slot of a check is for, and what it accepts, as one sentence."""
    return f"{slot.meaning}: {slot.accepts}"


def example_key(rule: Rule) -> str:
    """The key a rule shown as a word's example is named by: the key it expands from, else its id."""
    return rule.key or rule.id


def fallback(category: str, name: str) -> OwnCheck | None:
    """The check written for the explanation that shows a word when no profile's rule does: the first written with it,
    None when none is. For how a check is written (CHECKS), or a slot of it (CHECKS and the slot's name), the first
    written with that quantifier, else the first of all."""
    if category == CHECKS:
        return next((check for check in WORKED if check.rule.quantifier == name), WORKED[0])
    return next((check for check in WORKED if uses(check.rule, category, name)), None)


def applies(word: Word) -> tuple[str, ...]:
    """The kinds of fact a word applies to; every kind for a quantifier, none for a kind."""
    if isinstance(word, Kind):
        return ()
    if isinstance(word, Quantifier):
        return tuple(kind.name for kind in KINDS)
    return tuple(kind.name for kind in KINDS if word.applies_to(kind))


def _fields(kind: Kind) -> tuple[tuple[str, str, str], ...]:
    """The fields of a kind of fact: each name, what it is, and the filter that must hold for the fact to carry it
    ("" when it always does)."""
    return tuple((name, FIELDS[name], kind.sometimes.get(name, "")) for name in (*kind.fields, *kind.sometimes))


def _needs(kind: Kind) -> tuple[str, ...]:
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
            return any(condition.name == name for condition in rule.conditions)
        case "variables":
            return name in rule.variables
    return False


def keyed(rules: Iterable[Rule], address: str) -> list[Rule]:
    """The rules a key of the profile expands to: those whose key is that address, or matches it with any part or
    tier in place of the one it names (parts.holds for parts.<part>.holds), each once."""
    typed = address.strip().strip(".")
    found: list[Rule] = []
    for rule in rules:
        keys = [key.strip() for key in rule.key.split(";")] if rule.key else []
        if any(typed in (key, general(key)) for key in keys) and rule not in found:
            found.append(rule)
    return found


def general(key: str) -> str:
    """A key with the part or tier it names left out: parts.services.holds.classes.names as parts.holds.classes.names."""
    steps = key.split(".")
    return ".".join((steps[0], *steps[2:])) if steps[0] in ("parts", "tiers") and len(steps) > 2 else key


def searched(known: Known) -> tuple[str, ...]:
    """The profiles a word's example is looked for in, in order: the one in force first, then the bundled ones."""
    return (*filter(None, (known.in_force,)), *known.bundled)
