"""The counterpart rule: what the profile says lies with what (counterparts), held against the files the disk shows
below the app and below the tests.

A path matches a pattern step by step. `*` is any text within a step; a placeholder, `<word>`, binds the text of a
step or of part of one to a name of the language that is no private one, the same text wherever the pattern writes it
twice; the word of a repeating folder, written as a whole step at that folder's place below the app, binds only its
instances, never a folder the layout names beside them. A folder is there when a file lies below it; a file where a
folder is wanted is none.

Each match of a counterpart's source, every path of its when matching too with the source's bindings, that
has no match of its `has` so bound is a finding at it, but one its `accepted` names, which is waived with the entry's
reason. An entry that waives nothing (its source now has its counterpart, or is gone) is a finding itself, so a list
of accepted sources can only shrink; one below the app written with the app folder's name first is told to write its
path below the app. How many matches of its source each counterpart read is counted: one that read
none passes for want of anything to check.
"""
from __future__ import annotations

import re
from collections.abc import Collection, Iterable, Mapping

from xarch.kernel.logic.accepted_paths import stale_fix
from xarch.kernel.violations import Violation
from xarch.modules.layout.application.logic.instances import is_instance_name
from xarch.modules.layout.domain.published import Waived
from xarch.modules.layout.domain.structure import Allowed, Counterpart, Naming, Pattern, Word

RULE = "counterpart"
"""The id of the rule."""
_TOKEN = re.compile(r"<([^<>]*)>|\*")
_VARIABLE = re.compile(r"\{([^{}]*)\}")

Path = tuple[str, ...]
Bound = Mapping[str, str]
Paired = tuple[tuple[Violation, ...], tuple[Waived, ...], tuple[tuple[str, int], ...]]
"""What the counterparts come to: the violations, each source accepted with none, and how many matches of its source
each counterpart read, by its id."""
Side = tuple[frozenset[Path], frozenset[Path]]
"""The files the disk shows below one root, then the folders holding them, each by its steps below it."""


def _side(files: Iterable[Path]) -> Side:
    found = frozenset(files)
    return found, frozenset(path[:size] for path in found for size in range(1, len(path)))


def _of(side: Side, pattern: Pattern) -> list[Path]:
    """What the pattern can match on the side, sorted: the folders, or the files, of as many steps."""
    files, folders = side
    return sorted(path for path in (folders if pattern.folder else files) if len(path) == len(pattern.steps))


def paired(counterparts: Iterable[Counterpart], app: Iterable[Path], tests: Iterable[Path] | None,
           words: Iterable[Word], naming: Naming, package: str, tests_root: str | None) -> Paired:
    """What the counterparts find below the app (app, its files) and below the tests (tests, its files; None when there
    are none), in the order of the counterparts then of their sources, each counterpart's stale entries after its
    findings; package and tests_root name the app root and the tests root in the files of the findings."""
    sides = {False: _side(app), True: _side(tests or ())}
    roots = {False: package, True: tests_root or "tests"}
    found: list[Violation] = []
    waived: list[Waived] = []
    read: list[tuple[str, int]] = []
    words = tuple(words)
    for entry in counterparts:
        sources = matches(entry.source, sides[entry.source.tests], words, naming)
        read.append((entry.id, len(sources)))
        key = f"counterparts.{entry.id}"
        accepted = {(item.path, item.tests): item for item in entry.accepted}
        used: set[tuple[Path, bool]] = set()
        for path, bound in sources:
            if not all(matches(when, sides[when.tests], words, naming, bound) for when in entry.when):
                continue
            has = bool(matches(entry.has, sides[entry.has.tests], words, naming, bound))
            said = _said(entry, path, bound)
            file = "/".join((roots[entry.source.tests], *path))
            item = accepted.get((path, entry.source.tests))
            if item is not None:
                used.add((path, entry.source.tests))
                if has:
                    found.append(Violation(file, 0, f"{key}.accepted names {item.written}, which now has its "
                                                    f"counterpart {said['expected']}", RULE,
                                           f"drop the entry of {item.written} from {key}.accepted"))
                else:
                    waived.append(Waived(RULE, file, _message(entry, said), item.why, f"{key}.accepted"))
            elif not has:
                found.append(Violation(file, 0, _message(entry, said), RULE, _fix(entry, said)))
        found += [Violation("/".join((roots[item.tests], *item.path)), 0,
                            f"{key}.accepted names {item.written}, which is no match of {entry.source.written} that "
                            f"needs a counterpart ({key})", RULE, _unused_fix(item, key, sides[False], package))
                  for at, item in accepted.items() if at not in used]
    return tuple(found), tuple(waived), tuple(read)


