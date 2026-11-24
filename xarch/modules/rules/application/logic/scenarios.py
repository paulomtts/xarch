"""The scenario-coverage guard: every use case's result union is covered by the rows of a table in its test file.

A use case is a module-level union `<Name><suffix> = A | B | ...` of plain names in a file of the results part, in
an instance of a repeating folder: <Name> is the use case and A, B, ... its variants. Its test file is the guard's
`file` with `{name:<case>}` replaced by <Name> in that case (PublishDocument with `{name:snake}`: publish_document),
among the files of the table tier in the same instance (see tier_of). That file must hold a table, read from its
syntax tree in one of the forms the framework writes (`testing.tables`; the reader says how each is read), a test
being one the framework declares (`testing.declared`), as the reader hands the file's tests over:

    a test holding a table whose columns include the three the guard is given (state, command, result);
    rows the reader cannot read are a violation, since a table that cannot be read cannot be checked.
    every row is written as its form writes one, with a non-empty string literal as its id: a row written otherwise,
    a row without an id or one whose id is not a literal is a violation, said and fixed in the words of the language
    (its data file's `writing`), as the form of the row's table writes a row.
    the head of each row's result value (the callee of `Rejected("why")`, or a bare name) is a variant of the
    union; every variant heads the result of at least one row, or is named in the body of a standalone test
    (one with no table) of the same file, for a case that does not fit a row.
    the body of a table test holds no statement that branches (one of the language's `branching` keywords), and no
    expression that chooses between values (one of its `branching_expressions`): the odd case is its own test. The
    statement that runs a table's rows, at the line the reader gives as the table's runs, is the table and no branch
    of its test.

A framework that writes no table form (its `testing.tables` empty) has no table to read, and each result is its own
test: the guard has no columns, and every variant of the union must be named in the body of a test of the
file; a variant named by none is a violation at the top of the file. No row,
id or branch is checked then, whatever the facts of a function hold.

plain holds every table test of a tier that says `plain_tables` to the same rule as a use case's: no statement that
branches and no expression that chooses between values in its body, but the statement that runs a table's rows, said
once where scenario-coverage already says it of a use case's table.

weak lists, without failing, a variant met to the letter only: one no row covers, credited only to standalone tests
of the file that name it (to any test of the file that names it, for a framework that writes no table form),
none of which holds an `assert` statement in its body.

A finding names a test as it is declared: by its title in double quotes when the framework declares it by a call's
title (`"places an order" has a branch in its body`), by its function's name, bare, otherwise.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from xarch.kernel.logic.cases import filled
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.places import file_place
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.parsed import Row, SourceFile, Table, Test, Union
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.profile_values.testing import ScenarioCoverage

RULE = "scenario-coverage"
Problem = tuple[int, str, str]
"""A problem of a test file: its line, what is wrong, and how to fix it."""
_OUTCOME = "<a sentence stating the outcome>"
"""What the fix of a row writes as its id's text."""


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    guard = profile.scenarios
    if guard is None or profile.framework is None:
        return []
    found: list[Violation] = []
    for file, union, instance, name, files in _cases(app, tests, profile, guard):
        if not files:
            found.append(Violation(file.name, union.line, f"{union.name} has no test file {name} among the "
                                                          f"{guard.tier} tests of {instance} ({RULE})", RULE,
                                   f"write {name} among the {guard.tier} tests of {instance}"))
        for test in files:
            found += (_covered(test, union.name, union.members, guard, profile) if profile.framework.tables
                      else _named(test, union.name, union.members))
    return found


def plain(tests: Iterable[SourceFile], profile: Profile, said: Iterable[Violation] = ()) -> list[Violation]:
    """The branches in the body of each table test of a tier whose tables are plain, the statement that runs a table's
    rows being none, but where said already holds a violation of the rule at that file and line."""
    plain_tiers = {tier.name for tier in profile.tiers if tier.plain_tables}
    if not plain_tiers or profile.framework is None:
        return []
    known = {(v.file, v.line) for v in said if v.rule == RULE}
    found: list[Violation] = []
    for test in tests:
        where = tested(profile, test.path, test.beside)
        if where.tier is None or where.tier.name not in plain_tiers:
            continue
        key = f"tiers.{where.tier.name}.plain_tables"
        for declared in test.tests:
            if declared.body.tables:
                found += [Violation(test.name, line, f"{problem}, and a table test of the {where.tier.name} tier holds "
                                                     f"no branch ({key}; {RULE})", RULE, fix)
                          for line, problem, fix in _branches(declared, profile) if (test.name, line) not in known]
    return found


def weak(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Weak]:
    guard = profile.scenarios
    if guard is None or profile.framework is None:
        return []
    found: list[Weak] = []
    for _, union, _, _, files in _cases(app, tests, profile, guard):
        for test in files:
            found += _credited(test, union.name, union.members, guard, profile)
    return found


def _cases(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
           guard: ScenarioCoverage) -> Iterator[tuple[SourceFile, Union, str, str, list[SourceFile]]]:
    """Each use case of the app: the file of its results, its union, the instance it is in, the name of the test file
    the guard expects, and the test files of that name among the table tier's tests of the instance."""
    tests = list(tests)
    for file in app:
        where = file_place(profile, file.path)
        if where is None or where.part != guard.results or where.instance is None:
            continue
        for union in _use_cases(file, guard):
            name = _test_file(union, guard)
            yield file, union, where.instance, name, [t for t in tests if t.path[-1] == name
                                                      and _in(profile, t, guard.tier, where.instance)]


