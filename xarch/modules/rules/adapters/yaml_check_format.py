"""The checks of a profile written as the YAML of its `checks` (see spec's written_checks for the format): each check
under its id, one slot to a line in the order a check is written, a slot left out when it says what the format
assumes, maps and lists of words on one line, and sentences quoted."""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from xarch.modules.rules.domain.rule import FAIL, MUST_BE_REACHED, MUST_REACH
from xarch.modules.rules.domain.vocabulary import TARGETS
from xarch.platform.yaml_writer import YamlWriter
from xarch.profile_values.checks import ANY, APP, STRUCTURE, Condition, Saying, Scope, WrittenCheck, WrittenTarget

INDENT = "  "
STRUCTURE_WORD = "structure"
"""How a scope names the structure."""
_VALUED = {kind.name for kind in TARGETS if kind.values}
"""The kinds of target that take values, which the format writes as a map even when they have none."""


class YamlCheckFormat:
    """Satisfies rules' CheckFormat port with the YAML writer of platform."""

    def __init__(self, writer: YamlWriter):
        self._writer = writer

    def written(self, checks: Mapping[str, WrittenCheck]) -> str:
        lines = ["checks:"]
        for name, check in checks.items():
            lines += [f"{INDENT}{name}:", *(INDENT * 2 + line for line in self._check(check))]
            if check.flagged or check.clean:
                lines += [f"{INDENT * 2}examples:",
                          *(f"{INDENT * 3}{side}: {self._files(files)}"
                            for side, files in (("flagged", check.flagged), ("clean", check.clean)))]
        return "\n".join(lines) + "\n"

    def _check(self, check: WrittenCheck) -> list[str]:
        lines = [f"read: {self._one_or_list(check.read)}"]
        scope = self._scope(check.within)
        lines += [f"in: {scope}"] if scope else []
        lines += [f"keep: {self._list(map(self._filter, check.keep))}"] if check.keep else []
        lines += self._quantified(check)
        lines += [f"except: {self._list(map(self._filter, check.exempt))}"] if check.exempt else []
        lines += [f"mode: {check.mode}"] if check.mode != FAIL else []
        *cases, last = check.sayings
        if cases:
            lines.append("cases:")
            for case in cases:
                said = self._saying(case)
                lines += [f"{INDENT}- {said[0]}", *(f"{INDENT}  {line}" for line in said[1:])]
        return [*lines, *self._saying(last)[1:]]

    def _files(self, files: tuple[tuple[str, str], ...]) -> str:
        shown = [f"{self._writer.word(path)}: {self._writer.quoted(code)}" for path, code in files]
        return f"{{{', '.join(shown)}}}"

    def _saying(self, saying: Saying) -> list[str]:
        lines = [f"when: {self._list(map(self._filter, saying.when))}", f"message: {self._writer.quoted(saying.message)}",
                 f"fix: {self._writer.quoted(saying.fix)}"]
        return lines + ([f"once_per: {self._list(saying.once)}"] if saying.once else [])

    def _quantified(self, check: WrittenCheck) -> list[str]:
        quantified = check.quantified
        if quantified.slot == MUST_REACH:
            lines = [f"{INDENT}targets: {self._targets(quantified.targets)}",
                     f"{INDENT}through: {self._one_or_list(quantified.through)}"]
            lines += [f"{INDENT}through_only: {self._list(map(self._filter, quantified.through_only))}"] \
                if quantified.through_only else []
            return [f"{quantified.slot}:", *lines]
        if quantified.slot == MUST_BE_REACHED:
            lines = [f"{INDENT}from: {self._scope(quantified.start or Scope(), always=True)}",
                     f"{INDENT}through: {self._one_or_list(quantified.through)}"]
            lines += [f"{INDENT}through_only: {self._list(map(self._filter, quantified.through_only))}"] \
                if quantified.through_only else []
            lines += [f"{INDENT}then_through: {self._one_or_list(quantified.then_through)}"] \
                if quantified.then_through else []
            lines += [f"{INDENT}by_another_file: true"] if quantified.by_another_file else []
            return [f"{quantified.slot}:", *lines]
        return [f"{quantified.slot}: {self._targets(quantified.targets)}"]

    def _scope(self, scope: Scope, always: bool = False) -> str:
        entries = [f"files: {scope.files}"] if scope.files != APP or always else []
        entries += [f"part: {STRUCTURE_WORD if scope.part == STRUCTURE else self._writer.word(scope.part)}"] \
            if scope.part != ANY else []
        entries += [f"tier: {self._writer.word(scope.tier)}"] if scope.tier else []
        entries += [f"where: {self._list(map(self._filter, scope.where))}"] if scope.where else []
        return f"{{{', '.join(entries)}}}" if entries else ""

    def _filter(self, condition: Condition) -> str:
        name = f"not {condition.name}" if condition.negated else condition.name
        return f"{{{name}: {self._writer.word(condition.value)}}}" if condition.value else name

    def _targets(self, targets: tuple[WrittenTarget, ...]) -> str:
        shown = [self._target(target) for target in targets]
        return shown[0] if len(shown) == 1 else f"[{', '.join(shown)}]"

    def _target(self, target: WrittenTarget) -> str:
        return f"{{{target.kind}: {self._list(target.values)}}}" if target.values or target.kind in _VALUED \
            else target.kind

    def _one_or_list(self, items: tuple[str, ...]) -> str:
        return self._writer.word(items[0]) if len(items) == 1 else self._list(items)

    def _list(self, items: Iterable[str]) -> str:
        return f"[{', '.join(item if item.startswith('{') else self._writer.word(item) for item in items)}]"
