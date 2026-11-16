"""Whether a method only passes its arguments on, the pass-through guard's question, from the facts the reader records
of a function: a method forwards to the callee of its one call when it has no decorator, is no special method of the
language, and its whole body is that call on a chain of at least two attributes of its first parameter
(`self.repo.get(...)`), passing each of its other parameters straight through (a `*args` as `*args`, a `**kwargs` as
`**kwargs`) and nothing else. A function of no class forwards nothing.
"""
from __future__ import annotations

from xarch.modules.rules.domain.values import Function
from xarch.profile_values.language import CheckedLanguage


def forwards(function: Function, language: CheckedLanguage) -> str:
    """The dotted callee a method only passes its arguments on to, or "" (see the module)."""
    signature, call = function.signature, function.sole_call
    if (not function.owner or function.decorated or language.is_special(function.name) or call is None
            or not signature.positional):
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
