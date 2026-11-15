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

from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.domain.values import Function, Profile, SourceFile, Weak

RULE = "pass-through"


def weak(app: Iterable[SourceFile], profile: Profile) -> list[Weak]:
    if not profile.pass_through:
        return []
    found: list[Weak] = []
    for file in app:
        where = place(profile, dotted(file.path, profile.language.marks)[0])
        if where is None or where.part not in profile.pass_through:
            continue
        for function in file.functions:
            callee = forwards(function)
            if callee and function.owner:
                name = f"{function.owner}.{function.name}"
                found.append(Weak(RULE, file.name, function.line,
                                  f"{name} only passes its arguments on to {callee}",
                                  f"have the caller use {callee}, or keep it as a deliberate plain forward: it stays "
                                  "listed and fails only `check --strict`"))
    return found


def forwards(function: Function) -> str:
    """The dotted callee the function forwards to, or "": see the module's text."""
    call, signature = function.sole_call, function.signature
    dunder = function.name.startswith("__") and function.name.endswith("__")
    if function.decorated or dunder or call is None or not signature.positional:
        return ""
    own, others = signature.positional[0], [*signature.positional[1:], *signature.keyword_only]
    if call.callee[:1] != (own,) or len(call.callee) < 3:
        return ""
    passed: list[str] = []
    for arg in call.args:
        if (signature.star and arg == f"*{signature.star}") or (arg and not arg.startswith("*") and arg in others):
            passed.append(arg)
        else:
            return ""
    for keyword, value in call.keywords:
        if keyword == "**" and signature.double and value == signature.double:
            passed.append(f"**{value}")
        elif keyword != "**" and value in others:
            passed.append(value)
        else:
            return ""
    wanted = [*others, *([f"*{signature.star}"] if signature.star else []),
              *([f"**{signature.double}"] if signature.double else [])]
    return ".".join(call.callee) if sorted(passed) == sorted(wanted) else ""
