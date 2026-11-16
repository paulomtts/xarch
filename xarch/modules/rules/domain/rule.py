"""A check as data: a rule says, for the files in a scope, which facts of a kind it reads, which of them it keeps, what
they must, may only or may not match, which it excuses, how often one finding is said, whether a finding fails the
check or is listed, and how a finding is said. A profile key expands to the rules it means, and a profile may write
rules of its own; the engine runs them over the facts of the source, as the reader recorded them and placement placed
them.

Every slot holds a word of the vocabulary (see vocabulary), a part or a tier, targets, or a sentence with variables of
the vocabulary. Nothing is an expression: what a filter, a target or a variable means is the engine's, by its name. A
rule refuses to be made with a word that does not exist, or that does not apply to what it reads, by RuleRefused,
every problem at once, each named by the slot of the profile's syntax it is in.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import get_close_matches
from string import Formatter
from typing import NamedTuple

from xarch.kernel.placement import Place
from xarch.modules.rules.domain.errors import RuleRefused
from xarch.modules.rules.domain.values import SourceFile
from xarch.modules.rules.domain.vocabulary import (
    APP_SIDE,
    FILE,
    FILTERS,
    FOLDER,
    HIT,
    KEY,
    KEY_OF_RULE,
    KIND,
    KINDS,
    PART_KEYS,
    QUANTIFIERS,
    RENAMED_VARIABLES,
    SCOPE_PART,
    TARGETS,
    TESTS_SIDE,
    VALUES,
    VARIABLES,
    Kind,
)
from xarch.profile_values.checks import ALL, APP, TESTS, Condition, Saying, Scope
from xarch.profile_values.placement import Target

MAY_NOT, MAY_ONLY = "may_not", "may_only"
"""What a kept fact does with the targets: matches none of them, or matches one of them."""
MUST_REACH, MUST_BE_REACHED = "must_reach", "must_be_reached"
"""What a file or a declaration does through links: a file of the scope reaches a target, by one of its own facts or
through the files its links lead to, however far; a declaration of the scope is reached from a root, by the link of a
root, or of a declaration reached already when the rule spreads through it."""

FAIL, LIST = "fail", "list"
"""What a finding is: a violation, or a weak finding listed in the enforcement section."""

EXIST = "exist"
"""The kind of target every fact matches."""

NEAREST = 3
"""How many names a refusal offers for one that does not exist."""

_KINDS = {kind.name: kind for kind in KINDS}
_FILTERS = {word.name: word for word in FILTERS}
_TARGETS = {kind.name: kind for kind in TARGETS}
_VARIABLES = {variable.name: variable for variable in VARIABLES}
_QUANTIFIERS = {quantifier.name for quantifier in QUANTIFIERS}
_REACH = tuple(quantifier.name for quantifier in QUANTIFIERS if quantifier.reaches)


@dataclass(frozen=True)
class Match:
    """One target of a rule: a kind of target and its values, places a part may import, dotted names, or words such
    as patterns and part names. A fact is compared with each target of its rule in turn; the first it matches is its
    hit."""
    kind: str
    places: tuple[Target, ...] = ()
    names: tuple[tuple[str, ...], ...] = ()
    words: tuple[str, ...] = ()

    @property
    def values(self) -> int:
        return len(self.places) + len(self.names) + len(self.words)


EXISTING = (Match(EXIST),)
"""The targets every fact matches: under MAY_NOT, a rule whose kept facts are findings by being there."""


@dataclass(frozen=True)
class Rule:
    """One sentence of a check: its rule id; the scope of files it reads; the kinds of fact it reads of each, in
    order; the conditions a fact must pass to be read (keep); what it does with the targets (quantifier); the conditions
    of which any one excuses a fact (exempt); what a finding is (mode); the sayings, the first whose conditions hold
    being the one said; and the key of the profile it expands from, `{key}` in a saying.

    A rule of reach also says how it reaches: the kinds of fact that link a file to what it reaches (links) and the
    conditions a link passes (via); for MUST_BE_REACHED, the files the reach starts from (roots), the kinds of fact
    through which a declaration reached already reaches further (spread), and whether a declaration is reached only
    from a root other than its own file (elsewhere). A link reaches the declarations it names (the names it mentions,
    for a fact that has them) or the file it leads to (what it reaches).

    A rule that names a word of no slot, or one that does not apply to what the slot reads, is refused (RuleRefused),
    with every problem at once."""
    id: str
    scope: Scope
    facts: tuple[str, ...]
    quantifier: str
    targets: tuple[Match, ...]
    sayings: tuple[Saying, ...]
    keep: tuple[Condition, ...] = ()
    exempt: tuple[Condition, ...] = ()
    mode: str = FAIL
    key: str = ""
    links: tuple[str, ...] = ()
    via: tuple[Condition, ...] = ()
    roots: Scope | None = None
    spread: tuple[str, ...] = ()
    elsewhere: bool = False

    def __post_init__(self) -> None:
        found = self.problems()
        if found:
            raise RuleRefused(self.id, tuple(found))

    @property
    def said_kinds(self) -> tuple[str, ...]:
        """The kinds of fact a finding of the rule is: a file's, for a rule a file must reach by; else those it reads."""
        return ("file",) if self.quantifier == MUST_REACH else self.facts

    @property
    def needs(self) -> tuple[str, ...]:
        """The facts of the source (FACTS of capabilities) the rule reads: those of its kinds of fact, and those of the
        fields its words read, in order."""
        kinds = [_KINDS[name] for name in (*self.facts, *self.links, *self.spread, *self.said_kinds) if name in _KINDS]
        words = [*(_FILTERS.get(c.name) for c in self.conditions), *(_TARGETS.get(m.kind) for m in self.targets),
                 *(_VARIABLES.get(name) for name in self.variables)]
        found = [need for kind in kinds for need in kind.needs]
        found += [need for kind in kinds for word in words if word is not None for name in word.reads
                  if kind.carries(name) for need in kind.field_needs.get(name, ())]
        return tuple(dict.fromkeys(found))

    def problems(self) -> list[str]:
        """What is wrong with the rule, each problem as `<slot>: <what>, <what to write>`."""
        found: list[str] = []
        side = {APP: APP_SIDE, TESTS: TESTS_SIDE}.get(self.scope.files, "")
        found += _scope("in", self.scope)
        known = [_KINDS[name] for name in self.facts if name in _KINDS]
        found += [f"read: no kind of fact is named {name!r}{_nearest(name, _KINDS)}" for name in self.facts
                  if name not in _KINDS]
        if not self.facts:
            found.append(f"read: names no kind of fact: write one or more of {_listed(_KINDS)}")
        found += [f"read: {kind.name} is a fact of the {kind.side} only, and the scope reads the files of the "
                  f"{self.scope.files}: write `in: {{files: {kind.side}}}`" for kind in known
                  if kind.side and side and side != kind.side]
        found += _conditions("keep", self.keep, known, side, self.quantifier, "read")
        found += _quantified(self, known)
        said = [_KINDS[name] for name in self.said_kinds if name in _KINDS]
        found += _conditions("except", self.exempt, said, side, self.quantifier)
        if self.mode not in (FAIL, LIST):
            found.append(f"mode: is {self.mode!r}: write {FAIL} (a finding fails the check) or {LIST} (it is listed as "
                         "weak and fails only `check --strict`)")
        found += _sayings(self, said, side)
        return found

    @property
    def conditions(self) -> tuple[Condition, ...]:
        """Every filter the rule is written with, in every slot that takes one."""
        return (*self.scope.where, *self.keep, *self.exempt, *self.via, *(self.roots.where if self.roots else ()),
                *(c for s in self.sayings for c in s.when))

    @property
    def variables(self) -> tuple[str, ...]:
        """Every variable the rule is written with: in a message or a fix of its sayings, or by which one is said
        once."""
        return (*(name for s in self.sayings for text in (s.message, s.fix) for _, name, _, _ in Formatter().parse(text)
                  if name), *(name for s in self.sayings for name in s.once))


