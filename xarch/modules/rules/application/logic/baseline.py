"""The baseline: the violations a project had when it adopted xarch, recorded so that `check` reports only what is
not recorded, and the record may only go down.

A violation is keyed by its rule, its file and its message with every run of digits read as one mark, so that a line
number or a count in a message does not change it; the violations of one key are counted, and a key's count is its
ceiling. A violation whose key the record holds, up to its count, is baselined: not shown, counted. Every other one
is shown. A key found fewer times than recorded leaves the record above the code: the check passes, says by how much,
and `--strict` fails until the record is lowered. Lowering drops a key no longer found and lowers a count, never
raising one and never adding a key. A write of one rule changes only that rule's keys, and keeps every other key
of the record as it is.
"""
from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.outcomes import Baselined
from xarch.modules.rules.domain.published import BaselineStanding, Recorded, RuleCeiling

DIGITS = re.compile(r"\d+")
"""What a key reads as one mark in a message, 0: a run of digits."""

Key = tuple[str, str, str]
"""(rule, file, message with its digits marked)."""


def _key_of(rule: str, file: str, message: str) -> Key:
    """The key of a violation: its rule, its file, and its message with every run of digits read as one mark."""
    return rule, file, DIGITS.sub("0", message)


def recorded(violations: Iterable[Violation]) -> tuple[Recorded, ...]:
    """The record of the violations given, one entry per key with its count, in the order of rule, file and message;
    each entry keeps the message of the first violation of its key."""
    counts: Counter[Key] = Counter()
    first: dict[Key, Violation] = {}
    for violation in violations:
        key = _key_of(violation.rule, violation.file, violation.message)
        counts[key] += 1
        first.setdefault(key, violation)
    return tuple(Recorded(first[key].rule, first[key].file, first[key].message, counts[key]) for key in sorted(counts))


def _lowered(record: Iterable[Recorded], violations: Iterable[Violation]) -> tuple[Recorded, ...]:
    """The record lowered to the violations given: each entry kept at the lower of its count and how many violations
    of its key there are, an entry none has dropped; a key the record does not hold is never added."""
    found = Counter(_key_of(v.rule, v.file, v.message) for v in violations)
    kept = [(entry, min(entry.count, found[_key_of(entry.rule, entry.file, entry.message)])) for entry in record]
    return tuple(Recorded(entry.rule, entry.file, entry.message, count) for entry, count in kept if count)


def written(before: Iterable[Recorded] | None, violations: Iterable[Violation], reset: bool,
            rule: str = "") -> tuple[Recorded, ...]:
    """The record a write leaves: with reset, or with no record before, every violation recorded; else the record
    before lowered to them. With rule, only the violations and the keys of that rule are so written, and the record
    before keeps every key of another rule as it was."""
    entries = list(before or ())
    found = [v for v in violations if not rule or v.rule == rule]
    mine = [entry for entry in entries if not rule or entry.rule == rule]
    kept = [entry for entry in entries if rule and entry.rule != rule]
    fresh = recorded(found) if reset or before is None else _lowered(mine, found)
    return tuple(sorted((*kept, *fresh), key=lambda entry: _key_of(entry.rule, entry.file, entry.message)))


def applied(violations: Iterable[Violation], record: Iterable[Recorded], file: str) -> Baselined:
    """The violations the record does not hold, in their order, and how the record, kept in file, stands: by rule,
    how many it records and how many of those were found; how many violations it holds back; and how many it records
    that were not found (below)."""
    entries = list(record)
    room: Counter[Key] = Counter()
    for entry in entries:
        room[_key_of(entry.rule, entry.file, entry.message)] += entry.count
    shown: list[Violation] = []
    held: Counter[str] = Counter()
    for violation in violations:
        key = _key_of(violation.rule, violation.file, violation.message)
        if room[key] > 0:
            room[key] -= 1
            held[violation.rule] += 1
        else:
            shown.append(violation)
    ceilings: Counter[str] = Counter()
    for entry in entries:
        ceilings[entry.rule] += entry.count
    rules = tuple(RuleCeiling(rule, ceilings[rule], held[rule]) for rule in sorted(ceilings))
    return Baselined(tuple(shown), BaselineStanding(file, rules, sum(held.values()),
                                                    sum(ceilings.values()) - sum(held.values())))
