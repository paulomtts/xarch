"""The types-only check: a test of a tier that names parts in `types_only` may import them and use them as types, but
never call what it imports from them, and never reference a function of them at all.

A call is read through the import that binds its callee's first name (see the Call value): `X(...)` after `from
<part> import X [as Y]`, `m.X(...)` after `from <package> import <module of part> [as m]` or `import <module> as m`,
and the full dotted path after `import <module>`. A callee bound any other way (a parameter, an assignment, a
relative import) is not read, so a fake handed in as a parameter typed with the real class is fine.

A function is not a type, so a name that an import binds to a module-level function of such a part, `f = X; f(...)`
or `map(X, rows)` or `X.cache_clear`, is reported wherever it is read (see the Use value): a use whose path reaches
`<module of the part>.<name>`, where the source tree says the module defines the name as a function (see the
SourceFile value's module_functions). A reference to a class stays allowed (`isinstance`, exception matching, enum
members), and so does a module as a whole. It stays silent where the source tree cannot say what a name is: a name
that reaches a package which re-exports it, a name of a file it did not read, a name its module binds more than once.
A call already reported as a call is not reported again as a reference.

A part that lists parts in its own `types_only` is held to the same rule, read the same way, in each of its files:
its code may import those parts to annotate, for `isinstance` and exception matching, but never call what it reaches
of them nor reference one of their functions.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from xarch.kernel.logic.placement import Place
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.values import Profile, SourceFile, TestTier

RULE = "types-only"
OWNERS = 3
"""How many parts that may make the call a fix names before it says "or another part"."""


def violations(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile,
               root: str) -> list[Violation]:
    """tests are the files below the tests root; app the app's files, below the root package root."""
    functions = {dotted(f.path, profile.language.marks)[0]: set(f.module_functions) for f in app}
    found: list[Violation] = []
    for file in tests:
        tier = tested(profile, file.path).tier
        if tier is None or not tier.types_only:
            continue
        who, key = f"a {tier.name} test", f"tiers.{tier.name}.types_only"
        found += [Violation(file.name, line, _message(who, profile, where, what, key), RULE, _fix(tier, where.part))
                  for line, where, what in _misuses(file, tier.types_only, profile, root, functions)]
    return found


def part_violations(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    """The files of the app, below the root package root, whose part lists parts in its own `types_only`."""
    if not profile.types_only:
        return []
    app = list(app)
    functions = {dotted(f.path, profile.language.marks)[0]: set(f.module_functions) for f in app}
    found: list[Violation] = []
    for file in app:
        src = place(profile, dotted(file.path, profile.language.marks)[0])
        if src is None or src.part not in profile.types_only:
            continue
        who, key = label(profile, src), f"parts.{src.part}.types_only"
        found += [Violation(file.name, line, _message(who, profile, where, what, key), RULE,
                            _part_fix(profile, src.part, where.part))
                  for line, where, what in _misuses(file, profile.types_only[src.part], profile, root, functions)]
    return found


def _misuses(file: SourceFile, parts: tuple[str, ...], profile: Profile, root: str,
             functions: dict[tuple[str, ...], set[str]]) -> list[tuple[int, Place, str]]:
    """Each call of what the file reaches of the parts, and each reference to one of their functions, as (line,
    where it lies, what is done: "call <path>" or "reference <path>, a function")."""
    found: list[tuple[int, Place, str]] = []
    for call in file.calls:
        if call.func[:1] != (root,):
            continue
        where = place(profile, call.func[1:])
        if where is not None and where.part in parts:
            found.append((call.line, where, f"call {'.'.join(call.func)}"))
    called = Counter((call.line, call.func) for call in file.calls)
    for use in file.uses:
        if use.name[:1] != (root,):
            continue
        reached = _function(use.name, use.bound, functions)
        if reached is None:
            continue
        where = place(profile, reached[:-1])
        if where is None or where.part not in parts:
            continue
        if called[(use.line, use.name)] > 0:
            called[(use.line, use.name)] -= 1
            continue
        found.append((use.line, where, f"reference {'.'.join((root, *reached))}, a function"))
    return found


def _message(who: str, profile: Profile, where: Place, what: str, key: str) -> str:
    return f"{who} uses {label(profile, where)} only as a type: it may not {what} ({key})"


def _part_fix(profile: Profile, src: str, dst: str | None) -> str:
    """Use the part as a type only and leave the call to a part that may make it: one that may import it and does
    not list it as a type only, named from the profile."""
    owners = [name for name, targets in profile.rules.items() if name not in (src, dst)
              and any(t.part == dst for t in targets) and dst not in profile.types_only.get(name, ())]
    shown = [f"{name}/" for name in owners[:OWNERS]]
    if not shown:
        return f"use {dst}/ here only as a type, and leave the call to code outside {src}/"
    listed = shown[0] if len(shown) == 1 else f"{', '.join(shown[:-1])} or {shown[-1]}"
    more = " or another part" if len(owners) > OWNERS else ""
    return f"use {dst}/ here only as a type, and leave the call to {listed}{more}, which may make it"


def _function(name: tuple[str, ...], bound: int, functions: dict[tuple[str, ...], set[str]]) -> tuple[str, ...] | None:
    """The module-level function below the root that the path reaches, as its dotted path below the root (the module,
    then the function): the first prefix, from the one the import bound, whose last name a module of the app defines
    as a function."""
    for end in range(max(bound, 2), len(name) + 1):
        module, function = name[1:end - 1], name[end - 1]
        if function in functions.get(module, ()):
            return (*module, function)
    return None


def _fix(tier: TestTier, part: str) -> str:
    """Use the part as a type only and drive the tier's subject, else leave what it does to a tier that may call it;
    with the tier's own words for what it may touch."""
    driven = ", ".join(f"{s.part}/" for s in tier.subject)
    fix = (f"use {part}/ here only as a type, and drive what you test through {driven}" if driven else
           f"use {part}/ here only as a type, and test what it does from a tier that may call it")
    return f"{fix} ({tier.name} tests may touch: {tier.may_touch})" if tier.may_touch else fix