@dataclass(frozen=True)
class OwnCheck:
    """A check the profile writes itself: its rule, and its examples: the files of a small project in which the rule
    must find something (flagged), and of one in which it must find nothing (clean), each by its path below the app
    (tests/<path> for a test) with what it says."""
    rule: Rule
    flagged: tuple[tuple[str, str], ...] = ()
    clean: tuple[tuple[str, str], ...] = ()


def _nearest(name: str, known: dict) -> str:
    close = get_close_matches(name, list(known), n=NEAREST, cutoff=0.5)
    return f": did you mean {' or '.join(close)}?" if close else f": write one of {_listed(known)}"


def _nearest_variable(name: str) -> str:
    if name in RENAMED_VARIABLES:
        return f": it is called {{{RENAMED_VARIABLES[name]}}} now: write that"
    return _nearest(name, _VARIABLES)


def _listed(known: dict) -> str:
    return ", ".join(known)


def _scope(slot: str, scope: Scope) -> list[str]:
    problems: list[str] = []
    if scope.files not in (APP, TESTS, ALL):
        problems.append(f"{slot}.files: is {scope.files!r}: write {APP}, {TESTS} or {ALL}")
    side = {APP: APP_SIDE, TESTS: TESTS_SIDE}.get(scope.files, "")
    for condition in scope.where:
        word = _FILTERS.get(condition.name)
        if word is None:
            problems.append(f"{slot}.where: no filter is named {condition.name!r}{_nearest(condition.name, _FILTERS)}")
        elif word.about != FILE:
            problems.append(f"{slot}.where: {condition.name} is a filter about the {word.about}, and `where` takes "
                            f"filters about the file: move it to `keep` or `except`")
        else:
            problems += _value(f"{slot}.where", condition, word.value)
            problems += _sided(f"{slot}.where", condition.name, word.side, side)
    return problems


