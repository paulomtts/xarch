"""The no-twins check: two public classes of the app, in parts of different names, that declare the same fields are one
type written twice; so are two whose fields differ only as a copy's do, when the profile gives the minimum of that
case.

A class's fields are the names its body declares with an annotation, in order (see Class.fields), and each field's
type is its annotation as written (Class.types). A class counts when it is defined at the top level of a file of a
part (a package file included), its name does not start with `_`, and none of its bases is one the language marks as
an interface (an interface's fields are a requirement, not a type). Two classes are compared only when their parts
have different names: two parts of one instance of a repeating folder, of two instances, or outside any. Two classes
of the same part, in one instance or in two, are not this check's business, and the tests are never read.

Three cases, each with its own fewest fields:

- the same fields (`no_twins`, min_fields): the field names are equal, in order. Their types and defaults are not
  compared: a copy names the copies of the types it holds (`tuple[LoosenedView, ...]` where the original holds
  `tuple[Loosened, ...]`), and a default changes no shape.
- a renamed copy (`no_twins_renamed`, min_renamed): the shorter class A, of m fields, at least the minimum, against
  the first m fields of B, of n (m <= n <= 2m), position by position: the names differ at one position or more, the
  names that agree are more than half of n, and either every position whose names differ holds the same type in both,
  or only one position differs and at least the minimum of others agree. Types are compared as written, but for the
  name of a class that is a twin, by the same fields or as a renamed copy, which is read as the name of the class it
  copies, as often as that makes new twins; a name two counted classes share is read as written.
- a partial copy (`no_twins_subset`, min_subset): the field names of A, of m fields, at least the minimum, are those
  of B, of n > m, in B's order, with B's other fields between or around them (any subsequence, not only the first
  m), and A keeps at least half of B's fields (2m >= n): a value with fewer is a smaller value of its own. Types are
  not compared, as for the same fields.

The classes with the same fields form a group, in the order of the profile's parts (the order their litmus tests
run, so the inner part comes first), then of file name and line. A class is reported at its own place when an earlier
class of the group lies in a part of another name, naming one such: the first of those in its own instance of a
repeating folder (for a class outside every repeating folder, the first outside them too), else the first of them
all. So the first of a group is never reported, every class with an earlier twin in another part is, each report
names a class before it, and a class whose earlier twins all lie in its own part is not reported, though its later
twins in other parts are. A pair of a renamed or a partial copy is reported once, at the later of the two in the same
order, naming the earlier; a pair already reported by an earlier case is not reported again.
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from xarch.kernel.placement import Place
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.places import file_place, label
from xarch.modules.rules.domain.values import Class, Profile, SourceFile

RULE = "no-twins"
SHOWN = 4
"""How many field names a message shows."""
FIX = ("keep one of the two and import it from a part both may import, or give {cls} the fields its reader needs "
       "instead of a copy of {twin}'s")
RENAMED_FIX = ("keep one of the two, with one name for each field, and import it from a part both may import, or give "
               "{cls} the fields its reader needs instead of a renamed copy of {twin}'s")
_NAME = re.compile(r"[^\W\d]\w*")

Counted = tuple[SourceFile, Class, Place]


def violations(app: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    if profile.no_twins is None:
        return []
    order = {name: index for index, name in enumerate(profile.parts)}
    by_file = _counted(app, profile)
    counted = sorted(by_file, key=lambda item: order.get(item[2].part or "", len(order)))
    found, pairs = _same(by_file, max(profile.no_twins, 1), order, profile)
    copied: dict[str, str] = {}
    for (_, cls, _), (_, twin, _) in pairs:
        copied.setdefault(cls.name, twin.name)
    if profile.no_twins_renamed is not None:
        least = max(profile.no_twins_renamed, 1)
        renamed: list[tuple[Counted, Counted]] = []
        grown = True
        while grown:
            names = _unique(counted, copied)
            renamed = [(later, earlier) for later, earlier in _pairs(counted, pairs)
                       if _renamed(earlier[1], later[1], least, names) is not None]
            before = len(copied)
            for later, earlier in renamed:
                copied.setdefault(later[1].name, earlier[1].name)
            grown = len(copied) > before
        names = _unique(counted, copied)
        for later, earlier in renamed:
            found.append(_renamed_violation(later, earlier, _renamed(earlier[1], later[1], least, names), profile))
        pairs += renamed
    if profile.no_twins_subset is not None:
        least = max(profile.no_twins_subset, 1)
        for later, earlier in _pairs(counted, pairs):
            if _partial(earlier[1].fields, later[1].fields, least) or _partial(later[1].fields, earlier[1].fields,
                                                                                 least):
                found.append(_partial_violation(later, earlier, profile))
    return found


def _counted(app: Iterable[SourceFile], profile: Profile) -> list[Counted]:
    found: list[Counted] = []
    for file in sorted(app, key=lambda f: f.name):
        where = file_place(profile, file.path)
        if where is None or where.part is None:
            continue
        found += [(file, cls, where) for cls in sorted(file.classes, key=lambda c: c.line)
                  if cls.fields and profile.language.is_public(cls.name)
                  and not any(base in profile.language.interface for base in cls.bases)]
    return found


def _same(counted: list[Counted], least: int, order: dict[str, int],
          profile: Profile) -> tuple[list[Violation], list[tuple[Counted, Counted]]]:
    """The classes with the same fields, at least least of them, each group taken in the order of its first file."""
    groups: dict[tuple[str, ...], list[Counted]] = {}
    for item in counted:
        if len(item[1].fields) >= least:
            groups.setdefault(item[1].fields, []).append(item)
    found: list[Violation] = []
    pairs: list[tuple[Counted, Counted]] = []
    for fields, members in groups.items():
        group = sorted(members, key=lambda item: order.get(item[2].part or "", len(order)))
        for index, item in enumerate(group):
            file, cls, where = item
            others = [other for other in group[:index] if other[2].part != where.part]
            twin = next((other for other in others if other[2].instance == where.instance),
                        others[0] if others else None)
            pairs += [(item, other) for other in others]
            if twin is None:
                continue
            twin_file, twin_cls, twin_where = twin
            found.append(Violation(
                file.name, cls.line,
                f"{cls.name} declares the fields of {twin_cls.name} at {twin_file.name}:{twin_cls.line} in the same "
                f"order ({_fields(fields)}): {label(profile, where)} and {label(profile, twin_where)} hold one type "
                f"written twice ({RULE})", RULE, FIX.format(cls=cls.name, twin=twin_cls.name)))
    return found, pairs


def _pairs(counted: list[Counted], reported: list[tuple[Counted, Counted]]) -> list[tuple[Counted, Counted]]:
    """Every pair of counted classes in parts of different names, the later first, but those reported already."""
    done = {(id(later[1]), id(earlier[1])) for later, earlier in reported}
    return [(later, earlier) for index, later in enumerate(counted) for earlier in counted[:index]
            if earlier[2].part != later[2].part and (id(later[1]), id(earlier[1])) not in done]


def _unique(counted: list[Counted], copied: dict[str, str]) -> dict[str, str]:
    """How a type's name is read: a twin's as the name of the class it copies, however far; a name two counted
    classes share is left out, and read as written."""
    seen: dict[str, int] = {}
    for _, cls, _ in counted:
        seen[cls.name] = seen.get(cls.name, 0) + 1
    found: dict[str, str] = {}
    for name in copied:
        if seen.get(name, 0) > 1:
            continue
        original, steps = copied[name], 0
        while original in copied and steps < len(copied):
            original, steps = copied[original], steps + 1
        found[name] = original
    return found


def _typed(annotation: str, names: dict[str, str]) -> str:
    return _NAME.sub(lambda m: names.get(m.group(0), m.group(0)), annotation)


def _renamed(first: Class, second: Class, least: int, names: dict[str, str]) -> list[tuple[str, str]] | None:
    """The renamed fields, as (the name of the later class, the name of the earlier), when the later is a renamed copy
    of the earlier (or the earlier of the later); None when it is not."""
    short, long = (first, second) if len(first.fields) <= len(second.fields) else (second, first)
    m, n = len(short.fields), len(long.fields)
    if m < least or n > 2 * m:
        return None
    differ = [index for index in range(m) if short.fields[index] != long.fields[index]]
    agree = m - len(differ)
    if not differ or 2 * agree <= n:
        return None
    retyped = [index for index in differ if _typed(_type(short, index), names) != _typed(_type(long, index), names)]
    if retyped and not (len(differ) == 1 and agree >= least):
        return None
    return [(second.fields[index], first.fields[index]) for index in differ]


def _type(cls: Class, index: int) -> str:
    return cls.types[index] if index < len(cls.types) else ""


def _partial(part: tuple[str, ...], whole: tuple[str, ...], least: int) -> bool:
    """Whether part holds at least least of whole's fields, at least half of them, in whole's order, and fewer."""
    if len(part) < least or len(part) >= len(whole) or 2 * len(part) < len(whole):
        return False
    remaining = iter(whole)
    return all(name in remaining for name in part)


def _renamed_violation(later: Counted, earlier: Counted, renamed: list[tuple[str, str]] | None,
                       profile: Profile) -> Violation:
    file, cls, where = later
    twin_file, twin, twin_where = earlier
    names = " and ".join(f"{new} in place of {old}" for new, old in renamed or ())
    return Violation(
        file.name, cls.line,
        f"{cls.name} declares {_share(cls, twin)} at {twin_file.name}:{twin.line} in the same order, but for {names}"
        f"{_more(cls.fields[len(twin.fields):])} ({_fields(cls.fields)}): {label(profile, where)} and {label(profile, twin_where)} hold "
        f"one type written twice ({RULE})", RULE, RENAMED_FIX.format(cls=cls.name, twin=twin.name))


def _partial_violation(later: Counted, earlier: Counted, profile: Profile) -> Violation:
    file, cls, where = later
    twin_file, twin, twin_where = earlier
    fields = _fields(cls.fields)
    said = (f"{_share(cls, twin)} at {twin_file.name}:{twin.line}, in the same order ({fields})"
            if len(cls.fields) < len(twin.fields) else
            f"the fields of {twin.name} at {twin_file.name}:{twin.line} in the same order"
            f"{_more(tuple(name for name in cls.fields if name not in twin.fields))} ({fields})")
    return Violation(
        file.name, cls.line,
        f"{cls.name} declares {said}: {label(profile, where)} and {label(profile, twin_where)} hold one type written "
        f"twice ({RULE})", RULE, FIX.format(cls=cls.name, twin=twin.name))


def _share(cls: Class, twin: Class) -> str:
    """Which of the twin's fields the class declares: all of them, or how many of how many."""
    if len(cls.fields) < len(twin.fields):
        return f"{len(cls.fields)} of the {len(twin.fields)} fields of {twin.name}"
    return f"the fields of {twin.name}"


def _more(extra: tuple[str, ...]) -> str:
    """The fields a class declares beyond its twin's, when it declares any."""
    return f", and {len(extra)} more ({', '.join(extra)})" if extra else ""


def _fields(fields: tuple[str, ...]) -> str:
    if len(fields) <= SHOWN:
        return ", ".join(fields)
    return f"{', '.join(fields[:SHOWN])} and {len(fields) - SHOWN} more"
