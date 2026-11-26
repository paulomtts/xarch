"""The findings the profile accepts one by one, held against what the checks find: a check of the profile's own
accepts findings by `checks.<id>.accepted`, each entry naming a file and, if need be, the values some variables of
the check print for the finding; a finding said once for several facts is accepted when the entry names any one
of them. A finding an entry accepts is not reported, and the enforcement section names it
instead; an entry that accepts nothing is itself a finding of the check, at its file, so a list of accepted findings,
a ratchet, can only shrink. A tier accepts tiers findings the same way by `tiers.<tier>.accepted`, each entry naming
a test file and, if need be, what it imports. A file is named as the profile writes it: by its path below the app, tests/<path> for a
file below the tests root. An entry that accepts nothing written with the app folder's name first is told to write
its path below the app.
"""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.accepted_paths import stale_fix
from xarch.kernel.logic.placement import module_steps
from xarch.kernel.violations import RULES, Violation
from xarch.modules.rules.application.logic.engine import said_of, standing
from xarch.modules.rules.application.logic.sentences import value
from xarch.modules.rules.domain.outcomes import Sifted
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Excused, Weak
from xarch.modules.rules.domain.rule import Facts, Found, Read, Rule
from xarch.profile_values.checks import AcceptedFinding
from xarch.profile_values.placement import AcceptedImport


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


def _fix(path: str, key: str, facts: Facts, profile: Profile) -> str:
    """The fix of an entry of key that accepts nothing and writes path: to drop it, or, when it writes the app
    folder's name before a file the run read, to write the path as the profile names that file."""
    return stale_fix(path, facts.root, lambda steps: any(_written_path(r, profile) == steps for r in facts.files),
                     f"drop the entry of {path} from {key}")


def checks(rules: Iterable[Rule], facts: Facts, profile: Profile) -> Sifted:
    """What the checks of the profile's own find, each finding an entry of its check's `accepted` names taken out and
    named, and each entry that names none as a violation of its check."""
    rules = tuple(rules)
    entries = {rule.id: written.accepted for rule in rules if (written := profile.written.get(rule.id)) is not None}
    used: set[tuple[str, int]] = set()
    kept: list[Violation | Weak] = []
    excused: list[Excused] = []
    for item, founds in standing(rules, facts, profile):
        rule, path = founds[0].rule.id, _written_path(founds[0].read, profile)
        index = next((index for index, entry in enumerate(entries.get(rule, ())) if entry.file == path
                      and any(all(value(name, found, facts, profile) == said for name, said in entry.by)
                              for found in founds)), None)
        if index is None:
            kept.append(item)
            continue
        used.add((rule, index))
        excused.append(Excused(rule, item.file, item.line, _key(rule), item.message, entries[rule][index].why))
    stale = [_stale(rule, entry, facts, profile) for rule, listed in entries.items()
             for index, entry in enumerate(listed) if (rule, index) not in used]
    return Sifted(tuple(kept), tuple(stale), tuple(excused))


def tiers(rules: Iterable[Rule], facts: Facts, profile: Profile) -> Sifted:
    """What the tiers rules find, each finding an entry of a tier's `accepted` names taken out and named, and each
    entry that names none as a tiers violation: an entry names a finding of its file, a test of its tier or of no
    tier, and, when it writes an import, one of what the file imports from there."""
    entries = [(tier.name, entry) for tier in profile.tiers for entry in tier.accepted]
    used: set[int] = set()
    kept: list[Violation | Weak] = []
    excused: list[Excused] = []
    for item, found in said_of(rules, facts, profile):
        index = next((index for index, (tier, entry) in enumerate(entries)
                      if found.read.tier in (tier, "") and _accepts(entry, found, profile)), None)
        if index is None:
            kept.append(item)
            continue
        used.add(index)
        tier, entry = entries[index]
        excused.append(Excused(item.rule, item.file, item.line, f"tiers.{tier}.accepted", item.message, entry.why))
    stale = [_unused(tier, entry, facts, profile) for index, (tier, entry) in enumerate(entries) if index not in used]
    return Sifted(tuple(kept), tuple(stale), tuple(excused))


def _accepts(entry: AcceptedImport, found: Found, profile: Profile) -> bool:
    """Whether the entry names the finding: its file, and what it imports when it writes an import."""
    if entry.file != _written_path(found.read, profile):
        return False
    if not entry.target:
        return True
    tests = entry.target[:1] == (profile.default_tests,)
    kind = "import-into-tests" if tests else "import-into-app"
    target = module_steps(entry.target[1:] if tests else entry.target, profile.language.marks)
    return (found.fact.kind == kind and found.fact.target == target
            and (not entry.name or entry.name == found.fact.name))


def _unused(tier: str, entry: AcceptedImport, facts: Facts, profile: Profile) -> Violation:
    key, path = f"tiers.{tier}.accepted", "/".join(entry.file)
    what = f"{path} importing {entry.written}" if entry.target else f"the tiers findings of {path}"
    return Violation(_shown(entry.file, facts, profile), 0, f"{key} accepts {what}, and tiers finds none ({key})",
                     "tiers", _fix(path, key, facts, profile))


def _key(rule: str) -> str:
    return f"checks.{rule}.accepted"


def _stale(rule: str, entry: AcceptedFinding, facts: Facts, profile: Profile) -> Violation:
    key, path = _key(rule), "/".join(entry.file)
    what = (f"a finding of {path} with {' and '.join(f'{name} {said}' for name, said in entry.by)}" if entry.by
            else f"the findings of {path}")
    return Violation(_shown(entry.file, facts, profile), 0, f"{key} accepts {what}, and the check finds none ({key})",
                     rule, _fix(path, key, facts, profile), rule not in RULES)
