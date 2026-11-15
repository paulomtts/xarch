"""The dead-code check: a port no other file of the app names, and a fake no test names.

A port is what the stand-ins guard calls one (an interface class of a part `fakes.for` names). It is used when another
file of the app names it, by any name it reads, in code or in an annotation, whatever the file does with it, so that a
service's `repo: Repo`, an adapter's `Repo` and a call all count. These do not: the port's own file, a package file
(which only re-exports), and a file of a part that may import everything, the wiring, which only binds
what others use. A port named only by one of those is reported. Names are compared by their last step alone, so two
ports of one name in two places use each other's mention: a miss, never a false finding.

A fake is a module-level class in a file below the fakes folder whose name starts with the fakes' prefix (every class
there when there is none). It is used when a test file outside that folder names it, or a fake that is itself used
names it; a fake named only by an unused fake, or by itself, is not used. A file of the fakes folder with no class
(such as its package file) names nothing. Without a tests folder only ports are read.

With `untested`, a file of a part that has a tier is listed as weak, failing `check --strict` only, when no test code
of that tier reaches it. Test code of a tier is a file below the tests root that the tier holds (see tier_of), a test
or not; a file is reached when such test code imports it (`targets` reads the import), or when a reached file of a
part of the same tier imports it, however far that goes: a service a controller's test reaches through the controller
is reached, while a rule of a part of another tier that the service imports is not. Not listed: a package file; a
file that holds no function or method with a real statement, such as one of types, constants or interface stubs; and
a file of exceptions only (every class an exception, see holds, and no function at the top level), which the code
that raises them is tested through.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.placement import EVERYTHING
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.holds import exceptions
from xarch.modules.rules.application.logic.imports import dotted, targets
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.application.logic.stand_ins import ports_of
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.values import Profile, SourceFile, Weak

RULE = "dead-code"


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
    users = [f for f in app if f.path[-1] != profile.language.package_file
             and (where := place(profile, dotted(f.path, profile.language.marks)[0])) is not None and where.part not in wiring]
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


def untested(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str) -> list[Weak]:
    """app holds the files below the root package root, tests those below the tests root, imported as tests_root."""
    if not profile.dead_code or not profile.untested:
        return []
    app = list(app)
    files = {dotted(f.path, profile.language.marks)[0]: f for f in app}
    known = set(files)
    tier_of = {s.part: tier.name for tier in reversed(profile.tiers) for s in tier.subject}
    tiers = {steps: tier_of.get(where.part) for steps in files
             if (where := place(profile, steps)) is not None and where.part is not None}
    reached: set[tuple[tuple[str, ...], str]] = set()
    for test in tests:
        tier = tested(profile, test.path).tier
        if tier is not None:
            absolute = tuple(i for i in test.imports if not i.level)
            reached |= {(target, tier.name) for _, target in targets(absolute, (), known, root)
                        if target in files and tiers.get(target) == tier.name}
    grown = True
    while grown:
        grown = False
        for steps, tier_name in list(reached):
            file = files[steps]
            package = steps if dotted(file.path, profile.language.marks)[1] else steps[:-1]
            for _, target in targets(file.imports, package, known, root):
                if target in files and tiers.get(target) == tier_name and (target, tier_name) not in reached:
                    reached.add((target, tier_name))
                    grown = True
    raised = exceptions(app, root, profile)
    found: list[Weak] = []
    for steps, file in files.items():
        tier_name = tiers.get(steps)
        only_exceptions = bool(file.classes) and all((steps, c.name) in raised for c in file.classes) and not any(
            not f.owner for f in file.functions)
        if (tier_name is None or (steps, tier_name) in reached or dotted(file.path, profile.language.marks)[1] or only_exceptions
                or not any(f.statements for f in file.functions)):
            continue
        where = place(profile, steps)
        assert where is not None
        folder = "/".join((tests_root, *file.path[:-1]))
        found.append(Weak(RULE, file.name, 0, f"a file of {label(profile, where)} that no {tier_name} test reaches "
                                              "(guards.dead-code.untested)",
                          f"write its {tier_name} test in {folder}/, or delete what nothing uses"))
    return found
