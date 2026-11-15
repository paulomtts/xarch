"""The no-callbacks check: code of a part that lists `no_callbacks` never calls one of its own parameters.

A callback is a call, by its bare name, of a parameter of the function, method or nested function it lies in whose
annotation says it is a callable (see the Callback value): `exists(path)` in `def resolve(path, exists:
Callable[[Path], bool])`. Code that calls what it is handed can do through it whatever the caller can, I/O included,
so the part's `forbidden` list says nothing of it. Not a callback: the first parameter of a method, the object or
class it is called on; a parameter with no such annotation, such as a predicate a private helper is handed by a
lambda of the same file (a miss when such a parameter does carry I/O); one passed on to another call (`sorted(rows,
key=key)`); one whose method is called (`p.read()`); and one the body rebinds.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.imports import dotted
from xarch.modules.rules.application.logic.places import label, place
from xarch.modules.rules.domain.values import Profile, SourceFile

RULE = "no-callbacks"


def violations(app: Iterable[SourceFile], profile: Profile) -> list[Violation]:
    if not profile.no_callbacks:
        return []
    found: list[Violation] = []
    for file in app:
        where = place(profile, dotted(file.path)[0])
        if where is None or where.part not in profile.no_callbacks:
            continue
        found += [Violation(file.name, call.line, f"{call.function} calls its parameter {call.parameter}: "
                                                  f"{label(profile, where)} takes no callback "
                                                  f"(parts.{where.part}.no_callbacks)", RULE,
                            f"have the caller call {call.parameter} first and pass {call.function} the answer as a "
                            "value")
                  for call in file.callbacks if call.annotated and not call.receiver]
    return found
