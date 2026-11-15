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

In a test whose tier may import the fakes (see tier_imports), every call of one of the profile's mocks names its
spec, as its first argument or by one of the profile's spec keywords, and every call of one of its autospec
functions its first argument or the first spec keyword; one that names none is a violation. A spec that is a class
of the app, `from <module> import X` or `<module alias>.X`, whose module is a port's file and X a read port there,
is a violation that points to its fake. The check stays silent on what it cannot read: a call that unpacks *args or
**kwargs, a spec that is not a name an absolute import binds (a variable, an expression, a string), a spec imported
from a package that re-exports the port, and a mock built by `patch`.

weak lists, without failing, a fake that meets the rule to the letter only: a class <prefix>X below the fakes' folder
that does not define, in its own body, every method port X declares (its methods as above), where a name its body or
its methods assign (`size = 0`, `self.size = ...`) counts as defined. Fakes are matched by name, so a fake is weak
only when it falls short of every port of its name, and is shown against the one it comes closest to. Inherited methods
are not followed, so a fake that subclasses its port, whose bodies are `...`, is weak.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.tier_imports import may_use_fakes
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Call, Class, Profile, SourceFile, Weak

PROTOCOLS = {("typing", "Protocol"), ("typing_extensions", "Protocol")}
NONE = "None"
RULE = "stand-ins"
GUARD = f"({RULE})"


@dataclass(frozen=True)
class Port:
    """A port, where it is, and its kind: "fire-only", "read" or None (unannotated, or no methods)."""
    file: str
    module: tuple[str, ...]
    line: int
    name: str
    kind: str | None
    methods: tuple[str, ...] = ()


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
               has_tests: bool = True) -> list[Violation]:
    """has_tests is whether there is a tests root: without one there are no fakes to look for."""
    if profile.stand_ins is None or profile.fakes is None:
        return []
    tests = list(tests)
    ports, found = _ports(app, profile)
    if has_tests:
        found += _missing_fakes(ports.values(), tests, profile)
    found += _mocks(tests, ports, profile, root)
    return found


def weak(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Weak]:
    if profile.stand_ins is None or profile.fakes is None:
        return []
    folder, prefix = profile.fakes.path, profile.fakes.prefix
    ports, _ = _ports(app, profile)
    found: list[Weak] = []
    for test in tests:
        if test.path[:len(folder)] != folder:
            continue
        for cls in test.classes:
            defined = {m.name for m in cls.methods} | set(cls.attributes)
            gaps = [([m for m in port.methods if m not in defined], port) for port in ports.values()
                    if cls.name == f"{prefix}{port.name}"]
            if gaps and all(missing for missing, _ in gaps):
                missing, port = min(gaps, key=lambda gap: len(gap[0]))
                found.append(Weak(RULE, test.name, cls.line, f"{cls.name} does not define {', '.join(missing)}, "
                                                             f"which {port.name} declares ({port.file})"))
    return found


def _ports(app: Iterable[SourceFile], profile: Profile) -> tuple[dict[tuple[tuple[str, ...], str], Port],
                                                                 list[Violation]]:
    """The ports of the parts the fakes stand in for, by module and name, and the problems of their annotations."""
    assert profile.fakes is not None
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
    return ports, found


def _classified(file: SourceFile, cls: Class) -> tuple[Port, list[Violation]]:
    methods = [m for m in cls.methods if not _dunder(m.name) or m.name == "__call__"]
    bare = [m for m in methods if m.returns is None]
    problems = [Violation(file.name, m.line, f"{cls.name}.{m.name} has no return annotation: annotate it, since "
                                             f"whether {cls.name} is fire-only or read follows from it {GUARD}",
                          RULE, f"annotate what {cls.name}.{m.name} returns")
                for m in bare]
    kind = None
    if not bare and methods:
        kind = "read" if any(m.returns != NONE for m in methods) else "fire-only"
    return Port(file.name, dotted(file.path)[0], cls.line, cls.name, kind, tuple(m.name for m in methods)), problems


def _missing_fakes(ports: Iterable[Port], tests: list[SourceFile], profile: Profile) -> list[Violation]:
    assert profile.fakes is not None
    folder = profile.fakes.path
    fakes = {cls.name for t in tests if t.path[:len(folder)] == folder for cls in t.classes}
    shown = "/".join(("tests", *folder)) + "/"
    return [Violation(p.file, p.line, f"{p.name} is a read port with no fake: write {profile.fakes.prefix}{p.name} "
                                      f"under {shown} {GUARD}", RULE, f"write {profile.fakes.prefix}{p.name} under {shown}")
            for p in ports if p.kind == "read" and f"{profile.fakes.prefix}{p.name}" not in fakes]


def _mocks(tests: list[SourceFile], ports: dict[tuple[tuple[str, ...], str], Port], profile: Profile,
           root: str) -> list[Violation]:
    assert profile.fakes is not None and profile.stand_ins is not None
    names = profile.stand_ins
    shown = f"{names.mocks[0][-1]}({names.spec[0]}=<port>)"
    found: list[Violation] = []
    for file in tests:
        tier = tested(profile, file.path).tier
        if tier is None or not may_use_fakes(profile, tier):
            continue
        for call in file.calls:
            if call.func not in names.mocks and call.func not in names.autospec:
                continue
            named, spec = _spec(call, names.spec[:1] if call.func in names.autospec else names.spec)
            if not named:
                found.append(Violation(file.name, call.line, f"{call.func[-1]}() names nothing it stands in for: give "
                                                             f"it a spec, such as {shown} {GUARD}", RULE,
                                       f"give it a spec, such as {shown}"))
            elif spec is not None and spec[:1] == (root,):
                port = ports.get((spec[1:-1], spec[-1]))
                if port is not None and port.kind == "read":
                    written = f"{call.func[-1]}({names.spec[0]}={port.name})" if _by_keyword(call) else \
                        f"{call.func[-1]}({port.name})"
                    found.append(Violation(file.name, call.line, f"{written} stands in for {port.name}, a read port: "
                                                                 f"use its fake {profile.fakes.prefix}{port.name} "
                                                                 f"{GUARD}", RULE,
                                           f"use its fake {profile.fakes.prefix}{port.name}"))
    return found


def _spec(call: Call, names: tuple[str, ...]) -> tuple[bool, tuple[str, ...] | None]:
    """Whether the call names a spec (or may, when it unpacks arguments), by its first argument or one of the keywords
    names, and the spec when it is a name."""
    keywords = dict(call.keywords)
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
