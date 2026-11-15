"""The private-imports check: no file of the app or of its tests imports a private name from another file of them.

A private name is one that starts with `_` and is no dunder name (`__version__` is not private). The imports read
are `from <m> import <name>` where m is a relative import, or an absolute one of the app's package or the tests'
package: the import of a whole file (`import a._b`), whatever its name, and a name of an outside package or of the
standard library are not this check's business. Each private name is reported on the line of its import.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.values import Profile, SourceFile

RULE = "private-imports"


def violations(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
               tests_root: str) -> list[Violation]:
    """app holds the files below the root package root, tests those below the package tests_root."""
    if not profile.private_imports:
        return []
    found: list[Violation] = []
    for file in [*app, *tests]:
        for imp in file.imports:
            if imp.names is None or not (imp.relative or imp.module[:1] in ((root,), (tests_root,))):
                continue
            found += [Violation(file.name, imp.line, f"imports the private name {name} from {imp.written} ({RULE})", RULE,
                                f"make {name} public where it is defined (drop the `_`), or move it to a file both "
                                "may import")
                      for name in imp.names if _private(name)]
    return found


def _private(name: str) -> bool:
    return name.startswith("_") and not (name.startswith("__") and name.endswith("__"))
