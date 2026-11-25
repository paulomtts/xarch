"""The findings the profile accepts one by one, held against what the checks find: a check of the profile's own
accepts findings by `checks.<id>.accepted`, each entry naming a file and, if need be, the values some variables of
the check print for the finding. A finding an entry accepts is not reported, and the enforcement section names it
instead; an entry that accepts nothing is itself a finding of the check, at its file, so a list of accepted findings,
a ratchet, can only shrink. A file is named as the profile writes it: by its path below the app, tests/<path> for a
file below the tests root.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import RULES, Violation
from xarch.modules.rules.application.logic.engine import said_of
from xarch.modules.rules.application.logic.sentences import value
from xarch.modules.rules.domain.outcomes import Sifted
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Excused, Weak
from xarch.modules.rules.domain.rule import Facts, Read, Rule
from xarch.profile_values.checks import AcceptedFinding


def _written_path(read: Read, profile: Profile) -> tuple[str, ...]:
    """The file as an entry of the profile names it: its path below the app, or tests/<path> below the tests root."""
    return (profile.default_tests, *read.file.path) if read.in_tests and not read.file.beside else read.file.path


def _shown(path: tuple[str, ...], facts: Facts, profile: Profile) -> str:
    """A file an entry names, as a finding shows it: the file read there, else its path from the folder holding the
    app."""
    read = next((r for r in facts.files if _written_path(r, profile) == path), None)
    if read is not None:
        return read.file.name
    if path[:1] == (profile.default_tests,) and facts.tests_root:
        return "/".join((facts.tests_root, *path[1:]))
    return "/".join((facts.root, *path))


def checks(rules: Iterable[Rule], facts: Facts, profile: Profile) -> Sifted:
    """What the checks of the profile's own find, each finding an entry of its check's `accepted` names taken out and
    named, and each entry that names none as a violation of its check."""
    rules = tuple(rules)
    entries = {rule.id: written.accepted for rule in rules if (written := profile.written.get(rule.id)) is not None}
    used: set[tuple[str, int]] = set()
    kept: list[Violation | Weak] = []
    excused: list[Excused] = []
    for item, found in said_of(rules, facts, profile):
        rule, path = found.rule.id, _written_path(found.read, profile)
        index = next((index for index, entry in enumerate(entries.get(rule, ())) if entry.file == path
                      and all(value(name, found, facts, profile) == said for name, said in entry.by)), None)
        if index is None:
            kept.append(item)
            continue
        used.add((rule, index))
        excused.append(Excused(rule, item.file, item.line, _key(rule), item.message, entries[rule][index].why))
    stale = [_stale(rule, entry, facts, profile) for rule, listed in entries.items()
             for index, entry in enumerate(listed) if (rule, index) not in used]
    return Sifted(tuple(kept), tuple(stale), tuple(excused))


def _key(rule: str) -> str:
    return f"checks.{rule}.accepted"


def _stale(rule: str, entry: AcceptedFinding, facts: Facts, profile: Profile) -> Violation:
    key, path = _key(rule), "/".join(entry.file)
    what = (f"a finding of {path} with {' and '.join(f'{name} {said}' for name, said in entry.by)}" if entry.by
            else f"the findings of {path}")
    return Violation(_shown(entry.file, facts, profile), 0, f"{key} accepts {what}, and the check finds none ({key})",
                     rule, f"drop the entry of {path} from {key}", rule not in RULES)
