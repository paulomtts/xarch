"""The no-twins check: two public classes of the app, in parts of different names, that declare the same fields are one
type written twice; so are two whose fields differ only as a copy's do, when the profile gives the minimum of that
case.

A class's fields are the names its body declares with an annotation, in order (see Class.fields), and each field's
type is its annotation as written (Class.types). A class counts when it is defined at the top level of a file of a
part (a package file included), its name is public in the language (it does not start with the private prefix its
data file gives), and none of its bases is one the language marks as an interface (an interface's fields are a
requirement, not a type). Two classes are compared only when their parts have different names: two parts of one
instance of a repeating folder, of two instances, or outside any. Two classes of the same part, in one instance or in
two, are not this check's business, and the tests are never read.

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

A pair is no twin when the profile lists, in `no_twins_translated`, a part one of whose files builds one of the two
classes through an import (a call of it read through the import that binds it), imports the other, and holds
one function that names both (in a parameter's annotation, its return annotation or its body): the mark of a
translation at a seam. A class is reached through an import of the file that defines it or of a file that takes it
from there, as often as one file passes it on to another. Such a pair is reported by no case, its classes are read as
no copy of each other where a type's name is read, and it is handed out as excused, naming the function, once for
each pair, in the order the cases find them. A file that imports the other's file for another class, one that names
both in no one function, one that builds neither, one that builds a class it defines itself (a call through no
import), a translator in a part not listed and one in no part translate nothing.

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
from xarch.modules.rules.application.logic.imports import dotted, named_targets
from xarch.modules.rules.application.logic.places import file_place, label
from xarch.modules.rules.domain.outcomes import Twins
from xarch.modules.rules.domain.parsed import Class, Function, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Translation

RULE = "no-twins"
SHOWN = 4
"""How many field names a message shows."""
FIX = ("keep one of the two and import it from a part both may import, or give {cls} the fields its reader needs "
       "instead of a copy of {twin}'s")
RENAMED_FIX = ("keep one of the two, with one name for each field, and import it from a part both may import, or give "
               "{cls} the fields its reader needs instead of a renamed copy of {twin}'s")

Counted = tuple[SourceFile, Class, Place]
Files = dict[tuple[str, ...], tuple[SourceFile, tuple[str, ...]]]
"""Each file of the app that parses, by its dotted path below the root, with the folder its relative imports start
from."""
Built = dict[tuple[tuple[str, ...], tuple[str, ...]], tuple[SourceFile, Function]]
"""What the translators build from what: (the dotted path of the class one builds, that of the other class it
reaches), each with the file and the first function of it that names both."""


def checked(app: Iterable[SourceFile], profile: Profile, root: str) -> Twins:
    """The twins of the app, and the pairs the check excuses as translations."""
    if profile.no_twins is None:
        return Twins((), ())
    app = list(app)
    order = {name: index for index, name in enumerate(profile.parts)}
    built = _translated(app, profile, root)
    by_file = _counted(app, profile)
    counted = sorted(by_file, key=lambda item: order.get(item[2].part or "", len(order)))
    found, pairs, excused = _same(by_file, max(profile.no_twins, 1), order, profile, built, root)
    copied: dict[str, str] = {}
    for (_, cls, _), (_, twin, _) in pairs:
        copied.setdefault(cls.name, twin.name)
    if profile.no_twins_renamed is not None:
        least = max(profile.no_twins_renamed, 1)
        renamed: list[tuple[Counted, Counted]] = []
        grown = True
        while grown:
            names = _unique(counted, copied)
            renamed = [(later, earlier) for later, earlier in _pairs(counted, pairs, built, root, profile)
                       if _renamed(earlier[1], later[1], least, names, profile.language.names) is not None]
            before = len(copied)
            for later, earlier in renamed:
                copied.setdefault(later[1].name, earlier[1].name)
            grown = len(copied) > before
        names = _unique(counted, copied)
        for later, earlier in renamed:
            found.append(_renamed_violation(later, earlier, _renamed(earlier[1], later[1], least, names, profile.language.names), profile))
        pairs += renamed
        excused += [pair for pair in _pairs(counted, pairs, built, root, profile, translated=True)
                    if _renamed(pair[1][1], pair[0][1], least, names, profile.language.names) is not None]
    if profile.no_twins_subset is not None:
        least = max(profile.no_twins_subset, 1)
        for later, earlier in _pairs(counted, pairs, built, root, profile):
            if _partial(earlier[1].fields, later[1].fields, least) or _partial(later[1].fields, earlier[1].fields,
                                                                                 least):
                found.append(_partial_violation(later, earlier, profile))
        excused += [(later, earlier) for later, earlier in _pairs(counted, pairs, built, root, profile, translated=True)
                    if _partial(earlier[1].fields, later[1].fields, least)
                    or _partial(later[1].fields, earlier[1].fields, least)]
    return Twins(tuple(found), _translations(excused, built, root, profile))


def _counted(app: Iterable[SourceFile], profile: Profile) -> list[Counted]:
    found: list[Counted] = []
    for file in sorted(app, key=lambda f: f.name):
        where = file_place(profile, file.path)
        if where is None or where.part is None:
            continue
        found += [(file, cls, where) for cls in sorted(file.classes, key=lambda c: c.line)
                  if cls.fields and profile.language.is_public(cls.name)
                  and not cls.interface]
    return found


def _translated(app: list[SourceFile], profile: Profile, root: str) -> Built:
    """Each class a file of a part no_twins_translated lists builds through an import, with each other class that file
    reaches through its imports, when one function of the file names both."""
    if not profile.no_twins_translated:
        return {}
    marks = profile.language.marks
    files: Files = {steps: (file, steps if package else steps[:-1])
             for file in app if file.error is None for steps, package in (dotted(file.path, marks),)}
    found: Built = {}
    for steps, (file, folder) in files.items():
        where = file_place(profile, file.path)
        if where is None or where.part not in profile.no_twins_translated:
            continue
        built = [path for call in file.calls if call.func[:1] == (root,)
                 if (path := _defined(call.func, files, root)) is not None]
        reached = _reached(file, folder, files, root)
        for one in dict.fromkeys(built):
            for other in reached:
                function = next((f for f in file.functions if {one[-1], other[-1]} <= f.named), None)
                if other != one and function is not None:
                    found.setdefault((one, other), (file, function))
    return found


def _defined(path: tuple[str, ...], files: Files, root: str) -> tuple[str, ...] | None:
    """The dotted path of the class a dotted name reaches: a class of the file it names, or what that file takes
    under the name from another, as far as files pass it on; None when it reaches no class of the app."""
    seen: set[tuple[str, ...]] = set()
    while path not in seen:
        seen.add(path)
        held = files.get(path[1:-1])
        if held is None:
            return None
        file, folder = held
        name = path[-1]
        if any(cls.name == name for cls in file.classes):
            return path
        taken = next(((root, *target, name) for _, target, imported in named_targets(file.imports, folder, files.keys(),
                                                                                     root) if imported == name), None)
        if taken is None:
            return None
        path = taken
    return None


def _reached(file: SourceFile, folder: tuple[str, ...], files: Files, root: str) -> list[tuple[str, ...]]:
    """The dotted paths of the classes a file's imports reach: a name taken from a file, and every class a file taken
    as a whole defines or takes from another."""
    found: list[tuple[str, ...]] = []
    for _, target, name in named_targets(file.imports, folder, files.keys(), root):
        if name is not None:
            names: Iterable[str] = (name,)
        elif target in files:
            whole = files[target][0]
            names = (*(cls.name for cls in whole.classes), *(n for imp in whole.imports for n in imp.names or ()))
        else:
            names = ()
        found += [path for n in names if (path := _defined((root, *target, n), files, root)) is not None]
    return list(dict.fromkeys(found))


def _built(first: Counted, second: Counted, built: Built, root: str, profile: Profile) -> bool:
    """Whether a translator builds one of the two classes from the other."""
    return _translator(first, second, built, root, profile) is not None


def _translator(first: Counted, second: Counted, built: Built, root: str,
                profile: Profile) -> tuple[tuple[str, ...], tuple[str, ...], SourceFile, Function] | None:
    """The class a translator builds of the two, the other, and the translator's file and function; None when no
    translator builds one of them from the other."""
    marks = profile.language.marks
    one, other = ((root, *dotted(item[0].path, marks)[0], item[1].name) for item in (first, second))
    for pair in ((one, other), (other, one)):
        if pair in built:
            return (*pair, *built[pair])
    return None


def _translations(excused: list[tuple[Counted, Counted]], built: Built, root: str,
                  profile: Profile) -> tuple[Translation, ...]:
    """Each pair excused as a translation, once, as the translator's function says it."""
    found: list[Translation] = []
    for later, earlier in excused:
        said = _translator(later, earlier, built, root, profile)
        if said is None:
            continue
        one, other, file, function = said
        item = Translation(file.name, function.line, f"{function.owner}.{function.name}" if function.owner
                           else function.name, one[-1], other[-1])
        if item not in found:
            found.append(item)
    return tuple(found)


