"""The pass-through check: a method of a listed part that only forwards to one call, listed without failing.

A method forwards when it has no decorator, is no dunder method, and its whole body (a docstring aside) is one `return`
or bare statement of one call, perhaps awaited, on an attribute of its own first parameter (`self.repo.get(...)`, a
chain of at least two attributes), passing each of its other parameters straight through and nothing else. Any other
statement, condition, extra call, changed, extra or missing argument, or a read of the result, means it is not one; so
does a call on something that is not held by the object (`self.helper(...)`, a global, another parameter). A function
at module level never forwards, since it has no first parameter to hold a collaborator.

It is listed in the enforcement section like a weak check and fails `check --strict` only: a pure forward is often
what a simple read is, and failing on it would push filler code into the method.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import place
from xarch.modules.rules.domain.values import Profile, SourceFile, Weak

RULE = "pass-through"


def weak(app: Iterable[SourceFile], profile: Profile) -> list[Weak]:
    if not profile.pass_through:
        return []
    found: list[Weak] = []
    for file in app:
        where = place(profile, dotted(file.path)[0])
        if where is None or where.part not in profile.pass_through:
            continue
        for function in file.functions:
            if function.forwards and function.owner:
                name = f"{function.owner}.{function.name}"
                found.append(Weak(RULE, file.name, function.line,
                                  f"{name} only passes its arguments on to {function.forwards}",
                                  f"have the caller use {function.forwards}, or keep it as a deliberate plain forward: it stays "
                                  "listed and fails only `check --strict`"))
    return found
