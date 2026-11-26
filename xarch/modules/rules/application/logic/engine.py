"""The engine: runs rules as data over the facts of a run, read once.

For each file, the app's first and then the tests', and for each rule in order whose scope holds the file, the rule
reads the facts of its kinds in order. A fact is read when it passes every condition the rule keeps by; it is compared
with the rule's targets: under MAY_NOT it is a finding when it matches one (the target it matches is its hit), under
MAY_ONLY when it matches none. A finding any of the rule's exemptions excuses is dropped. It is said by the first
saying whose conditions hold of it, and a saying that keeps its findings once drops one whose variables it has said
already in that file; one that lists variables per line says the findings of one line that differ only in those
variables as one, the first, each such variable written as its values in the order found, joined by `, ` (a value
found again written once). A rule in FAIL mode makes violations, one in LIST mode weak findings. So every finding of a file
comes before those of the next, and within a file those of a rule before those of the next.

A rule of reach is worked out over every file first. Under MUST_REACH, a file on its scope's side (the app or the
tests) reaches when one of its kept facts matches a target, or when one of its links that passes the rule's via leads
to a file that reaches, however far; each file of the scope that does not reach is a finding, its file fact the fact
said. Under MUST_BE_REACHED, the links of the roots that pass via reach the declarations they name or the files they
lead to; a declaration or file reached already reaches further through its facts of the spread kinds, however far;
each kept fact of the scope that nothing reached is a finding: by its name, a declaration (and, for a rule that is
reached only from elsewhere, by a root other than its own file), and by its steps, a file.

Under MUST_NOT_REACH, a file reaches as under MUST_REACH, and each file of the scope that reaches is a finding: its file
fact said at the line of its first step (the kept fact of its own that matched, else the link that leads on), with the
way it reaches, each file a link leads to then what the fact that matched names, the shortest way found first.

A rule that counts reads the kept facts of each file of its scope alone, in the order the file says them: under AT_MOST
each one after its count is a finding, under AT_LEAST a file that keeps fewer than its count is one, its file fact the
fact said; an exemption excuses a finding as any other.

How many facts a rule reads at all is counted apart (read): a rule that reads none passes for want of anything to
check.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from string import Formatter

from xarch.kernel.violations import RULES, Violation
from xarch.modules.rules.application.logic.facts import reach_scopes
from xarch.modules.rules.application.logic.filters import Question, in_scope, question
from xarch.modules.rules.application.logic.sentences import said, value
from xarch.modules.rules.application.logic.targets import finding, matched
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.modules.rules.domain.rule import (
    AT_LEAST,
    AT_MOST,
    COUNTS,
    FAIL,
    FILE_REACH,
    MAY_NOT,
    MUST_BE_REACHED,
    MUST_NOT_REACH,
    MUST_REACH,
    Fact,
    Facts,
    Found,
    Read,
    Rule,
)

Reached = dict[tuple[str, ...] | str, set[int]]
"""What the links of a rule of reach reached: each declaration by its name, each file by its steps, with the files
whose links reached it, by their place in the run."""


def run(rules: Iterable[Rule], facts: Facts, profile: Profile) -> list[Violation | Weak]:
    rules = tuple(rules)
    reached = {index: _reach(rule, facts, profile) for index, rule in enumerate(rules)
               if rule.quantifier in (MUST_REACH, MUST_BE_REACHED)}
    ways = {index: _ways(rule, facts, profile) for index, rule in enumerate(rules) if rule.quantifier == MUST_NOT_REACH}
    found: list[Violation | Weak] = []
    for position, read in enumerate(facts.files):
        for index, rule in enumerate(rules):
            if in_scope(rule.scope, read, facts, profile):
                found += (_reaching(rule, read, ways[index], facts, profile) if index in ways
                          else _unreached(rule, read, position, reached[index], facts, profile) if index in reached
                          else _counted(rule, read, facts, profile) if rule.quantifier in COUNTS
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
        if rule.quantifier in (*FILE_REACH, AT_LEAST):
            count += 1
            continue
        count += sum(1 for kind in rule.facts for fact in file.facts.get(kind, ())
                     if _all(keep, Found(rule, file, fact), facts, profile))
    return count


def kept(rule: Rule, facts: Facts, profile: Profile) -> list[tuple[Read, Fact]]:
    """Each fact of the rule's kinds in the files of its scope that passes what it keeps, with its file, in the order
    of the files and then of the facts."""
    keep = _questions(rule.keep)
    return [(file, fact) for file in facts.files if in_scope(rule.scope, file, facts, profile)
            for kind in rule.facts for fact in file.facts.get(kind, ()) if _all(keep, Found(rule, file, fact), facts, profile)]


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


Way = tuple[int, tuple[str, ...]]
"""How a file reaches a target: the line of its first step, and the way on, each step as it is said."""


def _ways(rule: Rule, facts: Facts, profile: Profile) -> dict[tuple[str, ...], Way]:
    """How each file on the side of the rule's scope reaches a target, by its steps: a kept fact of its own that matches
    one, else the first of its links that leads to a file that reaches, by the shortest way; a file that reaches none
    is not held."""
    side, _ = reach_scopes(rule)
    assert side is not None
    keep, via = _questions(rule.keep), _questions(rule.via)
    on_side = [read for read in facts.files if in_scope(side, read, facts, profile)]
    ways: dict[tuple[str, ...], Way] = {}
    for read in on_side:
        own = next((fact for kind in rule.facts for fact in read.facts.get(kind, ())
                    if _all(keep, Found(rule, read, fact), facts, profile)
                    and matched(rule.targets, Found(rule, read, fact), facts, profile) is not None), None)
        if own is not None:
            ways[read.steps] = (own.line, (_named(own, facts),))
    links = {read.steps: [f for kind in rule.links for f in read.facts.get(kind, ())
                          if _all(via, Found(rule, read, f), facts, profile)] for read in on_side}
    grown = True
    while grown:
        known = dict(ways)
        for steps, linked in links.items():
            if steps in known:
                continue
            link = next((f for f in linked if f.target in known), None)
            if link is not None:
                ways[steps] = (link.line, (".".join((facts.root, *link.target)), *known[link.target][1]))
        grown = len(ways) > len(known)
    return ways


def _named(fact: Fact, facts: Facts) -> str:
    """What a fact that matched a target names, as a way says it: what it reaches, else its dotted path, else its name
    or text."""
    if fact.target:
        return ".".join((facts.root, *fact.target))
    return ".".join(fact.path) or fact.name or fact.text


def _reaching(rule: Rule, read: Read, ways: dict[tuple[str, ...], Way], facts: Facts,
              profile: Profile) -> list[Violation | Weak]:
    """The finding of a file of the scope of a rule under MUST_NOT_REACH that reaches a target: its file fact, at the
    line of its first step and with its way; none when an exemption excuses it."""
    way = ways.get(read.steps)
    if way is None:
        return []
    exempt = _questions(rule.exempt)
    found: list[Violation | Weak] = []
    for fact in read.facts.get("file", ()):
        candidate = Found(rule, read, fact._replace(line=way[0], chain=way[1]))
        if exempt and _any(exempt, candidate, facts, profile):
            continue
        found.append(_said(rule, _saying(rule, candidate, facts, profile)[1], candidate, facts, profile))
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


def _counted(rule: Rule, read: Read, facts: Facts, profile: Profile) -> list[Violation | Weak]:
    """The findings of a rule that counts in one file: under AT_MOST its kept facts after the count, under AT_LEAST its
    file fact when it keeps fewer than the count; those an exemption excuses dropped."""
    keep, exempt = _questions(rule.keep), _questions(rule.exempt)
    held = [fact for kind in rule.facts for fact in read.facts.get(kind, ())
            if _all(keep, Found(rule, read, fact), facts, profile)]
    if rule.quantifier == AT_MOST:
        subjects = held[rule.count:]
    else:
        subjects = list(read.facts.get("file", ())) if len(held) < rule.count else []
    found: list[Violation | Weak] = []
    for fact in subjects:
        candidate = Found(rule, read, fact)
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


def _listed(saying, found: Found, facts: Facts, profile: Profile) -> tuple[tuple[str, str], list[str]]:
    """The message and fix of a finding with each variable its saying lists per line left as a mark of its place,
    and the values of those variables."""
    marks = {name: f"\x00{index}\x00" for index, name in enumerate(saying.per_line)}

    def rendered(text: str) -> str:
        names = {name for _, name, _, _ in Formatter().parse(text) if name}
        return text.format_map({name: marks.get(name) or value(name, found, facts, profile) for name in names})

    return (rendered(saying.message), rendered(saying.fix)), [value(name, found, facts, profile)
                                                              for name in saying.per_line]


def _joined(text: str, values: list[list[str]]) -> str:
    for index, said_values in enumerate(values):
        text = text.replace(f"\x00{index}\x00", ", ".join(dict.fromkeys(said_values)))
    return text


def _file(rule: Rule, read: Read, facts: Facts, profile: Profile) -> list[Violation | Weak]:
    found: list[Violation | Weak] = []
    listed: dict[tuple, tuple[int, list[list[str]]]] = {}
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
            if saying.per_line:
                texts, values = _listed(saying, candidate, facts, profile)
                at = (fact.line, index, texts)
                if at not in listed:
                    listed[at] = (len(found), [[] for _ in values])
                    found.append(_said(rule, saying, candidate, facts, profile))
                place, gathered = listed[at]
                for into, one in zip(gathered, values):
                    into.append(one)
                first = found[place]
                found[place] = replace(first, message=_joined(texts[0], gathered), fix=_joined(texts[1], gathered))
                continue
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
