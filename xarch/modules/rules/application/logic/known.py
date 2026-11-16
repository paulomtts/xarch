"""The public names a profile accepts as only the tests' (guards.dead-code.known), held against what the tests-only
check lists (guards.dead-code.tests_only). An entry is `<file below the app>:<name>`. A name the check lists that an
entry names is accepted: the enforcement section names it, and it is no longer listed. An entry is itself listed,
weak, when its file defines no public class (an exception aside) or top-level function of its name, and when the check
does not list that name because another file of the app names it, so that the list cannot outlive what it accepts.
Like the check, which compares names by their spelling, an entry whose name another file spells is no longer the
tests' alone.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.published import KnownName, Weak
from xarch.modules.rules.domain.rule import Facts, Read
from xarch.modules.rules.domain.values import Accepting, Profile

RULE = "dead-code"
KEY = "guards.dead-code.known"


def accepting(listed: Iterable[Violation | Weak], facts: Facts, profile: Profile) -> Accepting:
    """What the tests-only check listed, the names the profile accepts taken out and its entries that no longer hold
    added after; with the check off, all of it as listed and nothing accepted."""
    listed = tuple(listed)
    if not profile.dead_code or not profile.tests_only:
        return Accepting(listed, ())
    places = {(item.file, item.line) for item in listed if isinstance(item, Weak)}
    known: list[KnownName] = []
    stale: list[Weak] = []
    for entry in profile.tests_only_known:
        path, _, name = entry.rpartition(":")
        read = next((r for r in facts.files if not r.in_tests and "/".join(r.file.path) == path), None)
        line = _declared(read, name, profile) if read is not None else None
        if read is None or line is None:
            stale.append(Weak(RULE, read.file.name if read is not None else f"{facts.root}/{path}", 0,
                              f"{path} defines no public class or top-level function {name}, which {KEY} lists "
                              f"({KEY})", f"drop {entry} from {KEY}, or name the file and the name as they are now"))
        elif (read.file.name, line) in places:
            known.append(KnownName(read.file.name, line, name))
        else:
            stale.append(Weak(RULE, read.file.name, line, f"{name} is listed by {KEY} as only the tests', but another "
                                                          f"file of the app names it ({KEY})",
                              f"drop {entry} from {KEY}: the app uses it"))
    accepted = {(item.file, item.line) for item in known}
    return Accepting((*(item for item in listed if not (isinstance(item, Weak) and (item.file, item.line) in accepted)),
                      *stale), tuple(known))


def _declared(read: Read, name: str, profile: Profile) -> int | None:
    """The line of the public class, an exception aside, or the top-level function the file defines under name; None
    when it defines none."""
    if not profile.language.is_public(name):
        return None
    function = next((f.line for f in read.facts.get("function", ()) if f.name == name and "top-level" in f.traits), None)
    return next((f.line for f in read.facts.get("class", ()) if f.name == name and "exception" not in f.traits), function)
