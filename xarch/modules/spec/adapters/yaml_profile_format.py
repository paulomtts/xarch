"""A profile xarch writes, as a YAML file that reads as one written by hand; and the checks of a profile written as the
YAML of its `checks` (see written_checks for the format): each check under its id, one slot to a line in the order a
check is written, a slot left out when it says what the format assumes, maps and lists of words on one line, and
sentences quoted."""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from xarch.modules.spec.domain.values import CASE_SLOTS, EXAMPLE_SLOTS, REACH_SLOTS, SCOPE_SLOTS, SLOTS, STRUCTURE_WORD
from xarch.platform.yaml_writer import YamlWriter
from xarch.profile_values.checks import (
    ANY,
    APP,
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


class YamlProfileFormat:
    """Satisfies spec's ProfileFormat port."""

    def __init__(self, writer: YamlWriter):
        self._writer = writer

    def written(self, document: dict[str, Any]) -> bytes:
        return self._writer.dump(document).encode("utf-8")

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
                "once_per": [f"once_per: {self._list(saying.once)}"] if saying.once else []}

    def _quantified(self, quantified: Quantified) -> list[str]:
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