def _sided(slot: str, name: str, wanted: str, side: str, strict: bool = False) -> list[str]:
    """A word of one side in a scope of the other is refused; a variable of one side also in a scope of both, where
    it would print nothing for the files of the other."""
    if wanted and side != wanted and (strict or side):
        return [f"{slot}: {name} applies only to the files of the {wanted}: write it in a check whose scope reads "
                f"them (`in: {{files: {wanted}}}`)"]
    return []


def _value(slot: str, condition: Condition, wanted: str) -> list[str]:
    name, value = condition.name, condition.value
    if not wanted:
        return [f"{slot}: {name} takes no value: write it alone"] if value else []
    if not value:
        return [f"{slot}: {name} needs a value ({wanted}): write {{{name}: <{wanted}>}}"]
    if wanted == FOLDER and ("*" in value or value.startswith("/") or ".." in value.split("/")):
        return [f"{slot}: {name} {value!r}: write a folder below the root, such as fakes or units/docs"]
    if wanted == KIND and value not in _KINDS:
        return [f"{slot}: {name} {value!r}: no kind of fact is named so{_nearest(value, _KINDS)}"]
    if wanted == KEY and value not in PART_KEYS:
        return [f"{slot}: {name} {value!r}: write one of {', '.join(PART_KEYS)}"]
    return []


def _conditions(slot: str, conditions: tuple[Condition, ...], kinds: list[Kind], side: str,
                quantifier: str, read: str = "") -> list[str]:
    """What is wrong with the conditions of a slot over the kinds it reads; a slot that keeps only what passes them
    (read: the slot that names those kinds) also refuses a filter that holds of no fact of one of the kinds, which it
    would drop whole."""
    problems: list[str] = []
    for condition in conditions:
        word = _FILTERS.get(condition.name)
        if word is None:
            problems.append(f"{slot}: no filter is named {condition.name!r}{_nearest(condition.name, _FILTERS)}")
            continue
        problems += _value(slot, condition, word.value)
        problems += _sided(slot, condition.name, word.side, side)
        if kinds and not any(word.applies_to(kind) for kind in kinds):
            problems.append(f"{slot}: {condition.name} does not apply to {_and(k.name for k in kinds)}: it reads "
                            f"{_or(word.reads)}, which {_carried(kinds)}; it applies to "
                            f"{_and(k.name for k in KINDS if word.applies_to(k))}")
        elif read and not condition.negated and any(not word.applies_to(kind) for kind in kinds):
            dropped = [kind.name for kind in kinds if not word.applies_to(kind)]
            them = "it" if len(dropped) == 1 else "them"
            problems.append(f"{slot}: {condition.name} drops every {_and(dropped)}, which never carries "
                            f"{_or(word.reads)}: read {them} in another check, or drop {them} from `{read}`")
        if word.needs == HIT and quantifier != MAY_NOT:
            problems.append(f"{slot}: {condition.name} reads the target a fact matched, which only a check under "
                            f"{MAY_NOT} has")
    return problems


