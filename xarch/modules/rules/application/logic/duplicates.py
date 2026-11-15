"""The no-duplicates check: two functions of the app whose code is the same once names and formatting are ignored.

Compared are the functions and the methods of the app's files (never the tests': a test's setup and tables repeat on
purpose, and a fake and the adapter it stands in for would be found against each other). Two functions are the same
when their shapes are (see the source tree): the same statements, calls, attributes, constants and keyword names, with
every local name and parameter name numbered by its first appearance, and the docstring, annotations, defaults,
decorators and formatting left out. What a function calls or reads is part of the code, so two functions that each
make one call to something different are different.

Only a function with at least `no_duplicates` real statements counts (nested ones counted, a docstring, `pass` and a
bare `...` not), and one with none (a Protocol stub, a bare docstring) never does, whatever the minimum.

Of every group of functions that match, the first by file name and line is the original: each other one is reported at
its own place, naming the original's.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import Function, Profile, SourceFile

RULE = "no-duplicates"
FIX = ("keep one of the two and import it where the other is, or move it to a part both may import when they cannot "
       "import each other")


def violations(app: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    if profile.no_duplicates is None:
        return []
    least = max(profile.no_duplicates, 1)
    groups: dict[str, list[tuple[SourceFile, Function]]] = {}
    for file in sorted(app, key=lambda f: f.name):
        for function in sorted(file.functions, key=lambda f: f.line):
            if function.statements >= least and function.shape:
                groups.setdefault(function.shape, []).append((file, function))
    found: list[Violation] = []
    for group in groups.values():
        original_file, original = group[0]
        found += [Violation(file.name, function.line,
                            f"{_named(function)} has the same code as {_named(original)} at "
                            f"{original_file.name}:{original.line}, whatever the names ({RULE})", RULE, FIX)
                  for file, function in group[1:]]
    return found


def _named(function: Function) -> str:
    return f"{function.owner}.{function.name}" if function.owner else function.name
