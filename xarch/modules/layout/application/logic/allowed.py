"""The findings of the layout the profile accepts one by one (structure.accepted), held against what the structure
and test-tree rules find: a finding an entry names, by the path of the folder or file it is about, is not reported
but waived, with the entry's reason; an entry that names none is itself a finding, of structure for a path below the
app and of test-tree for one below the tests root, so a list of accepted findings, a ratchet, can only shrink. An
entry below the app written with the app folder's name first is told to write its path below the app, when that path
is there or is a finding of structure."""
from __future__ import annotations

from collections.abc import Callable, Iterable

from xarch.kernel.logic.accepted_paths import stale_fix
from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.published import Waived
from xarch.modules.layout.domain.structure import Allowed

KEY = "structure.accepted"
"""The key the entries are written under."""

Located = tuple[tuple[str, ...], bool]
"""Where a finding is: its steps below the app root, or below the tests root when the second is true."""


There = Callable[[tuple[str, ...]], bool]
"""Whether a folder or file is below the app, by its steps."""


def sifted(found: Iterable[tuple[Located, Violation]], accepted: Iterable[Allowed], package: str,
           tests: str | None, there: There) -> tuple[tuple[Violation, ...], tuple[Waived, ...]]:
    """The findings no entry names, then each entry that names none as a finding, in the order written; and each
    finding an entry names, waived. package and tests name the app root and the tests root (None: no tests) in the
    findings of the entries; there says whether a folder or file is below the app."""
    entries, found = list(accepted), list(found)
    used: set[int] = set()
    kept: list[Violation] = []
    waived: list[Waived] = []
    for (path, below_tests), violation in found:
        index = next((index for index, entry in enumerate(entries)
                      if entry.path == path and entry.tests == below_tests), None)
        if index is None:
            kept.append(violation)
            continue
        used.add(index)
        waived.append(Waived(violation.rule, violation.file, violation.message, entries[index].why))
    at = {path for (path, below_tests), _ in found if not below_tests}
    stale = [_stale(entry, package, tests, lambda steps: steps in at or there(steps))
             for index, entry in enumerate(entries) if index not in used]
    return (*kept, *stale), tuple(waived)


def _stale(entry: Allowed, package: str, tests: str | None, there: There) -> Violation:
    rule = "test-tree" if entry.tests else "structure"
    fix = f"drop the entry of {entry.written} from {KEY}"
    root = (tests or entry.written.split("/")[0]) if entry.tests else package
    return Violation("/".join((root, *entry.path)), 0,
                     f"{KEY} accepts {entry.written} as a finding of {rule}, and {rule} finds none there ({KEY})",
                     rule, fix if entry.tests else stale_fix(entry.written, package, there, fix))
