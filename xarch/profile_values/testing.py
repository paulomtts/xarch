"""How a project's tests are named and placed, as the profile says it: the test framework's names, the forms that
declare a test, the table forms it writes, the scenario-coverage and stand-ins guards, and where the fakes live."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.profile_values.language import SPEC_FORMS, Writing


@dataclass(frozen=True)
class Framework:
    """How the project's test framework names things: the patterns of a test file's name (matched against the file
    name alone, `*` for any text); the forms a test is declared in (declared, at least one: a function whose name
    matches a pattern, or a call whose arguments hold the test's title and its body), a test being of the first form
    it matches; the dotted names of what skips a test or expects it to fail (a marker or a call; empty: none is
    counted); the table forms it writes (tables; none: it writes none, and no table is read); the names it binds
    without an import (globals), which are not the language's predefined names; and whether every test of a part sits
    beside the code it tests rather than in the mirrored tests tree (beside, the project's `testing.beside`)."""
    files: tuple[str, ...]
    declared: tuple[TestForm, ...]
    skips: tuple[tuple[str, ...], ...] = ()
    tables: tuple[TableForm, ...] = ()
    globals: tuple[tuple[str, ...], ...] = ()
    beside: bool = False


@dataclass(frozen=True)
class Place:
    """Where a slot of a table form is among the arguments of its holder: the argument at position (from 0; None: none
    is read by its position), else the one its keyword gives ("": none is read by a keyword); one of the two at
    least."""
    position: int | None = None
    keyword: str = ""


@dataclass(frozen=True)
class TestForm:
    """One form a test is declared in, as the framework's `testing.declared` says it, exactly one of two: a function
    whose name matches function, a pattern with `*` for any text; or a call of one of call's dotted names, the test's
    title the argument at title and its body the one at body (both set exactly when call is)."""
    function: str = ""
    call: tuple[tuple[str, ...], ...] = ()
    title: Place | None = None
    body: Place | None = None


@dataclass(frozen=True)
class RowId:
    """What gives a row of a table its id, exactly one of three: a keyword of the row call (keyword), a field of a
    literal row (field), or its value at a position from 0 (position)."""
    keyword: str = ""
    field: str = ""
    position: int | None = None

    @property
    def name(self) -> str:
        """The keyword or the field that gives the id; "" for an id by position."""
        return self.keyword or self.field

    def written(self, writing: Writing, callee: str, text: str) -> str:
        """The id as the language writes it, text its value: writing's keyword template, callee being what the row
        calls, or its field template; "" for an id by position, which no template writes."""
        if self.keyword:
            return writing.keyword_id(callee, self.keyword, text)
        return writing.field_id(self.field, text) if self.field else ""


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
class ScenarioCoverage:
    """The guard scenario-coverage: the part holding the result unions, the tier holding their tables, how a union's
    name ends, the names of the three parameters of a table (its state, its command and its result, in that order;
    none for a framework that writes no table form, where each result is its own test), and the name of a use case's
    test file, `{name:<case>}` standing for the use case in the case it writes."""
    results: str
    tier: str
    suffix: str
    columns: tuple[str, ...]
    file: str


@dataclass(frozen=True)
class Fixture:
    """A parameter of a test function that hands over a mock builder, and the names of its methods: those that build
    a mock, and those that build one from a spec given as an argument (autospec)."""
    name: str
    mocks: tuple[str, ...]
    autospec: tuple[str, ...] = ()


@dataclass(frozen=True)
class SpecEntry:
    """One way a call that builds a mock names its spec, as an entry of the framework's `testing.mocks.specs` says it,
    exactly one of three: a keyword argument (keyword, its name), the positional argument at a place from 0
    (position), or the type argument at a place from 0 (type_argument)."""
    keyword: str = ""
    position: int | None = None
    type_argument: int | None = None

    @property
    def form(self) -> str:
        """The key the entry is written with, one of SPEC_FORMS."""
        if self.keyword:
            return SPEC_FORMS[0]
        return SPEC_FORMS[1] if self.position is not None else SPEC_FORMS[2]

    @property
    def place(self) -> int:
        """The place, from 0, of the argument that names the spec; 0 for a keyword entry."""
        return self.position if self.position is not None else self.type_argument or 0

    def written(self, writing: Writing, callee: str, value: str) -> str:
        """The call of callee naming the spec value as the language writes it, by writing's `specs` template of the
        entry's form."""
        return writing.spec(self.form, callee, value, self.keyword, self.place)


@dataclass(frozen=True)
class StandIns:
    """The guard stand-ins: the dotted names of the calls that build a mock, of those that build a mock from a spec
    given as an argument (autospec), and the ways a call that builds one names its spec (specs, in the order written:
    a call names it by the first entry it gives, and a fix writes the first entry; an autospec call reads only the
    first keyword entry of them); and the fixtures, whose methods build mocks the same way. The other parameters are
    those of `fakes`."""
    mocks: tuple[tuple[str, ...], ...]
    autospec: tuple[tuple[str, ...], ...]
    specs: tuple[SpecEntry, ...]
    fixtures: tuple[Fixture, ...] = ()


@dataclass(frozen=True)
class Fakes:
    """Where the test fakes live, as a folder below the tests folder (e.g. ("fakes",)), the parts they stand in for,
    and how a fake's name starts (the fake of port X is <prefix>X; empty when the file does not say)."""
    folder: tuple[str, ...]
    stand_in_for: tuple[str, ...]
    prefix: str = ""
