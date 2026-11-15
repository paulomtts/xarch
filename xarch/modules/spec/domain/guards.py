"""The pre-built checks a profile may switch on, by the name its `guards` key (or, for package-only, a part's
`package_only: true`) uses, each with the parameters it takes."""
from __future__ import annotations

from xarch.modules.spec.domain.values import (
    ClosedTree,
    DeadCode,
    Guard,
    NoComments,
    NoDuplicates,
    PackageOnly,
    PassThrough,
    ScenarioCoverage,
    StandIns,
)

GUARDS = {
    "package-only": "`package_only: true` on each part: parts that are imported only as a package, never by their "
                    "files, from outside it",
    "scenario-coverage": "{results: <part>, tier: <tier>, suffix: <text>, columns: [<state>, <command>, <result>], "
                         "file: <name>}: every variant of a union named <Name><suffix> in a results part is the "
                         "result column of a row of the table in its use case's test file <file> (`{name}` is "
                         "<Name> in snake_case) of that tier, or is named by a standalone test of it; every row is a "
                         "`testing.table.row` call with a `testing.table.id`, and a table test has no branching; "
                         "read from the syntax tree, never run",
    "no-comments": "{}: no `#` comments in the app or its tests, whole-line or trailing; docstrings stay, and so do "
                   "`# type: ignore`, `# noqa`, `# pragma:`, a shebang and an encoding line",
    "stand-ins": "{}: every Protocol in a part `fakes` stands in for is fire-only (every method returns None) or read "
                 "(any one returns a value), each method annotated; every read port has a fake <prefix><Port> in "
                 "`fakes.folder`; and a test of a tier that may import the fakes gives every mock (`testing.mocks`) "
                 "a spec, never a read port's; silent where it cannot read the code: `*args`, a spec that is a "
                 "variable, a re-exported port, mocks made by `patch`",
    "closed-tree": "{}: every Python file of the app lies in a part or is the package file of a folder of the layout; "
                   "off unless switched on, since a profile is a protocol, not a closed world; a folder the profile "
                   "`excluded` is not looked at",
    "no-duplicates": "{min_statements: <number>}: no two functions or methods of the app (never its tests) have the "
                     "same code: the same tree once formatting, docstrings, annotations, defaults, decorators and "
                     "local names are ignored, so the same statements, calls, attributes, constants, keyword names, "
                     "async or not, and number of parameters; what is called is part of it. A function counts when "
                     "it holds at least min_statements statements (nested ones counted; 4 when left out). The first "
                     "by file and line is the original; each other is reported naming it",
    "dead-code": "{}: every port (a Protocol in a part `fakes.for` names) is named by another file of the app, in code "
                 "or an annotation, and every fake (a top-level class of the fakes folder whose name starts with "
                 "`prefix`) is named by a test outside that folder or by a fake that is itself used. The port's own "
                 "file, package files and the wiring (a part that may import `everything`) do not count; names are "
                 "compared by their last step",
    "pass-through": "{parts: [<part>, ...]}: a method of those parts whose whole body (a docstring aside) is one "
                    "`return` or bare statement of one call, perhaps awaited, on a chain of at least two attributes "
                    "of its own first parameter (`self.repo.get(...)`), passing every other parameter straight "
                    "through and nothing more, is listed as `weak` in the enforcement section and fails `check "
                    "--strict` only. Any other statement, a changed, extra or dropped argument, a decorator, a "
                    "dunder method, a function outside a class or a call on something not held by the object "
                    "(`self.helper(...)`) is not one",
}
"""The pre-built checks a profile may switch on, each with the parameters it takes."""
_GUARD_NAMES: dict[type, str] = {PackageOnly: "package-only", ScenarioCoverage: "scenario-coverage",
                                 NoComments: "no-comments", StandIns: "stand-ins", ClosedTree: "closed-tree",
                                 NoDuplicates: "no-duplicates", DeadCode: "dead-code", PassThrough: "pass-through"}


def guard_name(guard: Guard) -> str:
    """The name a profile switches the guard on by, one of GUARDS."""
    return _GUARD_NAMES[type(guard)]
