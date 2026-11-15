"""The scenario-coverage guard: every use case's result union is covered by the rows of a table in its test file.

A use case is a module-level union `<Name><suffix> = A | B | ...` of plain names in a file of the results part, in
an instance of a repeating folder: <Name> is the use case and A, B, ... its variants. Its test file is the guard's
`file` with `{name}` replaced by <Name> in snake_case (PublishDocument: publish_document), among the files of the
table tier in the same instance (see tier_of). That file must hold a table, read from its syntax tree; the
decorator, the row and the keyword of a row's id are the names the guard is given (see CaseTable), a test function
is one whose name matches the profile's pattern:

    a test function decorated `<decorator>(<names>, <rows>)`, whose names include the three columns the guard is
    given (state, command, result), as one comma-separated string or a list or tuple of strings;
    <rows> is a list or tuple literal, or the name of one assigned once at the top of the file; any other form
    (a call, a concatenation, a comprehension, a starred element) is a violation, since a table that cannot be read
    cannot be checked.
    every row is `<row>(..., <id>="<a sentence>")`, with a non-empty string literal as its id: a bare tuple,
    a row without an id or one whose id is not a literal is a violation.
    the head of each row's result value (the callee of `Rejected("why")`, or a bare name) is a variant of the
    union; every variant heads the result of at least one row, or is named in the body of a standalone test
    function (one with no table) of the same file, for a case that does not fit a row.
    the body of a table test holds no statement that branches (one of the language's `branching` keywords): the odd
    case is its own test.

weak lists, without failing, a variant met to the letter only: one no row covers, credited only to standalone tests
of the file that name it, none of which holds an `assert` statement in its body.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from fnmatch import fnmatchcase

from xarch.kernel.logic.testing import ScenarioCoverage
from xarch.kernel.violations import Violation, Weak
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.values import Function, Profile, Row, SourceFile, Table

RULE = "scenario-coverage"
NAME = "{name}"
"""Stands, in the file name the scenario-coverage guard expects, for the use case's name in snake_case."""
Problem = tuple[int, str, str]
"""A problem of a test file: its line, what is wrong, and how to fix it."""


def snake_name(name: str) -> str:
    """CamelCase to snake_case: MarkRead is mark_read, HTTPCheck is http_check."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    guard = profile.scenarios
    if guard is None or profile.framework is None:
        return []
    tests = list(tests)
    found: list[Violation] = []
    for file in app:
        where = place(profile, dotted(file.path, profile.language.marks)[0])
        if where is None or where.part != guard.results or where.instance is None:
            continue
        for union in file.unions:
            if not union.name.endswith(guard.suffix) or union.name == guard.suffix:
                continue
            use_case = union.name.removesuffix(guard.suffix)
            name = guard.file.replace(NAME, snake_name(use_case))
            files = [t for t in tests if t.path[-1] == name and _in(profile, t, guard.tier, where.instance)]
            if not files:
                found.append(Violation(file.name, union.line, f"{union.name} has no test file {name} among the "
                                                              f"{guard.tier} tests of {where.instance} "
                                                              f"({RULE})", RULE,
                                       f"write {name} among the {guard.tier} tests of {where.instance}"))
            for test in files:
                found += _covered(test, union.name, union.members, guard, profile)
    return found


def weak(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Weak]:
    guard = profile.scenarios
    if guard is None or profile.framework is None:
        return []
    tests = list(tests)
    found: list[Weak] = []
    for file in app:
        where = place(profile, dotted(file.path, profile.language.marks)[0])
        if where is None or where.part != guard.results or where.instance is None:
            continue
        for union in file.unions:
            if not union.name.endswith(guard.suffix) or union.name == guard.suffix:
                continue
            name = guard.file.replace(NAME, snake_name(union.name.removesuffix(guard.suffix)))
            for test in (t for t in tests if t.path[-1] == name and _in(profile, t, guard.tier, where.instance)):
                found += _credited(test, union.name, union.members, guard, profile.framework.functions)
    return found


def _credited(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
              pattern: str) -> list[Weak]:
    functions = [f for f in test.functions if fnmatchcase(f.name, pattern)]
    covered: set[str] = set()
    for function in functions:
        for table in function.tables:
            if set(guard.columns) <= set(table.columns):
                _rows(table, union, variants, guard, covered)
    found: list[Weak] = []
    for variant in variants:
        credit = [f for f in functions if not f.tables and variant in f.mentions]
        if variant not in covered and credit and not any(f.asserts for f in credit):
            names = ", ".join(f.name for f in credit)
            found.append(Weak(RULE, test.name, credit[0].line, f"{union} variant {variant} is credited to {names} by "
                                                               "name only: no assert in their bodies"))
    return found


def _in(profile: Profile, test: SourceFile, tier: str, instance: str) -> bool:
    where = tested(profile, test.path)
    return where.tier is not None and where.tier.name == tier and where.instance == instance


def _covered(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
             profile: Profile) -> list[Violation]:
    columns = guard.columns
    assert profile.framework is not None
    functions = [f for f in test.functions if fnmatchcase(f.name, profile.framework.functions)]
    tables = [(f, t) for f in functions for t in f.tables if set(columns) <= set(t.columns)]
    if not tables:
        return [Violation(test.name, 1, f"no table test whose parameters are {', '.join(columns)} ({RULE})", RULE,
                          f"add a table test whose parameters are {', '.join(columns)}")]
    problems: list[Problem] = []
    covered: set[str] = set()
    for function, table in tables:
        problems += _branches(function, profile) + _rows(table, union, variants, guard, covered)
    standalone = set().union(*(f.mentions for f in functions if not f.tables))
    line = tables[0][1].line
    if all(table.rows is not None for _, table in tables):
        problems += [(line, f"{union} variant {v} has no row in the table and no standalone test naming it",
                      f"add a row whose {columns[-1]} is {v}, or a standalone test naming it")
                     for v in variants if v not in covered | standalone]
    return [Violation(test.name, line, f"{problem} ({RULE})", RULE, fix) for line, problem, fix in problems]


def _branches(function: Function, profile: Profile) -> list[Problem]:
    fix = "arrange from given, act with when, assert == then, and give the odd case its own test"
    return [(line, f"{function.name} has {'an' if keyword[:1] in 'aeiou' else 'a'} `{keyword}` in its body", fix)
            for line, keyword in function.blocks if keyword in profile.language.branching]


def _rows(table: Table, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
          covered: set[str]) -> list[Problem]:
    result = guard.columns[-1]
    written = ".".join(guard.table.row)
    case = f'write {written}(..., {guard.table.id}="<a sentence stating the outcome>")'
    if table.rows is None:
        fix = "write them as a list, or as the name of a list assigned at the top of the file"
        return [(table.line, "the rows of the table cannot be read", fix)]
    problems: list[Problem] = []
    for row in table.rows:
        if not row.param:
            problems.append((row.line, f"row is not a {written}(...)", case))
        elif row.id is None:
            problems.append((row.line, "row has no id", case))
        if row.param or row.cells:
            problems += _result(row, table.columns.index(result), union, variants, result, covered)
    return problems


def _result(row: Row, index: int, union: str, variants: tuple[str, ...], column: str,
            covered: set[str]) -> list[Problem]:
    head = row.cells[index] if index < len(row.cells) else None
    if head in variants:
        covered.add(head)
        return []
    fix = f"use one of {', '.join(variants)}"
    if head is None:
        return [(row.line, f"row '{row.id}' names no variant in its {column} column", fix)]
    return [(row.line, f"row '{row.id}' has {head} in its {column} column, which is not a variant of {union}", fix)]
