"""The package-only guard: a part it names is imported as a package, `from <its package> import <name>`, never by
one of its files, from anywhere outside that part's own folder (its own instance, for a part in the `each` folder).

`from <its package> import <file>` imports a file too, so it is a violation when <file> is one of the app's files.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.imports import dotted, targets
from xarch.modules.rules.domain.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
               root: str) -> list[Violation]:
    """app holds the app's files, below the root package root; tests the test files, whose relative imports are
    their own."""
    if not profile.package_only:
        return []
    app = list(app)
    known = {dotted(f.path)[0] for f in app}
    found: list[Violation] = []
    for file, in_app in [*((f, True) for f in app), *((f, False) for f in tests)]:
        steps, is_package = dotted(file.path)
        src = place(profile, steps) if in_app else None
        imports = file.imports if in_app else tuple(i for i in file.imports if not i.level)
        for line, target in targets(imports, steps if is_package else steps[:-1], known, root):
            dst = place(profile, target)
            if dst is None or dst.part not in profile.package_only or not dst.sub:
                continue
            if src is not None and src.part == dst.part and src.instance == dst.instance:
                continue
            package = ".".join((root, *target[:len(target) - len(dst.sub)]))
            found.append(Violation(file.name, line, f"{label(profile, dst)} is imported only as a package: import "
                                                    f"from {package} ({'.'.join((root, *target))}) (package-only)"))
    return found
