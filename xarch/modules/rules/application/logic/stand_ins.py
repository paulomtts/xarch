"""The stand-ins guard: a port is fire-only or read by its signatures, every read port has a fake, and a mock in a
test that may use the fakes names a fire-only port.

A port is a module-level class, in a file of a part the fakes stand in for, with `Protocol` (typing's or
typing_extensions', `Protocol[T]` too) among its bases; any other class there is not a port. Its methods are the
functions of its own body (inherited ones are not followed), dunder methods left out but for __call__, the method a
callable port is; a property, a classmethod or a staticmethod counts as the method it is. By its methods' return
annotations a port is:

    read         any method returns something else than None: the port is written and read back, so it has a fake
    fire-only    every method returns None (`-> None`, or the string "None")
    unannotated  a method has no return annotation: a violation, since the kind follows from it

A port with no methods is neither, and no rule applies to it. A read port X has a fake: a module-level class named
<prefix>X in a file below the fakes' folder (by name only: one fake serves ports of the same name in two instances).

In a test whose tier may import the fakes (see tier_imports), every call of unittest.mock's Mock, MagicMock,
AsyncMock, NonCallableMock or NonCallableMagicMock names its spec, as its first argument, `spec=` or `spec_set=`,
and every create_autospec its first argument or `spec=`; one that names none is a violation. A spec that is a class
of the app, `from <module> import X` or `<module alias>.X`, whose module is a port's file and X a read port there,
is a violation that points to its fake. The check stays silent on what it cannot read: a call that unpacks *args or
**kwargs, a spec that is not a name an absolute import binds (a variable, an expression, a string), a spec imported
from a package that re-exports the port, and a mock built by `patch`.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.tier_imports import may_use_fakes
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Call, Class, Profile, SourceFile

PROTOCOLS = {("typing", "Protocol"), ("typing_extensions", "Protocol")}
MOCK_MODULE = ("unittest", "mock")
MOCKS = {"Mock", "MagicMock", "AsyncMock", "NonCallableMock", "NonCallableMagicMock"}
AUTOSPEC = "create_autospec"
NONE = "None"
GUARD = "(stand-ins)"


@dataclass(frozen=True)
class Port:
    """A port, where it is, and its kind: "fire-only", "read" or None (unannotated, or no methods)."""
    file: str
    module: tuple[str, ...]
    line: int
    name: str
    kind: str | None


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
               has_tests: bool = True) -> list[Violation]:
    """has_tests is whether there is a tests root: without one there are no fakes to look for."""
    if not profile.stand_ins or profile.fakes is None:
        return []
    tests = list(tests)
    found: list[Violation] = []
    ports: dict[tuple[tuple[str, ...], str], Port] = {}
    for file in app:
        where = place(profile, dotted(file.path)[0])
        if where is None or where.part not in profile.fakes.stand_in_for:
            continue
        for cls in file.classes:
            if any(base in PROTOCOLS for base in cls.bases):
                port, problems = _classified(file, cls)
                ports[(port.module, port.name)] = port
                found += problems
    if has_tests:
        found += _missing_fakes(ports.values(), tests, profile)
    found += _mocks(tests, ports, profile, root)
    return found


def _classified(file: SourceFile, cls: Class) -> tuple[Port, list[Violation]]:
    methods = [m for m in cls.methods if not _dunder(m.name) or m.name == "__call__"]
    bare = [m for m in methods if m.returns is None]
    problems = [Violation(file.name, m.line, f"{cls.name}.{m.name} has no return annotation: annotate it, since "
                                             f"whether {cls.name} is fire-only or read follows from it {GUARD}")
                for m in bare]
    kind = None
    if not bare and methods:
        kind = "read" if any(m.returns != NONE for m in methods) else "fire-only"
    return Port(file.name, dotted(file.path)[0], cls.line, cls.name, kind), problems


def _missing_fakes(ports: Iterable[Port], tests: list[SourceFile], profile: Profile) -> list[Violation]:
    assert profile.fakes is not None
    folder = profile.fakes.path
    fakes = {cls.name for t in tests if t.path[:len(folder)] == folder for cls in t.classes}
    shown = "/".join(("tests", *folder)) + "/"
    return [Violation(p.file, p.line, f"{p.name} is a read port with no fake: write {profile.fakes.prefix}{p.name} "
                                      f"under {shown} {GUARD}")
            for p in ports if p.kind == "read" and f"{profile.fakes.prefix}{p.name}" not in fakes]


def _mocks(tests: list[SourceFile], ports: dict[tuple[tuple[str, ...], str], Port], profile: Profile,
           root: str) -> list[Violation]:
    assert profile.fakes is not None
    found: list[Violation] = []
    for file in tests:
        tier = tested(profile, file.path).tier
        if tier is None or not may_use_fakes(profile, tier):
            continue
        for call in file.calls:
            if call.func[:-1] != MOCK_MODULE or call.func[-1] not in (*MOCKS, AUTOSPEC):
                continue
            named, spec = _spec(call)
            if not named:
                found.append(Violation(file.name, call.line, f"{call.func[-1]}() names nothing it stands in for: give "
                                                             f"it a spec, such as Mock(spec=<port>) {GUARD}"))
            elif spec is not None and spec[:1] == (root,):
                port = ports.get((spec[1:-1], spec[-1]))
                if port is not None and port.kind == "read":
                    written = f"{call.func[-1]}(spec={port.name})" if _by_keyword(call) else \
                        f"{call.func[-1]}({port.name})"
                    found.append(Violation(file.name, call.line, f"{written} stands in for {port.name}, a read port: "
                                                                 f"use its fake {profile.fakes.prefix}{port.name} "
                                                                 f"{GUARD}"))
    return found


def _spec(call: Call) -> tuple[bool, tuple[str, ...] | None]:
    """Whether the call names a spec (or may, when it unpacks arguments), and the spec when it is a name."""
    keywords = dict(call.keywords)
    names = ("spec",) if call.func[-1] == AUTOSPEC else ("spec", "spec_set")
    if call.args:
        return True, call.args[0]
    for name in names:
        if name in keywords:
            return True, keywords[name]
    return call.unpacked, None


def _dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def _by_keyword(call: Call) -> bool:
    return not call.args
