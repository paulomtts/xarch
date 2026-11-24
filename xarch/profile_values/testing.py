"""How a project's tests are named and placed, as the profile says it: the test framework's names, how a table of
cases is written, the scenario-coverage and stand-ins guards, and where the fakes live."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Framework:
    """How the project's test framework names things: the patterns of a test file's name (matched against the file
    name alone, `*` for any text) and of a test function's, and the dotted names of what skips a test or expects it
    to fail (a marker or a call; empty: none is counted); and how a test function holds a table of cases (None: the
    profile does not say); and the table forms it
    writes (tables; none: it writes none)."""
    files: tuple[str, ...]
    functions: str
    skips: tuple[tuple[str, ...], ...] = ()
    table: CaseTable | None = None
    tables: tuple[TableForm, ...] = ()


@dataclass(frozen=True)
class Place:
    """Where a slot of a table form is among the arguments of its holder: the argument at position (from 0; None: none
    is read by its position), else the one its keyword gives ("": none is read by a keyword); one of the two at
    least."""
    position: int | None = None
    keyword: str = ""


@dataclass(frozen=True)
class RowId:
    """What gives a row of a table its id, exactly one of three: a keyword of the row call (keyword), a field of a
    literal row (field), or its value at a position from 0 (position)."""
    keyword: str = ""
    field: str = ""
    position: int | None = None


@dataclass(frozen=True)
class TableForm:
    """One form a table of cases is written in, as the framework's `testing.tables` says it. Its holder, one of three:
    a decorator of the test (decorator, its dotted name), a call that makes or wraps the test (call, one or more
    dotted names), or a loop of the test's body over a list literal (loop). Where the column names come from
    (columns_from: a place among the holder's arguments, or one of the words parameters, bound and fields); where the rows are (rows: a
    place among the holder's arguments; None for a loop); how a row is written (row: the dotted name a row calls;
    empty: a row is a literal); and what gives a row its id."""
    columns_from: Place | str
    rows: Place | None
    row: tuple[str, ...]
    id: RowId
    decorator: tuple[str, ...] = ()
    call: tuple[tuple[str, ...], ...] = ()
    loop: bool = False


@dataclass(frozen=True)
class CaseTable:
    """How a test function holds a table of cases: the dotted name of its decorator and of its row, the keyword that
    gives a row its id, and (None: positional only) the keywords its two arguments, the parameter names and the rows,
    may be given by."""
    decorator: tuple[str, ...]
    row: tuple[str, ...]
    id: str
    keywords: tuple[str, str] | None = None


@dataclass(frozen=True)
class ScenarioCoverage:
    """The guard scenario-coverage: the part holding the result unions, the tier holding their tables, how a union's
    name ends, the names of the three parameters of a table (its state, its command and its result, in that order),
    how the table is written, and the name of a use case's test file, `{name:<case>}` standing for the use case in
    the case it writes."""
    results: str
    tier: str
    suffix: str
    columns: tuple[str, str, str]
    table: CaseTable
    file: str


@dataclass(frozen=True)
class Fixture:
    """A parameter of a test function that hands over a mock builder, and the names of its methods: those that build
    a mock, and those that build one from a spec given as an argument (autospec)."""
    name: str
    mocks: tuple[str, ...]
    autospec: tuple[str, ...] = ()


@dataclass(frozen=True)
class StandIns:
    """The guard stand-ins: the dotted names of the calls that build a mock, of those that build a mock from a spec
    given as an argument (autospec), and the keywords a mock is given its spec by; the first keyword is the one an
    autospec call takes; the fixtures, whose methods build mocks the same way; and the position of the argument that
    names the spec of a call that builds a mock (spec_position, from 0; None: only a keyword names it). The other
    parameters are those of `fakes`."""
    mocks: tuple[tuple[str, ...], ...]
    autospec: tuple[tuple[str, ...], ...]
    spec: tuple[str, ...]
    fixtures: tuple[Fixture, ...] = ()
    spec_position: int | None = None


@dataclass(frozen=True)
class Fakes:
    """Where the test fakes live, as a folder below the tests folder (e.g. ("fakes",)), the parts they stand in for,
    and how a fake's name starts (the fake of port X is <prefix>X; empty when the file does not say)."""
    folder: tuple[str, ...]
    stand_in_for: tuple[str, ...]
    prefix: str = ""
