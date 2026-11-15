"""The names check: every public class of a part that lists `names` matches one of its patterns.

A public class is one defined at the top level of a file of the part whose name does not start with `_`. A pattern
matches a name as written, `*` standing for any text (`*Service` matches DocumentService and Service). A nested class
is not read.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.placement import name_matches
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile

RULE = "names"


def violations(app: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    if not profile.names:
        return []
    found: list[Violation] = []
    for file in app:
        where = place(profile, dotted(file.path, profile.language.marks)[0])
        if where is None or where.part not in profile.names:
            continue
        patterns = profile.names[where.part]
        shown = " or ".join(patterns)
        found += [Violation(file.name, c.line, f"{c.name} does not match {shown}, as every class of "
                                               f"{label(profile, where)} must (parts.{where.part}.names)", RULE,
                            f"rename {c.name} to match {shown}, or move it to the part whose kind of class it is")
                  for c in file.classes
                  if profile.language.is_public(c.name) and not any(name_matches(p, c.name) for p in patterns)]
    return found
