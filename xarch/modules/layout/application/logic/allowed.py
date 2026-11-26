"""The findings of the layout the profile accepts one by one (structure.accepted), held against what the structure
and test-tree rules find: a finding an entry names, by the path of the folder or file it is about, is not reported
but waived, with the entry's reason; an entry that names none is itself a finding, of structure for a path below the
app and of test-tree for one below the tests root, so a list of accepted findings, a ratchet, can only shrink."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.layout.domain.published import Waived
from xarch.modules.layout.domain.structure import Allowed

KEY = "structure.accepted"
"""The key the entries are written under."""

Located = tuple[tuple[str, ...], bool]
"""Where a finding is: its steps below the app root, or below the tests root when the second is true."""


def sifted(found: Iterable[tuple[Located, Violation]], accepted: Iterable[Allowed], package: str,
           tests: str | None) -> tuple[tuple[Violation, ...], tuple[Waived, ...]]:
    """The findings no entry names, then each entry that names none as a finding, in the order written; and each
    finding an entry names, waived. package and tests name the app root and the tests root (None: no tests) in the
    findings of the entries."""
    entries = list(accepted)
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
    stale = [_stale(entry, package, tests) for index, entry in enumerate(entries) if index not in used]
    return (*kept, *stale), tuple(waived)


def _stale(entry: Allowed, package: str, tests: str | None) -> Violation:
    rule = "test-tree" if entry.tests else "structure"
    root = (tests or entry.written.split("/")[0]) if entry.tests else package
    return Violation("/".join((root, *entry.path)), 0,
                     f"{KEY} accepts {entry.written} as a finding of {rule}, and {rule} finds none there ({KEY})",
                     rule, f"drop the entry of {entry.written} from {KEY}")
