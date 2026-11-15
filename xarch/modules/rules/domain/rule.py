"""A check as data: a rule says, for the files in a scope, which facts of a kind it reads, which of them it keeps, what
they must, may only or may not match, which it excuses, how often one finding is said, whether a finding fails the
check or is listed, and how a finding is said. A profile key expands to the rules it means; the engine runs them over
the facts of the source, as the reader recorded them and placement placed them.

Every slot holds a fixed kind of value: a name from a closed list, a part or a tier, a tuple of targets, a sentence
with variables from a closed list. Nothing is an expression: what a filter, a target, a dedupe or a variable means is
the engine's, by its name.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple

from xarch.kernel.logic.placement import Place, Target
from xarch.modules.rules.domain.values import SourceFile

ANY = "*"
"""A scope's part that any file of its files is in: a part, the structure or no part."""
STRUCTURE = ""
"""A scope's part that is the structure: a folder of the layout no part claims."""

APP, TESTS, ALL = "app", "tests", "all"
"""The files a scope reads: the app's, the tests', or both, the app's first."""

MAY_NOT, MAY_ONLY, MUST = "may_not", "may_only", "must"
"""What a kept fact does with the targets: matches none of them, matches one of them, or has what they say."""

FAIL, LIST = "fail", "list"
"""What a finding is: a violation, or a weak finding listed in the enforcement section."""


@dataclass(frozen=True)
class Scope:
    """The files a rule reads: of the app, of the tests or both (files); in a part (part: its name, STRUCTURE for the
    structure, ANY for any); for tests, of a tier (tier: its name, "" for any, or none at all when part names a part
    the test mirrors); and the named filters a file passes besides (where)."""
    files: str = APP
    part: str = ANY
    tier: str = ""
    where: tuple[str, ...] = ()


@dataclass(frozen=True)
class Targets:
    """What a kept fact is compared with: a kind of target from the engine's closed list, and its values: places a
    part may import, dotted names, words such as package names or part names."""
    kind: str
    places: tuple[Target, ...] = ()
    names: tuple[tuple[str, ...], ...] = ()
    words: tuple[str, ...] = ()


EXISTING = Targets("existing")
"""The targets every fact matches: under MAY_NOT, a rule whose kept facts are findings by being there."""


@dataclass(frozen=True)
class Saying:
    """How a finding is said, when the named condition holds of it ("" always): the message and the fix, each a
    sentence with `{variable}`s from the engine's closed list, and the attributes by which a file's findings said
    this way are kept once (empty: every one is said)."""
    message: str
    fix: str
    when: str = ""
    once: tuple[str, ...] = ()


@dataclass(frozen=True)
class Rule:
    """One sentence of a check: its rule id; the scope of files it reads; the kinds of fact it reads of each, in
    order; the named filters a fact must pass to be read (keep); what it does with the targets (quantifier); the named
    filters that excuse a fact (exempt); what a finding is (mode); the sayings, the first whose condition holds being
    the one said; and the key of the profile it expands from, `{key}` in a saying, with the part it names, if any."""
    id: str
    scope: Scope
    facts: tuple[str, ...]
    quantifier: str
    targets: Targets
    sayings: tuple[Saying, ...]
    keep: tuple[str, ...] = ()
    exempt: tuple[str, ...] = ()
    mode: str = FAIL
    key: str = ""
    part: str = ""


class Fact(NamedTuple):
    """One thing a file says, as a rule reads it: its kind, the line it is on (0: the file as a whole), the dotted path
    it names (what an import imports, the name a use reaches, the callee of a call), a name it carries (a name an
    import takes, a method called, a parameter), the traits the reader recorded of it by name (relative, standard,
    held, receiver, annotated), how many steps of its path the import binding it bound, and, for an import into the
    app or the tests, the file or package it reaches below that root and where that sits. A run holds a fact for
    every import, name read and call of every file, so a fact is a named tuple, which is made several times faster
    than a frozen dataclass and is as immutable."""
    kind: str
    line: int
    path: tuple[str, ...] = ()
    name: str | None = None
    traits: frozenset[str] = frozenset()
    bound: int = 0
    target: tuple[str, ...] = ()
    at: Place | None = None
    text: str = ""


@dataclass(frozen=True)
class Read:
    """A file as the rules read it: the file as parsed; its steps below its root as the language names it, and
    whether it is the file that stands for its folder; whether it is a test file (of the tests root) or the app's;
    where it sits (place: in the app, None when it is a test or ungoverned; tier, instance, own folder, subject parts
    and kind for a test); and its facts by kind, each in the order the file says them."""
    file: SourceFile
    steps: tuple[str, ...]
    package: bool
    test: bool
    place: Place | None = None
    tier: str = ""
    instance: str | None = None
    own: tuple[str, ...] = ()
    mirrors: tuple[str, ...] = ()
    is_test: bool = False
    is_fake: bool = False
    facts: dict[str, tuple[Fact, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class Facts:
    """The facts of a run, read once: every file read, the app's first, then the tests'; the root package of the app
    and of the tests; the steps of every file of each, so that an import of a name that is a file is read as the
    file; and those of the test files (the files below the tests root whose name the profile's test files match)."""
    files: tuple[Read, ...]
    root: str
    tests_root: str = ""
    known: frozenset[tuple[str, ...]] = frozenset()
    known_tests: frozenset[tuple[str, ...]] = frozenset()
    test_files: frozenset[tuple[str, ...]] = frozenset()


@dataclass(frozen=True)
class Defined:
    """What the app defines, as the facts derived from it read it: the root package; where the file of each class it
    defines at the top level of a file sits, by the class's dotted path (the root first); and the names each file,
    by its steps below the root, binds to a function alone."""
    root: str
    classes: dict[tuple[str, ...], Place | None]
    functions: dict[tuple[str, ...], frozenset[str]]


class Found(NamedTuple):
    """A fact a rule reads in a file, and the target it matched (hit: None when it matched none, or before it is
    compared): what a filter, a condition and a variable of a saying are worked out from; a named tuple, made once
    for each fact a rule reads (see Fact)."""
    rule: Rule
    read: Read
    fact: Fact
    hit: tuple[str, ...] | None = None
