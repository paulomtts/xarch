"""The pre-built checks a profile may switch on, by the name its `guards` key (or, for package-only, a part's
`package_only: true`) uses, each with the parameters it takes."""
from __future__ import annotations

from xarch.modules.spec.domain.values import (
    ClosedTree,
    Guard,
    NoComments,
    PackageOnly,
    ScenarioCoverage,
    StandIns,
)

GUARDS = {
    "package-only": "`package_only: true` on each part: parts that are imported only as a package, never by their "
                    "files, from outside it",
    "scenario-coverage": "{results: <part>, tier: <tier>, suffix: <text>, columns: [<state>, <command>, <result>], "
                         "file: <name>}: every variant of a union named <Name><suffix> in a results part is the "
                         "result column of a row of the table in its use case's test file <file> of that tier; every "
                         "row is a `testing.table.row` call with a `testing.table.id`, and a table test has no "
                         "branching",
    "no-comments": "{}: no `#` comments in the app or its tests; docstrings and tool directives stay",
    "stand-ins": "{}: every Protocol in a part `fakes` stands in for is fire-only (every method returns None) or read "
                 "(any one returns a value), each method annotated; every read port has a fake <prefix><Port> in "
                 "`fakes.folder`; and a test of a tier that may import the fakes gives every mock (`testing.mocks`) "
                 "a spec, never a read port's",
    "closed-tree": "{}: every Python file of the app lies in a part or is the package file of a folder of the layout; "
                   "off unless switched on, since a profile is a protocol, not a closed world",
}
"""The pre-built checks a profile may switch on, each with the parameters it takes."""
_GUARD_NAMES: dict[type, str] = {PackageOnly: "package-only", ScenarioCoverage: "scenario-coverage",
                                 NoComments: "no-comments", StandIns: "stand-ins", ClosedTree: "closed-tree"}


def guard_name(guard: Guard) -> str:
    """The name a profile switches the guard on by, one of GUARDS."""
    return _GUARD_NAMES[type(guard)]
