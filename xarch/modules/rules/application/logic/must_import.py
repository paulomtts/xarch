"""The must-import check: a part that lists `must_import` holds code that touches something outside itself.

A file of such a part satisfies it when it imports one of the listed targets (a part, in the importer's instance or any,
as `may_import` writes them), or an outside package: a top-level package that is neither the standard library nor the
app's own, whatever the part's `libraries` say, since that is the check of `libraries`. A file also satisfies it when it
imports a file of its own part and instance that satisfies it, however far that chain goes: it reaches the technology
through a sibling. Two files that only import each other satisfy nothing.

Exempt: a package marker (`__init__.py`), and a file that holds no function or method with a real statement, such as a
file of types or constants, or of Protocol stubs: it has no code that could touch anything.

A file that fails is reported once, for the file as a whole.

A tier that lists `must_import` holds each of its test files (a file below the tests root its tier holds, whose name
the profile's test files match) to reaching one of the listed parts, in any instance: through an absolute import into
the app, or through test code it imports that is no test file (a helper, a builder, a fake) and reaches one, however
far that chain goes; a test file it imports is no way there. Exempt is a test file that holds no function or method
with a real statement. Silent on what a test is handed without importing it, such as a fixture its framework passes.
"""
from __future__ import annotations

import sys
from collections.abc import Iterable

from xarch.kernel.logic.placement import reaches
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted, targets
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.application.logic.tier_of import is_test, tested
from xarch.modules.rules.domain.values import Profile, SourceFile

RULE = "must-import"
PACKAGE_FILE = "__init__.py"


def violations(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    if not profile.must_import:
        return []
    parsed = [(f, *dotted(f.path)) for f in files]
    known = {steps for _, steps, _ in parsed}
    checked = [(file, steps, is_package) for file, steps, is_package in parsed
               if (src := place(profile, steps)) is not None and src.part in profile.must_import]
    touching: set[tuple[str, ...]] = set()
    links: dict[tuple[str, ...], list[tuple[str, ...]]] = {}
    for file, steps, is_package in checked:
        src = place(profile, steps)
        assert src is not None and src.part is not None
        wanted = profile.must_import[src.part]
        package = steps if is_package else steps[:-1]
        reached = [target for _, target in targets(file.imports, package, known, root)]
        places = [(target, place(profile, target)) for target in reached]
        if any(_outside(imp.module, imp.level, root) for imp in file.imports) or any(
                found is not None and any(reaches(t, src, found) for t in wanted) for _, found in places):
            touching.add(steps)
        links[steps] = [target for target, found in places if found is not None and found.part == src.part
                        and found.instance == src.instance and target != steps]
    _spread(touching, links)
    found_violations: list[Violation] = []
    for file, steps, _ in checked:
        src = place(profile, steps)
        assert src is not None and src.part is not None
        if steps in touching or file.path[-1] == PACKAGE_FILE or not any(f.statements for f in file.functions):
            continue
        shown = " or ".join(dict.fromkeys(f"{t.part}/" for t in profile.must_import[src.part]))
        found_violations.append(Violation(
            file.name, 0, f"{label(profile, src)} imports nothing from {shown} and no outside package, so it touches "
                          f"no technology (parts.{src.part}.must_import)", RULE,
            f"import what it wraps from {shown}, or an outside package, or move its code to a part that needs no "
            "technology"))
    return found_violations


def _outside(module: tuple[str, ...], level: int, root: str) -> bool:
    return not level and bool(module) and module[0] != root and module[0] not in sys.stdlib_module_names


def tier_violations(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
                    tests_root: str) -> list[Violation]:
    """tests are the files below the tests root, imported as the package tests_root; app the app's files, below the
    root package root."""
    if not any(tier.must_import for tier in profile.tiers):
        return []
    known_app = {dotted(f.path)[0] for f in app}
    parsed = [(f, *dotted(f.path)) for f in tests]
    known = {steps for _, steps, _ in parsed}
    helpers = {steps for f, steps, _ in parsed if not is_test(profile, f.path)}
    wanted = {tier.name: tier.must_import for tier in profile.tiers}
    touching: dict[str, set[tuple[str, ...]]] = {name: set() for name, parts in wanted.items() if parts}
    links: dict[tuple[str, ...], list[tuple[str, ...]]] = {}
    for file, steps, is_package in parsed:
        package = steps if is_package else steps[:-1]
        absolute = tuple(i for i in file.imports if not i.level)
        reached = {found.part for _, target in targets(absolute, (), known_app, root)
                   if (found := place(profile, target)) is not None}
        for name, parts in wanted.items():
            if name in touching and reached & set(parts):
                touching[name].add(steps)
        links[steps] = [target for _, target in targets(file.imports, package, known, tests_root) if target in helpers]
    found: list[Violation] = []
    for name, reaching in touching.items():
        _spread(reaching, links)
        shown = " or ".join(f"{p}/" for p in wanted[name])
        for file, steps, _ in parsed:
            where = tested(profile, file.path)
            if (where.tier is None or where.tier.name != name or not where.is_test or steps in reaching
                    or not any(f.statements for f in file.functions)):
                continue
            found.append(Violation(file.name, 0, f"a{'n' if name[:1] in 'aeiou' else ''} {name} test imports nothing "
                                                 f"from {shown}, directly or through test code it imports "
                                                 f"(tiers.{name}.must_import)", RULE,
                                   f"drive what it proves through {shown}, or move it to the tier of the part it calls "
                                   "directly"))
    return found


def _spread(touching: set[tuple[str, ...]], links: dict[tuple[str, ...], list[tuple[str, ...]]]) -> None:
    """Add to touching every file that imports, through the links, however far, a file that touches."""
    grown = True
    while grown:
        grown = False
        for steps, linked in links.items():
            if steps not in touching and any(s in touching for s in linked):
                touching.add(steps)
                grown = True