def _same(counted: list[Counted], least: int, order: dict[str, int], profile: Profile, built: Built,
          root: str) -> tuple[list[Violation], list[tuple[Counted, Counted]], list[tuple[Counted, Counted]]]:
    """The classes with the same fields, at least least of them, each group taken in the order of its first file: the
    violations, the pairs reported, and the pairs a translator excuses."""
    groups: dict[tuple[str, ...], list[Counted]] = {}
    for item in counted:
        if len(item[1].fields) >= least:
            groups.setdefault(item[1].fields, []).append(item)
    found: list[Violation] = []
    pairs: list[tuple[Counted, Counted]] = []
    excused: list[tuple[Counted, Counted]] = []
    for fields, members in groups.items():
        group = sorted(members, key=lambda item: order.get(item[2].part or "", len(order)))
        for index, item in enumerate(group):
            file, cls, where = item
            apart = [other for other in group[:index] if other[2].part != where.part]
            excused += [(item, other) for other in apart if _built(item, other, built, root, profile)]
            others = [other for other in apart if not _built(item, other, built, root, profile)]
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
    return found, pairs, excused


def _pairs(counted: list[Counted], reported: list[tuple[Counted, Counted]], built: Built, root: str,
           profile: Profile, translated: bool = False) -> list[tuple[Counted, Counted]]:
    """Every pair of counted classes in parts of different names, the later first, but those reported already: those
    no translator builds one of from the other, or (translated) those a translator does."""
    done = {(id(later[1]), id(earlier[1])) for later, earlier in reported}
    return [(later, earlier) for index, later in enumerate(counted) for earlier in counted[:index]
            if earlier[2].part != later[2].part and (id(later[1]), id(earlier[1])) not in done
            and _built(later, earlier, built, root, profile) == translated]


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


def _typed(annotation: str, names: dict[str, str], pattern: str) -> str:
    """The annotation with each name the language allows (by its pattern) that is a copy's read as its original's; as
    written when the language gives no pattern."""
    if not pattern:
        return annotation
    return re.sub(pattern, lambda m: names.get(m.group(0), m.group(0)), annotation)


def _renamed(first: Class, second: Class, least: int, names: dict[str, str],
             pattern: str) -> list[tuple[str, str]] | None:
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
    retyped = [index for index in differ if _typed(_type(short, index), names, pattern) != _typed(_type(long, index), names, pattern)]
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
