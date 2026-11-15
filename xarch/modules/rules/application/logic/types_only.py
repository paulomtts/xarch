"""The types-only check: a test of a tier that names parts in `types_only` may import them and use them as types,
but never call what it imports from them.

A call is read through the import that binds its callee's first name (see the Call value): `X(...)` after `from
<part> import X [as Y]`, `m.X(...)` after `from <package> import <module of part> [as m]` or `import <module> as m`,
and the full dotted path after `import <module>`. A callee bound any other way (a parameter, an assignment, a
relative import) is not read, so a fake handed in as a parameter typed with the real class is fine.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile


def violations(tests: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation]:
    found: list[Violation] = []
    for file in tests:
        tier = tested(profile, file.path).tier
        if tier is None or not tier.types_only:
            continue
        for call in file.calls:
            if call.func[:1] != (root,):
                continue
            where = place(profile, call.func[1:])
            if where is None or where.part not in tier.types_only:
                continue
            found.append(Violation(file.name, call.line, f"a {tier.name} test uses {label(profile, where)} only as a "
                                                         f"type: it may not call {'.'.join(call.func)} "
                                                         f"(tiers.{tier.name}.types_only)"))
    return found
