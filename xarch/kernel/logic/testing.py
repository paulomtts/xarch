"""How a project's tests are named and placed, as the profile says it and every module that reads a profile needs it:
the test framework's names, how a table of cases is written, the scenario-coverage and stand-ins guards, where the
fakes live, and a kind of test as the checks read it."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.placement import Target


@dataclass(frozen=True)
class Framework:
    """How the project's test framework names things: the patterns of a test file's name (matched against the file
    name alone, `*` for any text) and of a test function's, and the dotted names of what skips a test or expects it
    to fail (a marker or a call; empty: none is counted)."""
    files: tuple[str, ...]
    functions: str
    skips: tuple[tuple[str, ...], ...] = ()


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
    snake_case."""
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
    `fakes`."""
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


@dataclass(frozen=True)
class TierView:
    """One kind of test as a check reads it: its name; the parts it tests, each as a target (in its own instance for a
    part of a repeating folder); the folder below the tests root of tests that mirror no part (an empty folder places
    nothing); the parts its tests may use as types only; whether its tests keep to the forbidden list of the part they
    mirror; its words (proves, may_touch, litmus, one_file_per), which `where` shows; what the tests of its folder may
    import of the app (None: no folder, and the tests import what the part they mirror may); and the parts one of which
    each of its test files must reach."""
    name: str
    subject: tuple[Target, ...]
    folder: tuple[str, ...] | None = None
    types_only: tuple[str, ...] = ()
    forbidden: bool = False
    proves: str = ""
    may_touch: str = ""
    litmus: str = ""
    one_file_per: str = ""
    may_import: tuple[Target, ...] | None = None
    must_import: tuple[str, ...] = ()
