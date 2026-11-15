"""The engine: runs rules as data over the facts of a run, read once.

For each file, the app's first and then the tests', and for each rule in order whose scope holds the file, the rule
reads the facts of its kinds in order. A fact is read when it passes every filter the rule keeps by; it is compared
with the rule's targets: under MAY_NOT it is a finding when it matches one (the target it matches is its hit), under
MAY_ONLY when it matches none. A finding the rule's exemptions excuse is dropped. It is said by the first saying whose
condition holds of it, and a saying that keeps its findings once drops one whose attributes it has said already in
that file. A rule in FAIL mode makes violations, one in LIST mode weak findings. So every finding of a file comes
before those of the next, and within a file those of a rule before those of the next.

A rule of reach is worked out over every file first. Under MUST_REACH, a file on its scope's side (the app or the
tests) reaches when one of its kept facts matches a target, or when one of its links that passes the rule's via leads
to a file that reaches, however far; each file of the scope that does not reach is a finding, its file fact the fact
said. Under MUST_BE_REACHED, the links of the roots that pass via reach the declarations they name or the files they
lead to; a declaration or file reached already reaches further through its facts of the spread kinds, however far;
each kept fact of the scope that nothing reached is a finding: by its name, a declaration (and, when the roots must be
another file, by a root other than its own file), and by its steps, a file.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import replace

from xarch.kernel.violations import Violation, Weak
from xarch.modules.rules.application.logic.filters import Question, holds, in_scope, question
from xarch.modules.rules.application.logic.sentences import said, value
from xarch.modules.rules.application.logic.targets import finding, matcher
from xarch.modules.rules.domain.rule import (
    FAIL,
    MAY_NOT,
    MUST_BE_REACHED,
    MUST_REACH,
    Fact,
    Facts,
    Found,
    Read,
    Rule,
    Scope,
)
from xarch.modules.rules.domain.values import Profile

CALLED = "called"
"""The exemption that excuses a reference read as the callee of a call on its line, once for each such call: the call
was said as a call."""


ELSEWHERE = "another-file"
"""The filter of a root that is a file other than the one of the declaration it reaches."""

Reached = dict[tuple[str, ...] | str, set[int]]
"""What the links of a rule of reach reached: each declaration by its name, each file by its steps, with the files
whose links reached it, by their place in the run."""


def run(rules: Iterable[Rule], facts: Facts, profile: Profile) -> list[Violation | Weak]:
    rules = tuple(rules)
    reached = {index: _reach(rule, facts, profile) for index, rule in enumerate(rules)
               if rule.quantifier in (MUST_REACH, MUST_BE_REACHED)}
    found: list[Violation | Weak] = []
    for position, read in enumerate(facts.files):
        for index, rule in enumerate(rules):
            if in_scope(rule.scope, read, facts, profile):
                found += (_unreached(rule, read, position, reached[index], facts, profile) if index in reached
                          else _file(rule, read, facts, profile))
    return found


def _reach(rule: Rule, facts: Facts, profile: Profile) -> Reached:
    side = Scope(rule.scope.files)
    via = (question(rule.via),) if rule.via else ()
    links = {position: [f for kind in rule.links for f in read.facts.get(kind, ())
                        if _all(via, Found(rule, read, f), facts, profile)]
             for position, read in enumerate(facts.files)}
    if rule.quantifier == MUST_REACH:
        keep, match = tuple(question(name) for name in rule.keep), matcher(rule.targets.kind)
        on_side = [(position, read) for position, read in enumerate(facts.files) if in_scope(side, read, facts, profile)]
        reaching = {read.steps for _, read in on_side
                    if any(_all(keep, Found(rule, read, f), facts, profile)
                           and match(rule.targets, Found(rule, read, f), facts, profile) is not None
                           for kind in rule.facts for f in read.facts.get(kind, ()))}
        _spread(reaching, {read.steps: [f.target for f in links[position]] for position, read in on_side})
        return {steps: set() for steps in reaching}
    assert rule.roots is not None
    roots = replace(rule.roots, where=tuple(w for w in rule.roots.where if w != ELSEWHERE))
    found: Reached = {}
    for position, read in enumerate(facts.files):
        if in_scope(roots, read, facts, profile):
            for link in links[position]:
                for key in _points(link):
                    found.setdefault(key, set()).add(position)
    things = [(position, read, fact) for position, read in enumerate(facts.files)
              if in_scope(rule.scope, read, facts, profile) for kind in rule.facts for fact in read.facts.get(kind, ())]
    grown = True
    while grown:
        grown = False
        for position, read, fact in things:
            if _key(read, fact) not in found:
                continue
            for spread in _spread_of(rule, read, fact, position, links):
                for key in _points(spread):
                    if key not in found:
                        found[key] = {position}
                        grown = True
    return found


def _spread(reaching: set[tuple[str, ...]], links: dict[tuple[str, ...], list[tuple[str, ...]]]) -> None:
    """Add to reaching every file that links, however far, to a file that reaches."""
    grown = True
    while grown:
        grown = False
        for steps, linked in links.items():
            if steps not in reaching and any(s in reaching for s in linked):
                reaching.add(steps)
                grown = True


def _spread_of(rule: Rule, read: Read, fact: Fact, position: int, links: dict[int, list[Fact]]) -> list[Fact]:
    """The facts through which a declaration or file reached reaches further: itself, when it is of a kind the rule
    spreads through; else its file's links of those kinds."""
    if fact.kind in rule.spread:
        return [fact]
    return [link for link in links[position] if link.kind in rule.spread]


