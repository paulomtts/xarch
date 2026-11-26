"""A profile xarch writes, as a YAML file that reads as one written by hand, its `parts` as the folder tree in canonical
form (see _tree); and the checks of a profile written as the YAML of its `checks` (see written_checks for the format):
each check under its id, one slot to a line in the order a check is written, a slot left out when it says what the
format assumes, maps and lists of words on one line, and sentences quoted."""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from xarch.modules.spec.domain.values import CASE_SLOTS, EXAMPLE_SLOTS, REACH_SLOTS, SCOPE_SLOTS, SLOTS, STRUCTURE_WORD
from xarch.platform.yaml_writer import YamlWriter
from xarch.profile_values.checks import (
    ANY,
    APP,
    COUNT_SLOTS,
    FAIL,
    NEGATION,
    STRUCTURE,
    Condition,
    Quantified,
    Saying,
    Scope,
    WrittenCheck,
    WrittenTarget,
)

_NAME = re.compile(r"^name:.*$", re.MULTILINE)
"""The top-level `name` line of a YAML profile."""
_BASED_ON = re.compile(r"^based_on:.*\n", re.MULTILINE)
"""The top-level `based_on` line of a YAML profile, with its line break."""
_INDENT = "  "
"""How far a line of the checks is indented below the line that holds it."""
_PART_KEYS = ("name", "role", "litmus", "imports", "uses", "holds", "shared", "package_only", "tests", "untested")
"""The keys of a part in the order a profile writes them, before the folders and files below the part."""


class YamlProfileFormat:
    """Satisfies spec's ProfileFormat port."""

    def __init__(self, writer: YamlWriter):
        self._writer = writer

    def written(self, document: dict[str, Any]) -> bytes:
        parts = document.get("parts")
        shown = {**document, "parts": _tree(parts)} if isinstance(parts, Mapping) else document
        return self._writer.dump(shown).encode("utf-8")

    def renamed(self, text: str, name: str, based_on: str) -> str | None:
        without = _BASED_ON.sub("", text)
        if _NAME.search(without) is None:
            return None
        return _NAME.sub(lambda _: f"name: {name}\nbased_on: {based_on}", without, count=1)

    def checks(self, checks: Mapping[str, WrittenCheck]) -> str:
        lines = ["checks:"]
        for name, check in checks.items():
            lines += [f"{_INDENT}{name}:", *(_INDENT * 2 + line for line in self._check(check))]
        return "\n".join(lines) + "\n"

    def _check(self, check: WrittenCheck) -> list[str]:
        """The slots the check says, in the order of the format's SLOTS."""
        *cases, last = check.sayings
        own = self._saying(last)
        scope = self._scope(check.within)
        said = {"read": [f"read: {self._one_or_list(check.read)}"],
                "in": [f"in: {scope}"] if scope else [],
                "keep": [f"keep: {self._list(map(self._filter, check.keep))}"] if check.keep else [],
                check.quantified.slot: self._quantified(check.quantified),
                "except": [f"except: {self._list(map(self._filter, check.exempt))}"] if check.exempt else [],
                "mode": [f"mode: {check.mode}"] if check.mode != FAIL else [],
                **{slot: own[slot] for slot in CASE_SLOTS if slot in own and slot != "when"},
                "cases": ["cases:", *(line for case in cases for line in self._case(case))] if cases else [],
                "examples": self._examples(check)}
        return _ordered(said, SLOTS)

    def _case(self, case: Saying) -> list[str]:
        lines = _ordered(self._saying(case), CASE_SLOTS)
        return [f"{_INDENT}- {lines[0]}", *(f"{_INDENT}  {line}" for line in lines[1:])]

    def _examples(self, check: WrittenCheck) -> list[str]:
        files = {"flagged": check.flagged, "clean": check.clean}
        if not any(files.values()):
            return []
        return ["examples:", *(f"{_INDENT}{side}: {self._files(files[side])}" for side in EXAMPLE_SLOTS)]

    def _files(self, files: tuple[tuple[str, str], ...]) -> str:
        shown = [f"{self._writer.word(path)}: {self._writer.quoted(code)}" for path, code in files]
        return f"{{{', '.join(shown)}}}"

    def _saying(self, saying: Saying) -> dict[str, list[str]]:
        return {"when": [f"when: {self._list(map(self._filter, saying.when))}"],
                "message": [f"message: {self._writer.quoted(saying.message)}"],
                "fix": [f"fix: {self._writer.quoted(saying.fix)}"],
                "once_per": [f"once_per: {self._list(saying.once)}"] if saying.once else [],
                "per_line": [f"per_line: {self._list(saying.per_line)}"] if saying.per_line else []}

    def _quantified(self, quantified: Quantified) -> list[str]:
        if quantified.slot in COUNT_SLOTS:
            return [f"{quantified.slot}: {quantified.count}"]
        if quantified.slot not in REACH_SLOTS:
            return [f"{quantified.slot}: {self._targets(quantified.targets)}"]
        said = {"targets": [f"targets: {self._targets(quantified.targets)}"],
                "from": [f"from: {self._scope(quantified.start or Scope(), always=True)}"],
                "through": [f"through: {self._one_or_list(quantified.through)}"],
                "through_only": [f"through_only: {self._list(map(self._filter, quantified.through_only))}"]
                if quantified.through_only else [],
                "then_through": [f"then_through: {self._one_or_list(quantified.then_through)}"]
                if quantified.then_through else [],
                "by_another_file": ["by_another_file: true"] if quantified.by_another_file else []}
        return [f"{quantified.slot}:", *(f"{_INDENT}{line}" for line in _ordered(said, REACH_SLOTS[quantified.slot]))]

    def _scope(self, scope: Scope, always: bool = False) -> str:
        said = {"files": [f"files: {scope.files}"] if scope.files != APP or always else [],
                "part": [f"part: {STRUCTURE_WORD if scope.part == STRUCTURE else self._writer.word(scope.part)}"]
                if scope.part != ANY else [],
                "tier": [f"tier: {self._writer.word(scope.tier)}"] if scope.tier else [],
                "where": [f"where: {self._list(map(self._filter, scope.where))}"] if scope.where else []}
        entries = _ordered(said, SCOPE_SLOTS)
        return f"{{{', '.join(entries)}}}" if entries else ""

    def _filter(self, condition: Condition) -> str:
        name = f"{NEGATION}{condition.name}" if condition.negated else condition.name
        return f"{{{name}: {self._writer.word(condition.value)}}}" if condition.value else name

    def _targets(self, targets: tuple[WrittenTarget, ...]) -> str:
        shown = [self._target(target) for target in targets]
        return shown[0] if len(shown) == 1 else f"[{', '.join(shown)}]"

    def _target(self, target: WrittenTarget) -> str:
        return target.kind if target.values is None else f"{{{target.kind}: {self._list(target.values)}}}"

    def _one_or_list(self, items: tuple[str, ...]) -> str:
        return self._writer.word(items[0]) if len(items) == 1 else self._list(items)

    def _list(self, items: Iterable[str]) -> str:
        return f"[{', '.join(item if item.startswith('{') else self._writer.word(item) for item in items)}]"


