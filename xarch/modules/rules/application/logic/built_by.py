"""The built-by check: only the parts a part lists in `built_by` call the constructor of a class defined in it.

A class of the part is one defined at the top level of a file of it. A call builds it when its callee, read through the
absolute import that binds its first name (see the Call value), is that file's dotted path and then the class's name:
`X(...)` after `from <file> import X`, `m.X(...)` after `from <package> import <file> as m`. A call of anything below
the class, such as `X.build(...)`, is not read; nor is a class reached through a package file that re-exports it, one
built in its own file, or one built through a variable or a parameter. Every file of the app is read, the part's own
files included; tests are not.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.placement import Place
from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile

RULE = "built-by"


def violations(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    """app holds the files below the root package root."""
    if not profile.built_by:
        return []
    app = list(app)
    classes: dict[tuple[str, ...], tuple[str, Place]] = {}
    for file in app:
        steps, _ = dotted(file.path)
        where = place(profile, steps)
        if where is not None and where.part in profile.built_by:
            classes.update({(root, *steps, c.name): (where.part, where) for c in file.classes})
    found: list[Violation] = []
    for file in app:
        src = place(profile, dotted(file.path)[0])
        for call in file.calls:
            if call.func not in classes:
                continue
            part, at = classes[call.func]
            if src is not None and src.part in profile.built_by[part]:
                continue
            builders = " or ".join(f"{p}/" for p in profile.built_by[part])
            built = label(profile, at)
            who = label(profile, src) if src is not None else "code in no part"
            found.append(Violation(file.name, call.line, f"{who} builds {call.func[-1]}, a class of {built}, which "
                                                         f"only {builders} may build (parts.{part}.built_by)", RULE,
                                   f"take {call.func[-1]} as a parameter of the constructor, and build it in "
                                   f"{builders}"))
    return found
