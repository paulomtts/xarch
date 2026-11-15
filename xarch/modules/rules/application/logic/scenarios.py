"""The scenario-coverage guard: every use case's result union is covered by the scenarios of its test file.

A use case is a module-level union `<Name><suffix> = A | B | ...` of plain names in a file of the results part, in
an instance of the `each` folder: <Name> is the use case and A, B, ... its variants. Its test file is
`test_<name>.py`, <Name> in snake_case (PublishDocument: test_publish_document.py), among the files of the scenario
tier in the same instance (see tier_of). Its module docstring is the header, read line by line, each stripped:

    Scenario: <title>                    starts a scenario; the title is the rest of the line
      ... Then the <suffix> is <Variant> on this line or a later one before the next scenario: the scenario's variant,
                                         the name right after "is" (Rejected("why") names Rejected)

Every variant has a scenario, every scenario names one of the variants, and every scenario has a test function (at
module level or in a class) named `test_` and the title in snake_case: lowercased, each run of characters other than
letters and digits made one "_", none at either end.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Profile, SourceFile

SCENARIO = "Scenario:"


@dataclass(frozen=True)
class Scenario:
    title: str
    variant: str | None


def snake_name(name: str) -> str:
    """CamelCase to snake_case: MarkRead is mark_read, HTTPCheck is http_check."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


def snake_title(title: str) -> str:
    return re.sub(r"[^0-9a-zA-Z]+", "_", title.lower()).strip("_")


def scenarios(docstring: str, suffix: str) -> list[Scenario]:
    then = re.compile(rf"\bThen the {re.escape(suffix)} is ([A-Za-z_][A-Za-z0-9_]*)")
    found: list[Scenario] = []
    for line in docstring.splitlines():
        line = line.strip()
        if line.startswith(SCENARIO):
            found.append(Scenario(line.removeprefix(SCENARIO).strip(), None))
        elif found and found[-1].variant is None and (match := then.search(line)):
            found[-1] = Scenario(found[-1].title, match[1])
    return found


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    guard = profile.scenarios
    if guard is None:
        return []
    tests = list(tests)
    found: list[Violation] = []
    for file in app:
        where = place(profile, dotted(file.path)[0])
        if where is None or where.part != guard.results or where.instance is None:
            continue
        for union in file.unions:
            if not union.name.endswith(guard.suffix) or union.name == guard.suffix:
                continue
            use_case = union.name.removesuffix(guard.suffix)
            name = f"test_{snake_name(use_case)}.py"
            files = [t for t in tests if t.path[-1] == name and _in(profile, t, guard.tier, where.instance)]
            if not files:
                found.append(Violation(file.name, union.line, f"{union.name} has no test file {name} among the "
                                                              f"{guard.tier} tests of {where.instance} "
                                                              "(scenario-coverage)"))
            for test in files:
                found += _covered(test, union.name, union.members, guard.suffix)
    return found


def _in(profile: Profile, test: SourceFile, tier: str, instance: str) -> bool:
    where = tested(profile, test.path)
    return where.tier is not None and where.tier.name == tier and where.instance == instance


def _covered(test: SourceFile, union: str, variants: tuple[str, ...], suffix: str) -> list[Violation]:
    found = scenarios(test.docstring or "", suffix)
    problems = [f"{union} variant {v} has no scenario" for v in variants if v not in {s.variant for s in found}]
    for s in found:
        if s.variant is None:
            problems.append(f"scenario '{s.title}' names no variant: end it with `Then the {suffix} is <Variant>`")
        elif s.variant not in variants:
            problems.append(f"scenario '{s.title}' ends in {s.variant}, which is not a variant of {union}")
        if f"test_{snake_title(s.title)}" not in test.functions:
            problems.append(f"scenario '{s.title}' has no test test_{snake_title(s.title)}")
    return [Violation(test.name, 1, f"{p} (scenario-coverage)") for p in problems]
