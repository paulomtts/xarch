"""What a part's `imports` says: what it may import, what each of its files must import one of, and the outside
packages it may import, in one group.

    imports: {may: [<target> | {<target>: types_only}, ...] | everything, must: [<target>, ...],
              libraries: [<package>, ...] | everything}

An entry of `may` is a target as the target grammar writes it (see kernel/logic/targets), or a map of one target to its
mode; the only mode is `types_only`, a target the part may import only to use as a type. A marked entry is an entry of
`may` like any other, its mark read apart. `must` takes targets alone, each one an entry of `may`. The old keys of a
part, and `never` and `types_only` written in the group, are refused from the table of retired names.

A tier's `imports`, {may, also, must, types_only}, is checked as a group by the same `group`, under its own scope and
with its own example; the tier parser reads its keys (see profile_parsing).
"""
from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Any

from xarch.kernel.placement import EVERYTHING
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import keys_of, names_of
from xarch.modules.spec.application.logic.targets_written import WORD, allowed_targets
from xarch.modules.spec.domain.profile_keys import PART_IMPORTS
from xarch.modules.spec.domain.values import Part
from xarch.profile_values.placement import Repeat, Target

MODE = "types_only"
"""The one mode an entry of `may` takes."""


def group(spec: Mapping[Any, Any], where: str, problems: list[str], scope: str = PART_IMPORTS,
          example: str = "{may: [<part>]}") -> Mapping[Any, Any]:
    """The `imports` of the part or tier at where, its keys those of the scope: {} when it writes none, or when it is
    no map or says nothing, each problem added, naming the keys in the order of the table and showing the example;
    its unknown keys are refused under the scope."""
    if "imports" not in spec:
        return {}
    value, at = spec["imports"], f"{where}.imports"
    names = [key.name for key in keys_of(scope)]
    if not isinstance(value, Mapping):
        problems.append(f"{at}: must be a map of {_joined(names, 'and')}, such as {example}")
        return {}
    if not value:
        problems.append(f"{at}: says nothing: write {_joined(names, 'or')}, or drop it")
        return {}
    problems += ck.unknown_keys(value, names_of(scope), at, scope)
    return value


def _joined(names: list[str], word: str) -> str:
    """The names in order, the last after the word: may, must and libraries."""
    return f"{', '.join(names[:-1])} {word} {names[-1]}"


def may(value: Any, owner: Part, parts: dict[str, Part], declared: set[str], where: str,
        problems: list[str], *, repeats: Collection[Repeat]) -> tuple[tuple[Target, ...], tuple[Target, ...]]:
    """What the part may import, every entry as its target, marked or not, in the order written; and the targets of
    its marked entries, in the same order. An entry refused adds its problem and is in neither. repeats are the
    profile's repeating folders, whose words a reference names."""
    if not isinstance(value, list):
        return allowed_targets(value, owner, parts, declared, where, problems, patterns=True, repeats=repeats), ()
    allowed: list[Target] = []
    marked: list[Target] = []
    for entry in value:
        written = _marked(entry, where, problems) if isinstance(entry, Mapping) else entry
        if written is None:
            continue
        found = allowed_targets([written], owner, parts, declared, where, problems, patterns=True, repeats=repeats)
        allowed += found
        if isinstance(entry, Mapping):
            marked += found
    return tuple(allowed), tuple(marked)


def must(written: Mapping[Any, Any], owner: Part, parts: dict[str, Part], declared: set[str],
         allowed: tuple[Target, ...], problems: list[str], *, repeats: Collection[Repeat]) -> tuple[Target, ...]:
    """The targets each file of the part must import one of: each one an entry of `may` (allowed), marked or not."""
    where = f"parts.{owner.name}.imports.must"
    if "must" not in written:
        return ()
    value = written["must"]
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of targets such as [<part>, <part>@any]")
        return ()
    count = len(problems)
    problems += [f"{where}: {_shown(item)}: must takes references only, with no mode" for item in value
                 if isinstance(item, Mapping)]
    found = (allowed_targets(value, owner, parts, declared, where, problems, repeats=repeats) if len(problems) == count
             else ())
    if len(problems) != count:
        return ()
    for item, target in zip(value, found):
        if not any(t.part == EVERYTHING or t == target for t in allowed):
            problems.append(f"{where}: {item!r} is not in imports.may, so no file could import it: add it there, or "
                            "name a part the part may import")
    return found if len(problems) == count else ()


def _marked(entry: Mapping[Any, Any], where: str, problems: list[str]) -> Any:
    """The target a marked entry of `may` writes; None, with its problem, when the entry is no map of one target to
    the mode."""
    if len(entry) != 1:
        problems.append(f"{where}: {_shown(entry)}: one reference per entry: write each in its own {{...}}")
        return None
    ((target, mode),) = entry.items()
    if target == WORD:
        problems.append(f"{where}: {WORD} takes no mode: list the entries to give one a mode")
        return None
    if mode != MODE:
        problems.append(f"{where}: {_shown(entry)}: no mode {mode!r}: write {MODE}, or the reference alone")
        return None
    return target


def _shown(entry: Mapping[Any, Any]) -> str:
    """A map entry as a profile writes it, in flow style: {ports: types_only}."""
    return "{" + ", ".join(f"{_scalar(key)}: {_scalar(value)}" for key, value in entry.items()) + "}"


def _scalar(value: Any) -> str:
    """A value as a profile writes it: true, false and null in their own words."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return "null" if value is None else str(value)
