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
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from xarch.kernel.logic.placement import Place
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.imports import dotted
from xarch.modules.rules.domain.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile, TestTier


def violations(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile,
               root: str) -> list[Violation]:
    """tests are the files below the tests root; app the app's files, below the root package root."""
    functions = {dotted(f.path)[0]: set(f.module_functions) for f in app}
    found: list[Violation] = []
    for file in tests:
        tier = tested(profile, file.path).tier
        if tier is None or not tier.types_only:
            continue
        found += _calls(file, tier, profile, root)
        found += _references(file, tier, profile, root, functions)
    return found


def _calls(file: SourceFile, tier: TestTier, profile: Profile, root: str) -> list[Violation]:
    found: list[Violation] = []
    for call in file.calls:
        if call.func[:1] != (root,):
            continue
        where = place(profile, call.func[1:])
        if where is None or where.part not in tier.types_only:
            continue
        found.append(Violation(file.name, call.line, f"a {tier.name} test uses {label(profile, where)} only as a "
                                                     f"type: it may not call {'.'.join(call.func)} "
                                                     f"(tiers.{tier.name}.types_only)", "types-only",
                               _fix(tier, where.part)))
    return found


def _references(file: SourceFile, tier: TestTier, profile: Profile, root: str,
                functions: dict[tuple[str, ...], set[str]]) -> list[Violation]:
    """The reads of a function of a types-only part, but for those that are the callee of a call on their line."""
    called = Counter((call.line, call.func) for call in file.calls)
    found: list[Violation] = []
    for use in file.uses:
        if use.name[:1] != (root,):
            continue
        reached = _function(use.name, use.bound, functions)
        if reached is None:
            continue
        where = place(profile, reached[:-1])
        if where is None or where.part not in tier.types_only:
            continue
        if called[(use.line, use.name)] > 0:
            called[(use.line, use.name)] -= 1
            continue
        found.append(Violation(file.name, use.line, _reference(tier, profile, where, reached, root), "types-only",
                               _fix(tier, where.part)))
    return found


def _function(name: tuple[str, ...], bound: int, functions: dict[tuple[str, ...], set[str]]) -> tuple[str, ...] | None:
    """The module-level function below the root that the path reaches, as its dotted path below the root (the module,
    then the function): the first prefix, from the one the import bound, whose last name a module of the app defines
    as a function."""
    for end in range(max(bound, 2), len(name) + 1):
        module, function = name[1:end - 1], name[end - 1]
        if function in functions.get(module, ()):
            return (*module, function)
    return None


def _reference(tier: TestTier, profile: Profile, where: Place, reached: tuple[str, ...], root: str) -> str:
    return (f"a {tier.name} test uses {label(profile, where)} only as a type: it may not reference "
            f"{'.'.join((root, *reached))}, a function (tiers.{tier.name}.types_only)")


def _fix(tier: TestTier, part: str) -> str:
    """Use the part as a type only and drive the tier's subject, else leave what it does to a tier that may call it;
    with the tier's own words for what it may touch."""
    driven = ", ".join(f"{s.part}/" for s in tier.subject)
    fix = (f"use {part}/ here only as a type, and drive what you test through {driven}" if driven else
           f"use {part}/ here only as a type, and test what it does from a tier that may call it")
    return f"{fix} ({tier.name} tests may touch: {tier.may_touch})" if tier.may_touch else fix
