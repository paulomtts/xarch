"""The must-import check: a part that lists `must_import` holds code that touches something outside itself.

A file of such a part satisfies it when it imports one of the listed targets (a part, in the importer's instance or any,
as `may_import` writes them), or an outside package: a top-level package that is neither the standard library nor the
app's own, whatever the part's `libraries` say, since that is the check of `libraries`. A file also satisfies it when it
imports a file of its own part and instance that satisfies it, however far that chain goes: it reaches the technology
through a sibling. Two files that only import each other satisfy nothing.

Exempt: a package marker (`__init__.py`), and a file that holds no function or method with a real statement, such as a
file of types or constants, or of Protocol stubs: it has no code that could touch anything.

A file that fails is reported once, for the file as a whole.
"""
from __future__ import annotations

import sys
from collections.abc import Iterable

from xarch.kernel.logic.placement import reaches
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.imports import dotted, targets
from xarch.modules.rules.domain.places import label, place
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
    grown = True
    while grown:
        grown = False
        for steps, siblings in links.items():
            if steps not in touching and any(s in touching for s in siblings):
                touching.add(steps)
                grown = True
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
