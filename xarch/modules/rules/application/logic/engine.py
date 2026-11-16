"""The engine: runs rules as data over the facts of a run, read once.

For each file, the app's first and then the tests', and for each rule in order whose scope holds the file, the rule
reads the facts of its kinds in order. A fact is read when it passes every condition the rule keeps by; it is compared
with the rule's targets: under MAY_NOT it is a finding when it matches one (the target it matches is its hit), under
MAY_ONLY when it matches none. A finding any of the rule's exemptions excuses is dropped. It is said by the first
saying whose conditions hold of it, and a saying that keeps its findings once drops one whose variables it has said
already in that file. A rule in FAIL mode makes violations, one in LIST mode weak findings. So every finding of a file
comes before those of the next, and within a file those of a rule before those of the next.

A rule of reach is worked out over every file first. Under MUST_REACH, a file on its scope's side (the app or the
tests) reaches when one of its kept facts matches a target, or when one of its links that passes the rule's via leads
to a file that reaches, however far; each file of the scope that does not reach is a finding, its file fact the fact
said. Under MUST_BE_REACHED, the links of the roots that pass via reach the declarations they name or the files they
lead to; a declaration or file reached already reaches further through its facts of the spread kinds, however far;
each kept fact of the scope that nothing reached is a finding: by its name, a declaration (and, for a rule that is
reached only from elsewhere, by a root other than its own file), and by its steps, a file.

How many facts a rule reads at all is counted apart (read): a rule that reads none passes for want of anything to
check.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import RULES, Violation, Weak
from xarch.modules.rules.application.logic.facts import reach_scopes
from xarch.modules.rules.application.logic.filters import Question, in_scope, question
from xarch.modules.rules.application.logic.sentences import said, value
from xarch.modules.rules.application.logic.targets import finding, matched
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
)
from xarch.modules.rules.domain.values import Profile

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


def read(rule: Rule, facts: Facts, profile: Profile) -> int:
    """How many facts the rule reads: the files of its scope, for a rule a file must reach by; else the facts of its
    kinds in the files of its scope that pass what it keeps."""
    keep = _questions(rule.keep)
    count = 0
    for file in facts.files:
        if not in_scope(rule.scope, file, facts, profile):
            continue
        if rule.quantifier == MUST_REACH:
            count += 1
            continue
        count += sum(1 for kind in rule.facts for fact in file.facts.get(kind, ())
                     if _all(keep, Found(rule, file, fact), facts, profile))
    return count


def _questions(conditions) -> tuple[Question, ...]:
    return tuple(question(condition) for condition in conditions)


def _reach(rule: Rule, facts: Facts, profile: Profile) -> Reached:
    side, roots = reach_scopes(rule)
    via = _questions(rule.via)
    links = {position: [f for kind in rule.links for f in read.facts.get(kind, ())
                        if _all(via, Found(rule, read, f), facts, profile)]
             for position, read in enumerate(facts.files)}
    if rule.quantifier == MUST_REACH:
        assert side is not None
        keep = _questions(rule.keep)
        on_side = [(position, read) for position, read in enumerate(facts.files) if in_scope(side, read, facts, profile)]
        reaching = {read.steps for _, read in on_side
                    if any(_all(keep, Found(rule, read, f), facts, profile)
                           and matched(rule.targets, Found(rule, read, f), facts, profile) is not None
                           for kind in rule.facts for f in read.facts.get(kind, ()))}
        _spread(reaching, {read.steps: [f.target for f in links[position]] for position, read in on_side})
        return {steps: set() for steps in reaching}
    assert roots is not None
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
            for spread in _spread_of(rule, fact, position, links):
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


def _spread_of(rule: Rule, fact: Fact, position: int, links: dict[int, list[Fact]]) -> list[Fact]:
    """The facts through which a declaration or file reached reaches further: itself, when it is of a kind the rule
    spreads through; else its file's links of those kinds."""
    if fact.kind in rule.spread:
        return [fact]
    return [link for link in links[position] if link.kind in rule.spread]


def _points(fact: Fact) -> tuple[tuple[str, ...] | str, ...] | frozenset[str]:
    """What a link reaches: the declarations it names, else the file it leads to."""
    return fact.names if fact.names else ((fact.target,) if fact.target else ())


def _key(read: Read, fact: Fact) -> tuple[str, ...] | str:
    """What a fact is reached by: a file by its steps, a declaration by its name."""
    return read.steps if fact.kind == "file" else (fact.name or "")


def _unreached(rule: Rule, read: Read, position: int, reached: Reached, facts: Facts,
               profile: Profile) -> list[Violation | Weak]:
    keep = _questions(rule.keep) if rule.quantifier == MUST_BE_REACHED else ()
    exempt = _questions(rule.exempt)
    subjects = read.facts.get("file", ()) if rule.quantifier == MUST_REACH else [
        f for kind in rule.facts for f in read.facts.get(kind, ())]
    found: list[Violation | Weak] = []
    for fact in subjects:
        candidate = Found(rule, read, fact)
        by = reached.get(_key(read, fact))
        if not _all(keep, candidate, facts, profile) or (by is not None and (not rule.elsewhere or by - {position})):
            continue
        if exempt and _any(exempt, candidate, facts, profile):
            continue
        found.append(_said(rule, _saying(rule, candidate, facts, profile)[1], candidate, facts, profile))
    return found


def _saying(rule: Rule, found: Found, facts: Facts, profile: Profile):
    """The first saying of the rule whose conditions all hold of the finding, and where it is in the rule's sayings;
    the last holds always."""
    for index, saying in enumerate(rule.sayings):
        if _all(_questions(saying.when), found, facts, profile):
            return index, saying
    return len(rule.sayings) - 1, rule.sayings[-1]


def _said(rule: Rule, saying, found: Found, facts: Facts, profile: Profile) -> Violation | Weak:
    message, fix = said(saying.message, found, facts, profile), said(saying.fix, found, facts, profile)
    file, line = found.read.file.name, found.fact.line
    if rule.mode != FAIL:
        return Weak(rule.id, file, line, message, fix)
    return Violation(file, line, message, rule.id, fix, rule.id not in RULES)


def _file(rule: Rule, read: Read, facts: Facts, profile: Profile) -> list[Violation | Weak]:
    found: list[Violation | Weak] = []
    seen: set[tuple[int, tuple[str, ...]]] = set()
    keep, exempt = _questions(rule.keep), _questions(rule.exempt)
    targets, quantifier = rule.targets, rule.quantifier
    for kind in rule.facts:
        for fact in read.facts.get(kind, ()):
            candidate = Found(rule, read, fact)
            if not _all(keep, candidate, facts, profile):
                continue
            hit = matched(targets, candidate, facts, profile)
            if not finding(quantifier, hit):
                continue
            candidate = Found(rule, read, fact, hit if quantifier == MAY_NOT else None)
            if exempt and _any(exempt, candidate, facts, profile):
                continue
            index, saying = _saying(rule, candidate, facts, profile)
            if saying.once:
                key = (index, tuple(value(name, candidate, facts, profile) for name in saying.once))
                if key in seen:
                    continue
                seen.add(key)
            found.append(_said(rule, saying, candidate, facts, profile))
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