def _carried(kinds: list[Kind]) -> str:
    return "it does not carry" if len(kinds) == 1 else "none of them carries"


def _and(items) -> str:
    items = list(items)
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}" if items else "nothing"


def _or(items) -> str:
    items = list(items)
    return " or ".join(items) if items else "nothing"


def _quantified(rule: Rule, kinds: list[Kind]) -> list[str]:
    quantifier, problems = rule.quantifier, []
    if quantifier not in _QUANTIFIERS:
        return [f"quantifier: no quantifier is named {quantifier!r}: write one of {', '.join(sorted(_QUANTIFIERS))}"]
    slot = f"{quantifier}.targets" if quantifier == MUST_REACH else quantifier
    if quantifier == MUST_BE_REACHED:
        if rule.targets != EXISTING:
            problems.append(f"{quantifier}: takes no targets: what must be reached is what the check keeps")
    else:
        problems += _targets(slot, rule, kinds)
    if quantifier not in _REACH:
        extra = [name for name, on in (("through", rule.links), ("through_only", rule.via), ("from", rule.roots),
                                       ("then_through", rule.spread), ("by_another_file", rule.elsewhere)) if on]
        problems += [f"{name}: only a check under {MUST_REACH} or {MUST_BE_REACHED} reaches through links: drop it"
                     for name in extra]
        return problems
    problems += _links(f"{quantifier}.through", rule.links, "reaches" if quantifier == MUST_REACH else "")
    linked = [_KINDS[name] for name in rule.links if name in _KINDS]
    problems += _conditions(f"{quantifier}.through_only", rule.via, linked, "", quantifier, f"{quantifier}.through")
    if quantifier == MUST_REACH:
        problems += [f"{quantifier}.{name}: only a check under {MUST_BE_REACHED} has it: drop it"
                     for name, on in (("from", rule.roots), ("then_through", rule.spread),
                                      ("by_another_file", rule.elsewhere)) if on]
        return problems
    if not rule.links:
        problems.append(f"{quantifier}.through: names no kind of fact: write the kinds that link a root onwards, "
                        "such as names-mentioned or import-into-app")
    if rule.roots is None:
        problems.append(f"{quantifier}.from: is missing: write the files the reach starts from, as `in` writes a "
                        "scope")
    else:
        problems += _scope(f"{quantifier}.from", rule.roots)
    problems += _links(f"{quantifier}.then_through", rule.spread, "")
    problems += [f"read: under {quantifier}, a fact is reached by its name, which {kind.name} does not carry: read "
                 "file, or a kind that carries a name" for kind in kinds if kind.name != "file"
                 and "name" not in kind.fields]
    return problems


def _links(slot: str, names: tuple[str, ...], wanted: str) -> list[str]:
    problems: list[str] = []
    for name in names:
        kind = _KINDS.get(name)
        if kind is None:
            problems.append(f"{slot}: no kind of fact is named {name!r}{_nearest(name, _KINDS)}")
        elif not (kind.carries(wanted) if wanted else kind.links):
            leads = [k.name for k in KINDS if (k.carries(wanted) if wanted else k.links)]
            problems.append(f"{slot}: {name} leads nowhere: write a kind that leads to a file or to names, one of "
                            f"{', '.join(leads)}")
    return problems


