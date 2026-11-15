"""The pass-through check: a method of a listed part that only forwards to one call, listed without failing.

A method forwards when it has no decorator, is no dunder method, and its whole body (a docstring aside) is one `return`
or bare statement of one call, perhaps awaited, on an attribute of its own first parameter (`self.repo.get(...)`, a
chain of at least two attributes), passing each of its other parameters straight through and nothing else; or one
`return` of a chain of attributes read on the result of such a call (`return self.spec.skeleton(profile).language`),
which hands back a piece of what the collaborator answered and decides nothing either. Any other statement,
condition, extra call (a method called on the result included), changed, extra or missing argument, or any other use
of the result (an item of it, an operator, a call on it) means it is not one; so does a call on something that is not
held by the object (`self.helper(...)`, a global, another parameter). A function at module level never forwards,
since it has no first parameter to hold a collaborator.

It is listed in the enforcement section like a weak check and fails `check --strict` only: a pure forward is often
what a simple read is, and failing on it would push filler code into the method.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Weak
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.domain.values import Function, Profile, SourceFile

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
            if callee and function.owner and function.sole_call is not None:
                name = f"{function.owner}.{function.name}"
                then = ".".join(function.sole_call.then)
                said, use = (f" and returns its .{then}", f"{callee}(...).{then}") if then else ("", callee)
                found.append(Weak(RULE, file.name, function.line,
                                  f"{name} only passes its arguments on to {callee}{said}",
                                  f"have the caller use {use}, or keep it as a deliberate plain forward: it stays "
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
