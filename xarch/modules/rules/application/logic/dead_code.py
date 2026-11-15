"""The dead-code check: a port no other file of the app names, and a fake no test names.

A port is what the stand-ins guard calls one (a Protocol class of a part `fakes.for` names). It is used when another
file of the app names it, by any name it reads, in code or in an annotation, whatever the file does with it, so that a
service's `repo: Repo`, an adapter's `Repo` and a call all count. These do not: the port's own file, a package file
(`__init__.py`, which only re-exports), and a file of a part that may import everything, the wiring, which only binds
what others use. A port named only by one of those is reported. Names are compared by their last step alone, so two
ports of one name in two places use each other's mention: a miss, never a false finding.

A fake is a module-level class in a file below the fakes folder whose name starts with the fakes' prefix (every class
there when there is none). It is used when a test file outside that folder names it, or a fake that is itself used
names it; a fake named only by an unused fake, or by itself, is not used. A file of the fakes folder with no class
(such as its `__init__.py`) names nothing. Without a tests folder only ports are read.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.placement import EVERYTHING
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.stand_ins import ports_of
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Profile, SourceFile

RULE = "dead-code"
PACKAGE_FILE = "__init__.py"


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
               has_tests: bool = True) -> list[Violation]:
    if not profile.dead_code or profile.fakes is None:
        return []
    app = list(app)
    found = _dead_ports(app, profile)
    if has_tests:
        found += _dead_fakes(list(tests), profile)
    return found


def _wiring(profile: Profile) -> set[str]:
    return {part for part, targets in profile.rules.items() if any(t.part == EVERYTHING for t in targets)}


def _dead_ports(app: list[SourceFile], profile: Profile) -> list[Violation]:
    wiring = _wiring(profile)
    users = [f for f in app if f.path[-1] != PACKAGE_FILE
             and (where := place(profile, dotted(f.path)[0])) is not None and where.part not in wiring]
    return [Violation(port.file, port.line, f"{port.name} is a port that nothing else in the app names ({RULE})", RULE,
                      f"delete {port.name} and its fake, or add the code that uses it")
            for port in ports_of(app, profile)
            if not any(port.name in f.named for f in users if f.name != port.file)]


def _dead_fakes(tests: list[SourceFile], profile: Profile) -> list[Violation]:
    assert profile.fakes is not None
    folder, prefix = profile.fakes.path, profile.fakes.prefix
    inside = [t for t in tests if t.path[:len(folder)] == folder]
    fakes = [(t, c) for t in inside for c in t.classes if c.name.startswith(prefix) and c.name != prefix]
    used: set[str] = set().union(*(t.named for t in tests if t.path[:len(folder)] != folder))
    grown = True
    while grown:
        grown = False
        for _, cls in fakes:
            if cls.name in used:
                new = cls.named - used
                if new:
                    used |= new
                    grown = True
    return [Violation(file.name, cls.line, f"{cls.name} is a fake that no test names ({RULE})", RULE,
                      f"delete {cls.name}, or write the test that uses it")
            for file, cls in fakes if cls.name not in used]
