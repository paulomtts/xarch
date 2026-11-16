"""How a project's tests are named and placed, as the profile says it: the test framework's names, how a table of
cases is written, the scenario-coverage and stand-ins guards, and where the fakes live."""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Framework:
    """How the project's test framework names things: the patterns of a test file's name (matched against the file
    name alone, `*` for any text) and of a test function's, and the dotted names of what skips a test or expects it
    to fail (a marker or a call; empty: none is counted); and how a test function holds a table of cases (None: the
    profile does not say)."""
    files: tuple[str, ...]
    functions: str
    skips: tuple[tuple[str, ...], ...] = ()
    table: CaseTable | None = None


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
    how the table is written, and the name of a use case's test file, `{name}` standing for the use case in
    snake_case. key is the name a profile switches it on by."""
    key: ClassVar[str] = "scenario-coverage"
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
    autospec call takes; and the fixtures, whose methods build mocks the same way. The other parameters are those of
    `fakes`. key is the name a profile switches it on by."""
    key: ClassVar[str] = "stand-ins"
    mocks: tuple[tuple[str, ...], ...]
    autospec: tuple[tuple[str, ...], ...]
    spec: tuple[str, ...]
    fixtures: tuple[Fixture, ...] = ()


@dataclass(frozen=True)
class Fakes:
    """Where the test fakes live, as a folder below the tests folder (e.g. ("fakes",)), the parts they stand in for,
    and how a fake's name starts (the fake of port X is <prefix>X; empty when the file does not say)."""
    folder: tuple[str, ...]
    stand_in_for: tuple[str, ...]
    prefix: str = ""
