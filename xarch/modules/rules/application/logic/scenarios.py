"""The scenario-coverage guard: every use case's result union is covered by the rows of a table in its test file.

A use case is a module-level union `<Name><suffix> = A | B | ...` of plain names in a file of the results part, in
an instance of the `each` folder: <Name> is the use case and A, B, ... its variants. Its test file is
`test_<name>.py`, <Name> in snake_case (PublishDocument: test_publish_document.py), among the files of the table
tier in the same instance (see tier_of). That file must hold a table, read from its syntax tree:

    a test function decorated `pytest.mark.parametrize(<names>, <rows>)`, whose names include the three columns
    the guard is given (state, command, result), as one comma-separated string or a list or tuple of strings;
    <rows> is a list or tuple literal, or the name of one assigned once at the top of the file; any other form
    (a call, a concatenation, a comprehension, a starred element) is a violation, since a table that cannot be read
    cannot be checked.
    every row is `pytest.param(..., id="<a sentence>")`, with a non-empty string literal as its id: a bare tuple,
    a row without an id or one whose id is not a literal is a violation.
    the head of each row's result value (the callee of `Rejected("why")`, or a bare name) is a variant of the
    union; every variant heads the result of at least one row, or is named in the body of a standalone test
    function (one with no table) of the same file, for a case that does not fit a row.
    the body of a table test holds no `if`, `match`, `try`, `for` or `while`: the odd case is its own test.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Function, Profile, Row, SourceFile, Table

CASE = 'write pytest.param(..., id="<a sentence stating the outcome>")'


def snake_name(name: str) -> str:
    """CamelCase to snake_case: MarkRead is mark_read, HTTPCheck is http_check."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


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
                found += _covered(test, union.name, union.members, guard.columns)
    return found


def _in(profile: Profile, test: SourceFile, tier: str, instance: str) -> bool:
    where = tested(profile, test.path)
    return where.tier is not None and where.tier.name == tier and where.instance == instance


def _covered(test: SourceFile, union: str, variants: tuple[str, ...], columns: tuple[str, str, str]) -> list[Violation]:
    functions = [f for f in test.functions if f.name.startswith("test_")]
    tables = [(f, t) for f in functions for t in f.tables if set(columns) <= set(t.columns)]
    if not tables:
        return [Violation(test.name, 1, "no table test: add a parametrized test whose parameters are "
                                        f"{', '.join(columns)} (scenario-coverage)")]
    problems: list[tuple[int, str]] = []
    covered: set[str] = set()
    for function, table in tables:
        problems += _branches(function) + _rows(table, union, variants, columns[-1], covered)
    standalone = set().union(*(f.mentions for f in functions if not f.tables))
    line = tables[0][1].line
    if all(table.rows is not None for _, table in tables):
        problems += [(line, f"{union} variant {v} has no row in the table and no standalone test naming it")
                     for v in variants if v not in covered | standalone]
    return [Violation(test.name, line, f"{problem} (scenario-coverage)") for line, problem in problems]


def _branches(function: Function) -> list[tuple[int, str]]:
    return [(line, f"{function.name} has {'an' if keyword == 'if' else 'a'} `{keyword}` in its body: arrange from "
                   "given, act with when, assert == then, and give the odd case its own test")
            for line, keyword in function.branches]


def _rows(table: Table, union: str, variants: tuple[str, ...], result: str, covered: set[str]) -> list[tuple[int, str]]:
    if table.rows is None:
        return [(table.line, "the rows of the table cannot be read: write them as a list, or as the name of a list "
                             "assigned at the top of the file")]
    problems: list[tuple[int, str]] = []
    for row in table.rows:
        if not row.param:
            problems.append((row.line, f"row is not a pytest.param(...): {CASE}"))
        elif row.id is None:
            problems.append((row.line, f"row has no id: {CASE}"))
        if row.param or row.cells:
            problems += _result(row, table.columns.index(result), union, variants, result, covered)
    return problems


def _result(row: Row, index: int, union: str, variants: tuple[str, ...], column: str,
            covered: set[str]) -> list[tuple[int, str]]:
    head = row.cells[index] if index < len(row.cells) else None
    if head in variants:
        covered.add(head)
        return []
    if head is None:
        return [(row.line, f"row '{row.id}' names no variant in its {column} column: use one of {', '.join(variants)}")]
    return [(row.line, f"row '{row.id}' has {head} in its {column} column, which is not a variant of {union}")]