def _targets(slot: str, rule: Rule, kinds: list[Kind]) -> list[str]:
    problems: list[str] = []
    if not rule.targets:
        return [f"{slot}: names no target: write one, such as exist, {{path: [<dotted name>]}} or {{part: [<part>]}}"]
    known = [(match, _TARGETS[match.kind]) for match in rule.targets if match.kind in _TARGETS]
    problems += [f"{slot}: no kind of target is named {match.kind!r}{_nearest(match.kind, _TARGETS)}"
                 for match in rule.targets if match.kind not in _TARGETS]
    if any(match.kind == EXIST for match in rule.targets):
        if len(rule.targets) > 1:
            problems.append(f"{slot}: exist matches every fact: write it alone")
        if rule.quantifier != MAY_NOT:
            problems.append(f"{slot}: exist matches every fact, so nothing could be a finding under "
                            f"{rule.quantifier}: write it under {MAY_NOT}, or name what to match")
    side = {APP: APP_SIDE, TESTS: TESTS_SIDE}.get(rule.scope.files, "")
    for match, word in known:
        if word.values and not match.values and rule.quantifier != MAY_ONLY:
            problems.append(f"{slot}: {match.kind} lists no values, so it matches nothing: write its values "
                            f"({word.values}) as {{{match.kind}: [...]}}")
        if not word.values and match.values:
            problems.append(f"{slot}: {match.kind} takes no values: write it alone")
        problems += _sided(slot, match.kind, word.side, side)
        if kinds and not any(word.applies_to(kind) for kind in kinds):
            problems.append(f"{slot}: {match.kind} does not apply to {_and(k.name for k in kinds)}: it compares "
                            f"{_or(word.reads)}; it applies to {_and(k.name for k in KINDS if word.applies_to(k))}")
    for kind in kinds:
        if known and not any(word.applies_to(kind) for _, word in known):
            outcome = {MAY_NOT: "never be a finding", MAY_ONLY: "always be a finding"}.get(
                rule.quantifier, "never reach a target")
            problems.append(f"{slot}: no target applies to {kind.name}, so a fact of it would {outcome}: add a target "
                            "that compares what it carries, or drop it from `read`")
    return problems


def _sayings(rule: Rule, kinds: list[Kind], side: str) -> list[str]:
    problems: list[str] = []
    if not rule.sayings:
        return ["message: is missing: every check says what it found, and fix what to do about it"]
    caught: set[str] = set()
    for index, saying in enumerate(rule.sayings):
        last = index == len(rule.sayings) - 1
        slot = "" if last else f"cases[{index + 1}]."
        if last and saying.when:
            problems.append("cases: the message and fix of the check itself hold when no case does, and take no "
                            "`when`: move it into a case")
        if not last and not saying.when:
            problems.append(f"{slot}when: is missing: a case is said when its filters hold; write them, or make it "
                            "the check's own message")
        problems += _conditions(f"{slot}when", saying.when, kinds, side, rule.quantifier)
        only = {c.value for c in saying.when if c.name == "of-kind" and not c.negated}
        held = [kind for kind in kinds if kind.name not in caught and (not only or kind.name in only)]
        if len(saying.when) == 1 and only:
            caught |= only
        guards = {c.name for c in (*rule.keep, *saying.when) if not c.negated}
        for part, text in (("message", saying.message), ("fix", saying.fix)):
            problems += _sentence(f"{slot}{part}", text, rule, held, side, guards)
        for name in saying.once:
            variable = _VARIABLES.get(name)
            if variable is None:
                problems.append(f"{slot}once_per: no variable is named {name!r}{_nearest_variable(name)}")
            else:
                problems += _variable(f"{slot}once_per", variable, rule, held, side, guards)
    return problems


def _sentence(slot: str, text: str, rule: Rule, kinds: list[Kind], side: str, guards: set[str]) -> list[str]:
    if not text.strip():
        return [f"{slot}: is empty: say {'what was found' if slot.endswith('message') else 'what to do about it'}"]
    try:
        parsed = list(Formatter().parse(text))
    except ValueError as e:
        return [f"{slot}: {e}: write each variable as {{<name>}}, and a brace of the text as {{{{ or }}}}"]
    problems: list[str] = []
    for _, name, spec, conversion in parsed:
        if name is None:
            continue
        variable = _VARIABLES.get(name)
        if not name or spec or conversion or variable is None:
            problems.append(f"{slot}: {{{name}{f'!{conversion}' if conversion else ''}{f':{spec}' if spec else ''}}} "
                            f"is no variable{_nearest_variable(name) if name else ''}")
            continue
        problems += _variable(slot, variable, rule, kinds, side, guards)
    return problems


