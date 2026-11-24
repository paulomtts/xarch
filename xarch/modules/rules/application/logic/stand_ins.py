"""The stand-ins guard: a port is fire-only or read by its signatures, every read port has a fake, and a mock in a
test that may use the fakes names a fire-only port.

A port is a module-level class, in a file of a part the fakes stand in for, that the reader marks as an interface (by
the marks of its data file's `interface`); any other class there is not a port. Its
methods are the functions of its own body (inherited ones are not followed), the language's special methods left
out but for the one calling an instance runs (its data file's `call`), the method a callable port is; a method the
language marks as a property or as bound to the class counts as the method it is. By its methods' return annotations a
port is:

    read         some method gives a value: the port is written and read back, so it has a fake
    fire-only    every method gives no value: its annotation is one the data file's `nothing` lists, or it has none
                 and the data file says `unannotated: nothing`
    unannotated  a method has no return annotation, and the data file does not say `unannotated`: a violation, since
                 the kind follows from it

A port with no methods is neither, and no rule applies to it. A read port X has a fake: a module-level class named
<prefix>X in a file below the fakes' folder (by name only: one fake serves ports of the same name in two instances).

In a test whose tier may import the fakes (see tier_imports), every call of one of the profile's mocks names its
spec, as its argument at the profile's spec_position (when the profile gives one) or by one of the profile's spec
keywords, and every call of one of its autospec functions as that argument or by the first spec keyword; one that
names none is a violation. A spec that is a class
of the app, a name X taken from a module or read as an attribute of a module imported whole, whose module is a port's
file and X a read port there, is a violation that points to its fake.

A mock may also come from a fixture: a parameter of a function, named in the profile's `fixtures`, whose methods build
mocks. A call of `<parameter>.<method>` for a method the fixture lists under `mocks` follows exactly the rules of the
profile's mocks, and one listed under `autospec` those of its autospec functions; it is shown as written: the
parameter and the method, joined by a dot.

The check stays silent on what it cannot read: a call that unpacks its arguments, a spec that is not a name an
import binds (a variable, an expression, a string), a spec imported from a package that re-exports the port,
a mock built by a function the profile does not list among its mocks or autospec functions, and a fixture the function
rebinds (the source tree reports only a parameter its function's signature alone binds), reaches through a longer
chain of attributes, or calls itself.

weak lists, without failing, a fake that meets the rule to the letter only: a class <prefix>X below the fakes' folder
that does not define, in its own body, every method port X declares (its methods as above), where a name its body
assigns, or its methods assign on the object they are called on, counts as defined. Fakes are matched by name, so a
fake is weak only when it falls short of every port of its name, and is shown against the one it comes closest to.
Inherited methods are not followed, so a fake that subclasses its port, whose bodies do nothing, is weak.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import file_place
from xarch.modules.rules.application.logic.tier_of import may_use_fakes, tested
from xarch.modules.rules.domain.parsed import Call, Class, ParameterCall, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.profile_values.testing import StandIns

RULE = "stand-ins"
GUARD = f"({RULE})"


@dataclass(frozen=True)
class _Port:
    """A port, where it is, and its kind: "fire-only", "read" or None (unannotated, or no methods)."""
    file: str
    module: tuple[str, ...]
    line: int
    name: str
    kind: str | None
    methods: tuple[str, ...] = ()


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
               tests_root: str | None) -> list[Violation]:
    """tests_root names the tests root, None when there is none: without one there are no fakes to look for."""
    if profile.stand_ins is None or profile.fakes is None:
        return []
    tests = list(tests)
    ports, found = _ports(app, profile)
    if tests_root is not None:
        found += _missing_fakes(ports.values(), tests, profile, tests_root)
    found += _mocks(tests, ports, profile, root)
    return found


def weak(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Weak]:
    if profile.stand_ins is None or profile.fakes is None:
        return []
    folder, prefix = profile.fakes.folder, profile.fakes.prefix
    ports, _ = _ports(app, profile)
    found: list[Weak] = []
    for test in tests:
        if test.beside or test.path[:len(folder)] != folder:
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


def _ports(app: Iterable[SourceFile], profile: Profile) -> tuple[dict[tuple[tuple[str, ...], str], _Port],
                                                                 list[Violation]]:
    """The ports of the parts the fakes stand in for, by module and name, and the problems of their annotations."""
    assert profile.fakes is not None
    found: list[Violation] = []
    ports: dict[tuple[tuple[str, ...], str], _Port] = {}
    for file in app:
        where = file_place(profile, file.path)
        if where is None or where.part not in profile.fakes.stand_in_for:
            continue
        for cls in file.classes:
            if cls.interface:
                port, problems = _classified(file, cls, profile)
                ports[(port.module, port.name)] = port
                found += problems
    return ports, found


def _classified(file: SourceFile, cls: Class, profile: Profile) -> tuple[_Port, list[Violation]]:
    language = profile.language
    methods = [m for m in cls.methods if not language.is_special(m.name) or m.name == language.call]
    bare = [m for m in methods if m.returns is None and not language.gives_nothing(m.returns)]
    problems = [Violation(file.name, m.line, f"{cls.name}.{m.name} has no return annotation, and whether {cls.name} "
                                             f"is fire-only or read follows from it {GUARD}",
                          RULE, f"annotate what {cls.name}.{m.name} returns")
                for m in bare]
    kind = None
    if not bare and methods:
        kind = "fire-only" if all(language.gives_nothing(m.returns) for m in methods) else "read"
    module = dotted(file.path, profile.language.marks)[0]
    return _Port(file.name, module, cls.line, cls.name, kind, tuple(m.name for m in methods)), problems


def _missing_fakes(ports: Iterable[_Port], tests: list[SourceFile], profile: Profile,
                   tests_root: str) -> list[Violation]:
    assert profile.fakes is not None
    folder = profile.fakes.folder
    fakes = {cls.name for t in tests if not t.beside and t.path[:len(folder)] == folder for cls in t.classes}
    shown = "/".join((tests_root, *folder)) + "/"
    return [Violation(p.file, p.line, f"{p.name} is a read port with no fake {GUARD}", RULE,
                      f"write {profile.fakes.prefix}{p.name} under {shown}")
            for p in ports if p.kind == "read" and f"{profile.fakes.prefix}{p.name}" not in fakes]


def _mocks(tests: list[SourceFile], ports: dict[tuple[tuple[str, ...], str], _Port], profile: Profile,
           root: str) -> list[Violation]:
    assert profile.fakes is not None and profile.stand_ins is not None
    found: list[Violation] = []
    for file in tests:
        tier = tested(profile, file.path, file.beside).tier
        if tier is None or not may_use_fakes(profile, tier):
            continue
        for mock in _built(file, profile.stand_ins):
            found += _mock(file, mock, ports, profile, root)
    return found


@dataclass(frozen=True)
class _Built:
    """A call that builds a mock: the call as the source tree read it (of an imported name, or of a fixture's method),
    how it is shown (the name called, or for a fixture's the parameter and the method joined by a dot), and whether it
    is an autospec, which takes its spec by
    the argument at the profile's position or by the first spec keyword only."""
    made: Call | ParameterCall
    shown: str
    autospec: bool


def _built(file: SourceFile, names: StandIns) -> list[_Built]:
    """The calls of the file that build a mock, those of imported names first, then those of a fixture's methods."""
    found = [_Built(c, c.func[-1], c.func in names.autospec)
             for c in file.calls if c.func in names.mocks or c.func in names.autospec]
    for call in file.parameter_calls:
        for fixture in names.fixtures:
            if call.parameter == fixture.name and call.method in (*fixture.mocks, *fixture.autospec):
                found.append(_Built(call, f"{call.parameter}.{call.method}", call.method in fixture.autospec))
    return found


def _mock(file: SourceFile, mock: _Built, ports: dict[tuple[tuple[str, ...], str], _Port], profile: Profile,
          root: str) -> list[Violation]:
    assert profile.fakes is not None and profile.stand_ins is not None
    names = profile.stand_ins
    prefix = mock.shown.rpartition(".")[0]
    constructor = f"{prefix}." if prefix else ""
    suggested = f"{constructor}{names.mocks[0][-1]}({names.spec[0]}=<port>)"
    named, spec, placed = _spec(mock, names.spec[:1] if mock.autospec else names.spec, names.spec_position)
    if not named:
        return [Violation(file.name, mock.made.line, f"{mock.shown}() names nothing it stands in for {GUARD}", RULE,
                          f"give it a spec, such as {suggested}")]
    if spec is not None and spec[:1] == (root,):
        port = ports.get((spec[1:-1], spec[-1]))
        if port is not None and port.kind == "read":
            before = "..., " * (names.spec_position or 0)
            written = f"{mock.shown}({before}{port.name})" if placed else \
                f"{mock.shown}({names.spec[0]}={port.name})"
            return [Violation(file.name, mock.made.line, f"{written} stands in for {port.name}, a read port {GUARD}", RULE,
                              f"use its fake {profile.fakes.prefix}{port.name}")]
    return []


def _spec(call: _Built, names: tuple[str, ...], position: int | None) -> tuple[bool, tuple[str, ...] | None, bool]:
    """Whether the call names a spec (or may, when it unpacks arguments), by its argument at position (None: by no
    argument) or one of the keywords names; the spec when it is a name; and whether the argument at position names it."""
    made = call.made
    keywords = dict(made.keywords)
    if position is not None and len(made.args) > position:
        return True, made.args[position], True
    for name in names:
        if name in keywords:
            return True, keywords[name], False
    return made.unpacked, None, False


