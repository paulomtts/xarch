"""The no-twins check: two public classes of the app, in parts of different names, that declare the same fields in
the same order are one type written twice.

A class's fields are the names its body declares with an annotation, in order (see Class.fields). Their types and
defaults are not compared: a copy names the copies of the types it holds (`tuple[LoosenedView, ...]` where the
original holds `tuple[Loosened, ...]`), and a default changes no shape. A class counts when it is defined at the top
level of a file of a part (a package file included), its name does not start with `_`, none of its bases is one the
language marks as an interface (an interface's fields are a requirement, not a type), and it declares at least
`no_twins` fields. Two such classes are twins when their field names are equal, in order, and their parts have
different names: two parts of one instance of a repeating folder, of two instances, or outside any. Two classes of
the same part, in one instance or in two, are not this check's business, and the tests are never read.

The classes with the same fields form a group, in the order of the profile's parts (the order their litmus tests
run, so the inner part comes first), then of file name and line. A class is reported at its own place when an earlier
class of the group lies in a part of another name, naming one such: the first of those in its own instance of a
repeating folder (for a class outside every repeating folder, the first outside them too), else the first of them
all. So the first of a group is never reported, every class with an earlier twin in another part is, each report
names a class before it, and a class whose earlier twins all lie in its own part is not reported, though its later
twins in other parts are.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.placement import Place
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.domain.values import Class, Profile, SourceFile

RULE = "no-twins"
SHOWN = 4
"""How many field names a message shows."""


def violations(app: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    if profile.no_twins is None:
        return []
    least = max(profile.no_twins, 1)
    order = {name: index for index, name in enumerate(profile.parts)}
    groups: dict[tuple[str, ...], list[tuple[SourceFile, Class, Place]]] = {}
    for file in sorted(app, key=lambda f: f.name):
        where = place(profile, dotted(file.path, profile.language.marks)[0])
        if where is None or where.part is None:
            continue
        for cls in sorted(file.classes, key=lambda c: c.line):
            if len(cls.fields) >= least and profile.language.is_public(cls.name) \
                    and not any(base in profile.language.interface for base in cls.bases):
                groups.setdefault(cls.fields, []).append((file, cls, where))
    found: list[Violation] = []
    for fields, members in groups.items():
        group = sorted(members, key=lambda item: order.get(item[2].part or "", len(order)))
        for index, (file, cls, where) in enumerate(group):
            others = [item for item in group[:index] if item[2].part != where.part]
            twin = next((item for item in others if item[2].instance == where.instance), others[0] if others else None)
            if twin is None:
                continue
            twin_file, twin_cls, twin_where = twin
            found.append(Violation(
                file.name, cls.line,
                f"{cls.name} declares the fields of {twin_cls.name} at {twin_file.name}:{twin_cls.line} in the same "
                f"order ({_fields(fields)}): {label(profile, where)} and {label(profile, twin_where)} hold one type "
                f"written twice ({RULE})", RULE,
                f"keep one of the two and import it from a part both may import, or give {cls.name} the fields its "
                f"reader needs instead of a copy of {twin_cls.name}'s"))
    return found


def _fields(fields: tuple[str, ...]) -> str:
    if len(fields) <= SHOWN:
        return ", ".join(fields)
    return f"{', '.join(fields[:SHOWN])} and {len(fields) - SHOWN} more"