def _unused_fix(item: Allowed, key: str, app: Side, package: str) -> str:
    """The fix of an entry of accepted that accepts nothing: to drop it, or, for one below the app written with the
    app folder's name first, to write its path below the app."""
    fix = f"drop the entry of {item.written} from {key}.accepted"
    files, folders = app
    return fix if item.tests else stale_fix(item.written, package, lambda steps: steps in files or steps in folders, fix)


def matches(pattern: Pattern, side: Side, words: Collection[Word], naming: Naming,
            bound: Bound | None = None) -> list[tuple[Path, dict[str, str]]]:
    """Each path of the side the pattern matches, sorted, with the text each placeholder binds, those of bound put
    back as bound."""
    found = []
    for path in _of(side, pattern):
        bindings = _matched(pattern, path, words, naming, dict(bound or {}))
        if bindings is not None:
            found.append((path, bindings))
    return found


def _matched(pattern: Pattern, path: Path, words: Collection[Word], naming: Naming,
             bound: dict[str, str]) -> dict[str, str] | None:
    """The bindings with those the path adds, None when the pattern does not match it."""
    for at, (want, step) in enumerate(zip(pattern.steps, path)):
        names: list[str] = []
        hit = re.fullmatch(_regex(want, bound, names), step)
        if hit is None:
            return None
        for index, name in enumerate(names):
            text = hit.group(f"g{index}")
            if not is_instance_name(text, naming) or _beside(name, want, pattern, at, text, words):
                return None
            bound[name] = text
    return bound


def _regex(want: str, bound: Bound, names: list[str]) -> str:
    """A step of a pattern as a regular expression, a placeholder bound as its text; names gains each placeholder the
    step binds, in order, as the group g<its index> holds it."""
    pieces: list[str] = []
    last = 0
    for token in _TOKEN.finditer(want):
        pieces.append(re.escape(want[last:token.start()]))
        name = token.group(1)
        if name is None:
            pieces.append(".*")
        elif name in bound:
            pieces.append(re.escape(bound[name]))
        elif name in names:
            pieces.append(f"(?P=g{names.index(name)})")
        else:
            pieces.append(f"(?P<g{len(names)}>.+)")
            names.append(name)
        last = token.end()
    return "".join(pieces) + re.escape(want[last:])


def _beside(name: str, want: str, pattern: Pattern, at: int, text: str, words: Iterable[Word]) -> bool:
    """Whether the text is a folder the layout names beside the instances of a repeating folder whose word the
    placeholder is, written as the whole step at that folder's place below the app."""
    return not pattern.tests and want == f"<{name}>" and any(
        word.word == name and word.root == pattern.steps[:at] and text in word.named for word in words)


def _said(entry: Counterpart, path: Path, bound: Bound) -> dict[str, str]:
    """What a message or a fix of a source with no counterpart prints, by variable."""
    source = Pattern(path, entry.source.tests, entry.source.folder).written
    when = ", ".join(_bind(item, bound).written for item in entry.when)
    return {**bound, "source": source, "expected": _bind(entry.has, bound).written, "when": when,
            "key": f"counterparts.{entry.id}"}


def _bind(pattern: Pattern, bound: Bound) -> Pattern:
    """The pattern with each placeholder bound put back as its text; `*` is kept."""
    return Pattern(tuple(_TOKEN.sub(lambda token: bound.get(token.group(1) or "", token.group(0)), step)
                         for step in pattern.steps), pattern.tests, pattern.folder)


def _message(entry: Counterpart, said: Mapping[str, str]) -> str:
    if entry.message:
        return _filled(entry.message, said)
    though = f", though it has {said['when']}" if said["when"] else ""
    return f"{said['source']} has no {said['expected']}{though} ({said['key']})"


def _fix(entry: Counterpart, said: Mapping[str, str]) -> str:
    if entry.fix:
        return _filled(entry.fix, said)
    return (f"create {said['expected']}, or name {said['source']} under {said['key']}.accepted with the reason it has "
            "none")


def _filled(text: str, said: Mapping[str, str]) -> str:
    """The text with each variable it writes as its value."""
    return _VARIABLE.sub(lambda variable: said.get(variable.group(1), variable.group(0)), text)