def _variable(slot: str, variable, rule: Rule, kinds: list[Kind], side: str, guards: set[str]) -> list[str]:
    name, problems = variable.name, []
    problems += _sided(slot, f"{{{name}}}", variable.side, side, strict=True)
    missing = [kind.name for kind in kinds if not variable.applies_to(kind)]
    if missing:
        reads = f"it reads {_or(variable.reads)}; " if variable.reads else ""
        problems.append(f"{slot}: {{{name}}} prints nothing for {_and(missing)}: {reads}it applies to "
                        f"{_and(k.name for k in KINDS if variable.applies_to(k))}")
    for kind in kinds:
        guard = variable.needs_field(kind) if variable.applies_to(kind) else ""
        if guard and guard not in guards:
            problems.append(f"{slot}: {{{name}}} prints something for {kind.name} only when {guard} holds: keep it "
                            f"(`keep: [{guard}]`), or say it in a case `when: [{guard}]`")
    if variable.needs == HIT and rule.quantifier != MAY_NOT:
        problems.append(f"{slot}: {{{name}}} is the target a fact matched, which only a check under {MAY_NOT} has")
    if variable.needs == KEY_OF_RULE and not rule.key:
        problems.append(f"{slot}: {{{name}}} is the key the check comes from, and this one has none")
    if variable.needs == SCOPE_PART and not rule.scope.named_part:
        problems.append(f"{slot}: {{{name}}} is the part the scope names, and this scope names none: write "
                        "`in: {part: <part>}`")
    if variable.needs == VALUES and not any(match.values for match in rule.targets):
        problems.append(f"{slot}: {{{name}}} prints the values of the targets, and no target of this check lists any")
    return problems


class Fact(NamedTuple):
    """One thing a file says, as a rule reads it: its kind, the line it is on (0: the file as a whole), the dotted path
    it names (what an import imports, the name a use reaches, the callee of a call), a name it carries (a name an
    import takes, a method called, a parameter), the traits the reader recorded of it by name (relative, standard,
    held, receiver, annotated-callable), how many steps of its path the import binding it bound, for an import into
    the app or the tests, the file or package it reaches below that root and where that sits, a text it says, and the
    names it mentions (a class's or a file's). A run holds a fact for every import, name read and call of every file,
    so a fact is a named tuple, which is made several times faster than a frozen dataclass and is as immutable."""
    kind: str
    line: int
    path: tuple[str, ...] = ()
    name: str | None = None
    traits: frozenset[str] = frozenset()
    bound: int = 0
    target: tuple[str, ...] = ()
    at: Place | None = None
    text: str = ""
    names: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Read:
    """A file as the rules read it: the file as parsed; its steps below its root as the language names it, and
    whether it is the file that stands for its folder; in_tests, whether it lies below the tests root rather than the
    app's; where it sits (place: in the app, None when it is below the tests root or ungoverned); its tier (a test's
    own, or for a file of the app the tier whose tests cover its part, "" for none); for a file below the tests root,
    its instance, own folder and the parts it mirrors, is_test, whether its name is a test file's, and whether it is a
    fake; and its facts by kind, each in the order the file says them."""
    file: SourceFile
    steps: tuple[str, ...]
    package: bool
    in_tests: bool
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
    file; those of the test files (the files below the tests root whose name the profile's test files match); and the
    tier whose tests cover each file of the app, by its steps (a file of a part no tier tests is not held)."""
    files: tuple[Read, ...]
    root: str
    tests_root: str = ""
    known: frozenset[tuple[str, ...]] = frozenset()
    known_tests: frozenset[tuple[str, ...]] = frozenset()
    test_files: frozenset[tuple[str, ...]] = frozenset()
    tested_by: dict[tuple[str, ...], str] = field(default_factory=dict)


@dataclass(frozen=True)
class Defined:
    """What the app defines, as the facts derived from it read it: the root package; where the file of each class it
    defines at the top level of a file sits, by the class's dotted path (the root first); the names each file, by its
    steps below the root, binds to a function alone; and its classes that are exceptions, as (their file's steps,
    their name)."""
    root: str
    classes: dict[tuple[str, ...], Place | None]
    functions: dict[tuple[str, ...], frozenset[str]]
    exceptions: frozenset[tuple[tuple[str, ...], str]] = frozenset()


class Found(NamedTuple):
    """A fact a rule reads in a file, and the target it matched (hit: None when it matched none, or before it is
    compared): what a filter, a condition and a variable of a saying are worked out from; a named tuple, made once
    for each fact a rule reads (see Fact)."""
    rule: Rule
    read: Read
    fact: Fact
    hit: tuple[str, ...] | None = None