def _use_cases(file: SourceFile, guard: ScenarioCoverage) -> list[Union]:
    """The unions of a file that are a use case's results: two names or more joined, named for the use case with the
    guard's suffix (one name alone is an alias, and the suffix alone names no use case)."""
    return [u for u in file.unions if len(u.members) > 1 and u.name.endswith(guard.suffix) and u.name != guard.suffix]


def _test_file(union: Union, guard: ScenarioCoverage) -> str:
    """The name of the test file the guard expects for the use case a union holds the results of: the guard's file,
    the use case's name written in the case its placeholder asks for."""
    return filled(guard.file, union.name.removesuffix(guard.suffix))


def _given_id(row: Row) -> str | None:
    """A row's id when it says something: a literal of blanks alone is no id."""
    return row.id if row.id is not None and row.id.strip() else None


def _printed(declared: Test) -> str:
    """How a finding names a test: a title in double quotes, a function's name bare."""
    return f'"{declared.name}"' if declared.titled else declared.name


def _named(test: SourceFile, union: str, variants: tuple[str, ...]) -> list[Violation]:
    """Each variant no test of the file names in its body, for a framework that writes no table form, in the union's
    order, at the top of the file."""
    named = set().union(*(declared.body.mentions for declared in test.tests))
    return [Violation(test.name, 1, f"{union} variant {v} is named by no test ({RULE})", RULE,
                      f"write a test naming {v}") for v in variants if v not in named]


def _credited(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
              profile: Profile) -> list[Weak]:
    assert profile.framework is not None
    covered: set[str] = set()
    standalone = test.tests
    if profile.framework.tables:
        for declared in test.tests:
            for table in declared.body.tables:
                if set(guard.columns) <= set(table.columns):
                    _rows(table, union, variants, guard, profile, covered)
        standalone = tuple(declared for declared in test.tests if not declared.body.tables)
    found: list[Weak] = []
    for variant in variants:
        credit = [declared for declared in standalone if variant in declared.body.mentions]
        if variant not in covered and credit and not any(declared.body.asserts for declared in credit):
            names = ", ".join(_printed(declared) for declared in credit)
            found.append(Weak(RULE, test.name, credit[0].line, f"{union} variant {variant} is credited to {names} by "
                                                               "name only: no assert in their bodies"))
    return found


def _in(profile: Profile, test: SourceFile, tier: str, instance: str) -> bool:
    where = tested(profile, test.path, test.beside)
    return where.tier is not None and where.tier.name == tier and where.instance == instance


def _covered(test: SourceFile, union: str, variants: tuple[str, ...], guard: ScenarioCoverage,
             profile: Profile) -> list[Violation]:
    columns = guard.columns
    tables = [(declared, table) for declared in test.tests for table in declared.body.tables
              if set(columns) <= set(table.columns)]
    if not tables:
        return [Violation(test.name, 1, f"no table test whose parameters are {', '.join(columns)} ({RULE})", RULE,
                          f"add a table test whose parameters are {', '.join(columns)}")]
    problems: list[Problem] = []
    covered: set[str] = set()
    for declared, table in tables:
        problems += _branches(declared, profile) + _rows(table, union, variants, guard, profile, covered)
    standalone = set().union(*(declared.body.mentions for declared in test.tests if not declared.body.tables))
    line = tables[0][1].line
    if all(table.rows is not None for _, table in tables):
        problems += [(line, f"{union} variant {v} has no row in the table and no standalone test naming it",
                      f"add a row whose {columns[-1]} is {v}, or a standalone test naming it")
                     for v in variants if v not in covered | standalone]
    return [Violation(test.name, line, f"{problem} ({RULE})", RULE, fix) for line, problem, fix in problems]


def _branches(declared: Test, profile: Profile) -> list[Problem]:
    """Each block and each expression of the test's body that branches, in line order, but the loop at the line that
    runs the rows of one of its tables (its runs; 0 is no line)."""
    fix = "arrange from given, act with when, assert == then, and give the odd case its own test"
    language = profile.language
    body = declared.body
    runs = {(table.runs, "for") for table in body.tables if table.runs}
    found = [(line, keyword, "") for line, keyword in body.blocks
             if keyword in language.branching and (line, keyword) not in runs]
    found += [(line, keyword, " expression") for line, keyword in body.expressions
              if keyword in language.branching_expressions]
    return [(line, f"{_printed(declared)} has {'an' if keyword[:1] in 'aeiou' else 'a'} `{keyword}`{what} in its body", fix)
            for line, keyword, what in sorted(found)]


def _rows(table: Table, union: str, variants: tuple[str, ...], guard: ScenarioCoverage, profile: Profile,
          covered: set[str]) -> list[Problem]:
    assert profile.framework is not None
    form = profile.framework.tables[table.form]
    writing = profile.language.writing
    callee = profile.language.member.join(form.row)
    result = guard.columns[-1]
    given = form.id.written(writing, callee, _OUTCOME)
    case = (f"write {given}" if given else
            f"write the row's id, a sentence stating the outcome, as its value at position {form.id.position}")
    shape = writing.row_call(callee) if form.row else "literal"
    if table.rows is None:
        fix = "write them as a list, or as the name of a list assigned at the top of the file"
        return [(table.line, "the rows of the table cannot be read", fix)]
    problems: list[Problem] = []
    for row in table.rows:
        if not row.written:
            problems.append((row.line, f"row is not a {shape}", case))
        elif _given_id(row) is None:
            problems.append((row.line, "row has no id", case))
        if row.written or row.cells:
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
        return [(row.line, f"row '{_given_id(row)}' names no variant in its {column} column", fix)]
    return [(row.line, f"row '{_given_id(row)}' has {head} in its {column} column, which is not a variant of {union}",
             fix)]
