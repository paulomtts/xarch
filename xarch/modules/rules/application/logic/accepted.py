"""The imports a part accepts although its imports.may does not allow them (parts.<part>.imports.accepted), held
against what its files import. An entry names a file of the part, the file or folder below the app it imports
(optionally only one name taken from there) and why. The may-import rule excuses every import an entry accepts (the
filter target-accepted), and the enforcement section names each one instead. An entry that accepts nothing any more,
because its file is gone, because the file no longer imports what it names, or because imports.may now allows that
import, is itself a may-import violation: a ratchet of accepted imports can only shrink. An entry whose file is
written with the app folder's name first is told to write its path below the app.
"""
from __future__ import annotations

from xarch.kernel.logic.accepted_paths import stale_fix
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.places import accepting, allowed
from xarch.modules.rules.domain.outcomes import Ratchet
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import AcceptedEdge
from xarch.modules.rules.domain.rule import Facts

RULE = "may-import"


def ratchet(facts: Facts, profile: Profile) -> Ratchet:
    """Each entry of every part's imports.accepted that accepts nothing, as a violation, and each import accepted, in
    the order of the parts and of their entries."""
    stale: list[Violation] = []
    found: list[AcceptedEdge] = []
    for part, entries in profile.imports_accepted.items():
        key = f"parts.{part}.imports.accepted"
        for entry in entries:
            path, written = "/".join(entry.file), entry.written
            read = next((r for r in facts.files if not r.in_tests and r.file.path == entry.file), None)
            if read is None:
                stale.append(Violation(f"{facts.root}/{path}", 0,
                                       f"{path} is no file of the app, which {key} accepts an import of ({key})",
                                       RULE, _gone_fix(path, key, facts)))
                continue
            named = [fact for fact in read.facts.get("import-into-app", ())
                     if accepting(profile, part, entry.file, fact.target, fact.name) == entry]
            held = [fact for fact in named
                    if fact.at is not None and not allowed(profile, read.place, fact.at, fact.name)]
            if not named:
                stale.append(Violation(read.file.name, 0, f"{path} no longer imports {written}, which {key} accepts "
                                                          f"({key})", RULE, f"drop the entry of {path} from {key}"))
            elif not held:
                stale.append(Violation(read.file.name, 0, f"{path} imports {written}, which "
                                                          f"parts.{part}.imports.may allows: {key} accepts nothing "
                                                          f"({key})", RULE, f"drop the entry of {path} from {key}"))
            found += [AcceptedEdge(read.file.name, line, part, written, entry.why)
                      for line in dict.fromkeys(fact.line for fact in held)]
    return Ratchet(tuple(stale), tuple(found))


def _gone_fix(path: str, key: str, facts: Facts) -> str:
    """The fix of an entry of key whose file, path, is no file of the app: to drop or rename it, or, when it writes
    the app folder's name before a file of the app, to write the path below the app."""
    return stale_fix(path, facts.root, lambda steps: any(not r.in_tests and r.file.path == steps for r in facts.files),
                     f"drop the entry of {path} from {key}, or name the file as it is now")
