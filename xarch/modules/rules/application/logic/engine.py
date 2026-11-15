"""The engine: runs rules as data over the facts of a run, read once.

For each file, the app's first and then the tests', and for each rule in order whose scope holds the file, the rule
reads the facts of its kinds in order. A fact is read when it passes every filter the rule keeps by; it is compared
with the rule's targets: under MAY_NOT it is a finding when it matches one (the target it matches is its hit), under
MAY_ONLY when it matches none, under MUST when it lacks what they say. A finding the rule's exemptions excuse is
dropped. It is said by the first saying whose condition holds of it, and a saying that keeps its findings once drops
one whose attributes it has said already in that file. A rule in FAIL mode makes violations, one in LIST mode weak
findings. So every finding of a file comes before those of the next, and within a file those of a rule before those
of the next.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from xarch.kernel.violations import Violation, Weak
from xarch.modules.rules.application.logic.filters import holds, in_scope
from xarch.modules.rules.application.logic.sentences import said, value
from xarch.modules.rules.application.logic.targets import compared
from xarch.modules.rules.domain.rule import FAIL, Facts, Found, Read, Rule
from xarch.modules.rules.domain.values import Profile

CALLED = "called"
"""The exemption that excuses a reference read as the callee of a call on its line, once for each such call: the call
was said as a call."""


def run(rules: Iterable[Rule], facts: Facts, profile: Profile) -> list[Violation | Weak]:
    rules = tuple(rules)
    found: list[Violation | Weak] = []
    for read in facts.files:
        for rule in rules:
            if in_scope(rule.scope, read, facts, profile):
                found += _file(rule, read, facts, profile)
    return found


def _file(rule: Rule, read: Read, facts: Facts, profile: Profile) -> list[Violation | Weak]:
    found: list[Violation | Weak] = []
    seen: set[tuple[int, tuple[str, ...]]] = set()
    calls = Counter((call.line, call.path) for call in read.facts.get("call", ())) if CALLED in rule.exempt else None
    for kind in rule.facts:
        for fact in read.facts.get(kind, ()):
            candidate = Found(rule, read, fact)
            if not all(holds(name, candidate, facts, profile) for name in rule.keep):
                continue
            finding, hit = compared(rule.quantifier, rule.targets, candidate, facts, profile)
            if not finding:
                continue
            candidate = Found(rule, read, fact, hit)
            if any(holds(name, candidate, facts, profile) for name in rule.exempt if name != CALLED):
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