def _points(fact: Fact) -> tuple[tuple[str, ...] | str, ...] | frozenset[str]:
    """What a link reaches: the declarations it names, else the file it leads to."""
    return fact.names if fact.names else ((fact.target,) if fact.target else ())


def _key(read: Read, fact: Fact) -> tuple[str, ...] | str:
    return read.steps if fact.kind == "file" else (fact.name or "")


def _unreached(rule: Rule, read: Read, position: int, reached: Reached, facts: Facts,
               profile: Profile) -> list[Violation | Weak]:
    keep = tuple(question(name) for name in rule.keep) if rule.quantifier == MUST_BE_REACHED else ()
    exempt = tuple(question(name) for name in rule.exempt)
    elsewhere = rule.roots is not None and ELSEWHERE in rule.roots.where
    subjects = read.facts.get("file", ()) if rule.quantifier == MUST_REACH else [
        f for kind in rule.facts for f in read.facts.get(kind, ())]
    found: list[Violation | Weak] = []
    for fact in subjects:
        candidate = Found(rule, read, fact)
        by = reached.get(_key(read, fact))
        if not _all(keep, candidate, facts, profile) or (by is not None and (not elsewhere or by - {position})):
            continue
        if exempt and _any(exempt, candidate, facts, profile):
            continue
        found.append(_said(rule, candidate, facts, profile))
    return found


def _said(rule: Rule, found: Found, facts: Facts, profile: Profile) -> Violation | Weak:
    saying = next(s for s in rule.sayings if not s.when or holds(s.when, found, facts, profile))
    message, fix = said(saying.message, found, facts, profile), said(saying.fix, found, facts, profile)
    file, line = found.read.file.name, found.fact.line
    return Violation(file, line, message, rule.id, fix) if rule.mode == FAIL else Weak(rule.id, file, line, message, fix)


def _file(rule: Rule, read: Read, facts: Facts, profile: Profile) -> list[Violation | Weak]:
    found: list[Violation | Weak] = []
    seen: set[tuple[int, tuple[str, ...]]] = set()
    calls = Counter((call.line, call.path) for call in read.facts.get("call", ())) if CALLED in rule.exempt else None
    keep = tuple(question(name) for name in rule.keep)
    exempt = tuple(question(name) for name in rule.exempt if name != CALLED)
    match, targets, quantifier = matcher(rule.targets.kind), rule.targets, rule.quantifier
    for kind in rule.facts:
        for fact in read.facts.get(kind, ()):
            candidate = Found(rule, read, fact)
            if not _all(keep, candidate, facts, profile):
                continue
            hit = match(targets, candidate, facts, profile)
            if not finding(quantifier, hit):
                continue
            candidate = Found(rule, read, fact, hit if quantifier == MAY_NOT else None)
            if exempt and _any(exempt, candidate, facts, profile):
                continue
            if calls is not None and fact.kind == "reference" and calls[(fact.line, fact.path)] > 0:
                calls[(fact.line, fact.path)] -= 1
                continue
            index = next(i for i, s in enumerate(rule.sayings) if not s.when or holds(s.when, candidate, facts, profile))
            saying = rule.sayings[index]
            if saying.once:
                key = (index, tuple(value(name, candidate, facts, profile) for name in saying.once))
                if key in seen:
                    continue
                seen.add(key)
            message, fix = said(saying.message, candidate, facts, profile), said(saying.fix, candidate, facts, profile)
            file, line = read.file.name, fact.line
            found.append(Violation(file, line, message, rule.id, fix) if rule.mode == FAIL else
                         Weak(rule.id, file, line, message, fix))
    return found


def _all(questions: tuple[Question, ...], found: Found, facts: Facts, profile: Profile) -> bool:
    for asked in questions:
        if not asked(found, facts, profile):
            return False
    return True


def _any(questions: tuple[Question, ...], found: Found, facts: Facts, profile: Profile) -> bool:
    for asked in questions:
        if asked(found, facts, profile):
            return True
    return False