def _ordered(said: Mapping[str, list[str]], slots: Iterable[str]) -> list[str]:
    """The lines said for each of slots, in their order; what is said for no slot of them is not written."""
    return [line for slot in slots for line in said.get(slot, [])]


def _tree(parts: Mapping[str, Any]) -> dict[str, Any]:
    """The folder tree in canonical form: each key split into its steps and the tree built again, a part's own keys
    first in the order a profile writes them, then its folders and files in the order given; a folder that is no part,
    has no note and holds one entry joined with that entry; a folder holding nothing written {}."""
    return _joined(_nested(parts))


def _below(key: str) -> bool:
    """Whether a key of the tree is a folder (it ends in `/`) or a file (it holds a dot), not a key of a part."""
    return key.endswith("/") or "." in key


def _nested(node: Mapping[str, Any]) -> dict[str, Any]:
    """The node with its own keys in the order a profile writes them and each folder or file key one step to a
    level."""
    own = sorted((key for key in node if not _below(key)),
                 key=lambda key: _PART_KEYS.index(key) if key in _PART_KEYS else len(_PART_KEYS))
    nested: dict[str, Any] = {key: node[key] for key in own}
    for key, value in node.items():
        if _below(key):
            _put(nested, key, value)
    return nested


def _put(nested: dict[str, Any], key: str, value: Any) -> None:
    """The folder or file a key writes, put in nested one step to a level; a folder given twice holds what both give,
    its own keys first."""
    first, slash, rest = key.partition("/")
    if rest:
        held = nested.get(f"{first}/")
        if not isinstance(held, dict):
            held = nested[f"{first}/"] = {}
        _put(held, rest, value)
        return
    step = f"{first}{slash}"
    held = nested.get(step)
    if not isinstance(held, dict) or not isinstance(value, Mapping):
        nested[step] = _nested(value) if isinstance(value, Mapping) else value
        return
    merged = {**held, **{key: item for key, item in value.items() if not _below(key)}}
    for key, item in value.items():
        if _below(key):
            _put(merged, key, item)
    nested[step] = _nested(merged)


def _joined(nested: dict[str, Any]) -> dict[str, Any]:
    """The nested tree with each folder that is no part, has no note and holds one entry joined with that entry, and
    each folder holding nothing as {}."""
    joined: dict[str, Any] = {}
    for key, value in nested.items():
        if _below(key) and isinstance(value, Mapping):
            value = _joined(dict(value))
            if key.endswith("/") and len(value) == 1 and _below(next(iter(value))):
                ((step, value),) = value.items()
                key += step
        joined[key] = {} if value is None and key.endswith("/") else value
    return joined
