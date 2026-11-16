"""The checks a profile writes itself, as values: spec reads them from the profile's `checks`, checks every name the
profile declares in them (an id, a part, a tier) and writes them as the format does; rules makes each a rule,
resolving the words of its vocabulary (a kind of target such as `place` or `part`, a filter, a variable) and refusing
a check whose words do not apply.

The records keep the shape the format writes: the files a check reads, the kinds of fact, the filters it keeps, one
quantifier with its targets and, for a quantifier of reach, how it reaches; the filters that excuse a finding, the
mode, how a finding is said (the cases first, the check's own message last) and the examples. A target is a kind and
its values as written; a filter is a Condition, as a rule names it.
"""
from __future__ import annotations

from dataclasses import dataclass

NEGATION = "not "
"""How a filter is negated: written after `not `."""

ANY = "*"
"""A scope's part that any file of its files is in: a part, the structure or no part."""
STRUCTURE = ""
"""A scope's part that is the structure: a folder of the layout no part claims."""

APP, TESTS, ALL = "app", "tests", "all"
"""The files a scope reads: the app's, the tests', or both, the app's first."""

FAIL, LIST = "fail", "list"
"""What a finding is: a violation, or a weak finding listed in the enforcement section."""

QUANTIFIER_SLOTS = ("may_not", "may_only", "must_reach", "must_be_reached")
"""The slots of which a check writes one, its quantifier."""


@dataclass(frozen=True)
class Condition:
    """A filter as a rule names it: the filter's name, its value for one that takes one, and whether it is negated
    (`not <name>`): the fact passes when the filter does not hold."""
    name: str
    value: str = ""
    negated: bool = False


@dataclass(frozen=True)
class Scope:
    """The files a rule reads: of the app, of the tests or both (files); the part they belong to (part: its name,
    STRUCTURE for the structure, ANY for any): the part a file of the app lies in, the part a test's folder mirrors; of
    a tier (tier: its name, "" for any); and the filters about the file it passes besides (where)."""
    files: str = APP
    part: str = ANY
    tier: str = ""
    where: tuple[Condition, ...] = ()

    @property
    def named_part(self) -> str:
        """The part the scope names, "" for any part or the structure."""
        return self.part if self.part not in (ANY, STRUCTURE) else ""


@dataclass(frozen=True)
class Saying:
    """How a finding is said, when the conditions hold of it (none: always): the message and the fix, each a sentence
    with `{variable}`s of the vocabulary, and the variables by which a file's findings said this way are said once each
    (empty: every one is said)."""
    message: str
    fix: str
    when: tuple[Condition, ...] = ()
    once: tuple[str, ...] = ()


@dataclass(frozen=True)
class WrittenTarget:
    """One target of a check as the profile writes it: a kind of target, and its values as written: None when the kind
    is written alone, an empty tuple when it is written with an empty list of values."""
    kind: str
    values: tuple[str, ...] | None = None


@dataclass(frozen=True)
class Quantified:
    """The quantifier of a check (`may_not`, `may_only`, `must_reach` or `must_be_reached`) and what it says: its
    targets (for `must_be_reached`, none); and for a quantifier of reach, the kinds of fact it reaches through, the
    filters a link passes (through_only), and for `must_be_reached` the files the reach starts from (start), the kinds
    of fact through which a declaration reached already reaches further (then_through), and whether a declaration is
    reached only from a file other than its own (by_another_file)."""
    slot: str
    targets: tuple[WrittenTarget, ...] = ()
    through: tuple[str, ...] = ()
    through_only: tuple[Condition, ...] = ()
    start: Scope | None = None
    then_through: tuple[str, ...] = ()
    by_another_file: bool = False


@dataclass(frozen=True)
class WrittenCheck:
    """A check of the profile's own: the files it reads (within, the format's `in`), the kinds of fact it reads, the
    filters a fact passes to be read (keep), its quantifier, the filters any one of which excuses a finding (exempt,
    the format's `except`), whether a finding fails the check or is listed (mode), how a finding is said (its cases
    in order, then its own message and fix), and its examples: the files of a small project in which it must find
    something (flagged), and of one in which it must find nothing (clean), each its path below the app
    (tests/<path> for a test) and its code."""
    read: tuple[str, ...]
    within: Scope
    quantified: Quantified
    sayings: tuple[Saying, ...]
    keep: tuple[Condition, ...] = ()
    exempt: tuple[Condition, ...] = ()
    mode: str = FAIL
    flagged: tuple[tuple[str, str], ...] = ()
    clean: tuple[tuple[str, str], ...] = ()
