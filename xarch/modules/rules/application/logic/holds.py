"""The holds check: a file of a part that lists `holds` defines at the top level what the part holds, listed without
failing.

holds: classes. A function defined at the top level of a file of the part (a function with no owner class) whose
name does not start with `_` is listed: a private helper and a dunder name are not.

holds: functions. A class defined at the top level of a file of the part is listed, whatever its name (a class whose
name starts with `_` holds state and methods all the same), but for two kinds of class a file of functions needs: an
exception, which derives from a builtin exception directly or through classes of the app (a base read through the
absolute import that binds it, as a class of a file of the app that is an exception itself, however far that goes);
and a record, a class with no method but dunder methods, that a top-level function of the same file (private or not)
names in its return annotation, so that it is what that function answers.

A package file (the file that stands for its folder) is not read: it only gathers what its package holds. It is listed in the enforcement
section like a weak check and fails `check --strict` only: where a part's code belongs by its kind is the profile's
description, which code may follow for a reason the check cannot see.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.domain.values import Class, Profile, SourceFile, Weak

RULE = "holds"
CLASSES, FUNCTIONS = "classes", "functions"
SHOWN = 3
"""How many parts that hold the other kind a fix names."""


def weak(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Weak]:
    """The files of the app, below the root package root."""
    if not profile.holds:
        return []
    app = list(app)
    found_exceptions = exceptions(app, root, profile)
    found: list[Weak] = []
    for file in app:
        steps, is_package = dotted(file.path, profile.language.marks)
        where = place(profile, steps)
        if is_package or where is None or where.part not in profile.holds:
            continue
        key = f"(parts.{where.part}.holds)"
        if profile.holds[where.part] == CLASSES:
            found += [Weak(RULE, file.name, f.line, f"{f.name} is a function at the top level, but "
                                                   f"{label(profile, where)} holds classes {key}",
                           f"make {f.name} a method of the class whose rule it is, or move it to "
                           f"{_others(profile, FUNCTIONS)}")
                      for f in file.functions if not f.owner and not f.name.startswith("_")]
        else:
            found += [Weak(RULE, file.name, c.line, f"{c.name} is a class, but {label(profile, where)} holds "
                                                   f"functions {key}",
                           f"move {c.name} to {_others(profile, CLASSES)}, or make what it does functions")
                      for c in file.classes if (steps, c.name) not in found_exceptions
                      and not _record(c, file)]
    return found


def _others(profile: Profile, kind: str) -> str:
    parts = [f"{name}/" for name, holds in profile.holds.items() if holds == kind][:SHOWN]
    return f"a part that holds {kind}: {', '.join(parts)}" if parts else f"a part that holds {kind}"


def _record(cls: Class, file: SourceFile) -> bool:
    """A class with no method but dunder methods that a top-level function of its file returns."""
    if any(not (m.name.startswith("__") and m.name.endswith("__")) for m in cls.methods):
        return False
    return any(cls.name in f.returns_named for f in file.functions if not f.owner)


def exceptions(app: list[SourceFile], root: str, profile: Profile) -> set[tuple[tuple[str, ...], str]]:
    """Every class of the app that is an exception, as (dotted path of its file, name)."""
    classes = {(dotted(f.path, profile.language.marks)[0], c.name): c for f in app for c in f.classes}
    found = {key for key, cls in classes.items() if cls.exception}
    grown = True
    while grown:
        grown = False
        for key, cls in classes.items():
            if key not in found and any(base is not None and base[:1] == (root,)
                                        and (base[1:-1], base[-1]) in found for base in cls.bases):
                found.add(key)
                grown = True
    return found
