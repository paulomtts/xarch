"""A rule written in the syntax a profile writes its own checks in (see spec's written_checks): what `xarch profile
explain <key> --rule` prints for a key's rules, so that a check xarch has reads as a check a profile could write. A
rule written so and read back is the same rule, its id and key aside: a check of one's own takes an id of its own, and
its key is `checks.<id>`.
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterable

from xarch.kernel.logic.language import LanguageView
from xarch.kernel.placement import Target
from xarch.modules.rules.domain.rule import (
    ANY,
    APP,
    EXISTING,
    FAIL,
    MUST_BE_REACHED,
    MUST_REACH,
    STRUCTURE,
    Condition,
    Match,
    OwnCheck,
    Rule,
    Saying,
    Scope,
)

PLAIN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./@()-]*(?: [A-Za-z0-9_./@()-]+)*")
"""A word written without quotes: what YAML reads as the text it is, in a list or a map written on one line."""
INDENT = "  "
_IMPORT = re.compile(r"%import (?P<dotted>[^ %]+) (?P<name>[^ %]+)%")
"""The token of a line that imports a name from a file of the app, in the code of a check written for the
explanation."""


def written(rules: Iterable[Rule], ids: Iterable[str]) -> str:
    """The rules as the `checks` of a profile, each under its id."""
    lines = ["checks:"]
    for rule, name in zip(rules, ids):
        lines += [f"{INDENT}{name}:", *(INDENT * 2 + line for line in check(rule))]
    return "\n".join(lines) + "\n"


def written_own(checks: Iterable[OwnCheck], language: LanguageView) -> str:
    """Checks of a profile's own as its `checks` are written, each under its id with its examples, the tokens of
    the language (see filled) in their code filled in."""
    lines = ["checks:"]
    for own in checks:
        lines += [f"{INDENT}{own.rule.id}:", *(INDENT * 2 + line for line in check(own.rule)),
                  f"{INDENT * 2}examples:",
                  *(f"{INDENT * 3}{side}: {_files(files, language)}"
                    for side, files in (("flagged", own.flagged), ("clean", own.clean)))]
    return "\n".join(lines) + "\n"


def _files(files: tuple[tuple[str, str], ...], language: LanguageView) -> str:
    shown = [f"{_word(filled(path, language))}: {_quoted(filled(code, language))}" for path, code in files]
    return f"{{{', '.join(shown)}}}"


def filled(text: str, language: LanguageView) -> str:
    """The text with the tokens of the language filled in: `%extension%`, `%comment%`, and `%import <dotted> <name>%`,
    a line that imports name from the file of the app that dotted names, as the language's importing says
    (left as written when it does not say)."""
    text = text.replace("%extension%", language.extension).replace("%comment%", language.comment)
    if not language.importing:
        return text
    return _IMPORT.sub(lambda found: language.importing.format(dotted=found["dotted"], name=found["name"]), text)


def check(rule: Rule) -> list[str]:
    """The slots of one check, in the order a check is written."""
    lines = [f"read: {_one_or_list(rule.facts)}"]
    scope = _scope(rule.scope)
    lines += [f"in: {scope}"] if scope else []
    lines += [f"keep: {_list(map(_filter, rule.keep))}"] if rule.keep else []
    lines += _quantified(rule)
    lines += [f"except: {_list(map(_filter, rule.exempt))}"] if rule.exempt else []
    lines += [f"mode: {rule.mode}"] if rule.mode != FAIL else []
    *cases, last = rule.sayings
    if cases:
        lines.append("cases:")
        for case in cases:
            said = _saying(case)
            lines += [f"{INDENT}- {said[0]}", *(f"{INDENT}  {line}" for line in said[1:])]
    return [*lines, *_saying(last)[1:]]


def _saying(saying: Saying) -> list[str]:
    lines = [f"when: {_list(map(_filter, saying.when))}", f"message: {_quoted(saying.message)}",
             f"fix: {_quoted(saying.fix)}"]
    return lines + ([f"once_per: {_list(saying.once)}"] if saying.once else [])


def _quantified(rule: Rule) -> list[str]:
    if rule.quantifier == MUST_REACH:
        lines = [f"{INDENT}targets: {_targets(rule.targets)}", f"{INDENT}through: {_one_or_list(rule.links)}"]
        lines += [f"{INDENT}through_only: {_list(map(_filter, rule.via))}"] if rule.via else []
        return [f"{rule.quantifier}:", *lines]
    if rule.quantifier == MUST_BE_REACHED:
        lines = [f"{INDENT}from: {_scope(rule.roots or Scope(), always=True)}",
                 f"{INDENT}through: {_one_or_list(rule.links)}"]
        lines += [f"{INDENT}through_only: {_list(map(_filter, rule.via))}"] if rule.via else []
        lines += [f"{INDENT}then_through: {_one_or_list(rule.spread)}"] if rule.spread else []
        lines += [f"{INDENT}by_another_file: true"] if rule.elsewhere else []
        return [f"{rule.quantifier}:", *lines]
    return [f"{rule.quantifier}: {_targets(rule.targets)}"]


def _scope(scope: Scope, always: bool = False) -> str:
    entries = [f"files: {scope.files}"] if scope.files != APP or always else []
    entries += [f"part: {'structure' if scope.part == STRUCTURE else _word(scope.part)}"] if scope.part != ANY else []
    entries += [f"tier: {_word(scope.tier)}"] if scope.tier else []
    entries += [f"where: {_list(map(_filter, scope.where))}"] if scope.where else []
    return f"{{{', '.join(entries)}}}" if entries else ""


def _filter(condition: Condition) -> str:
    name = f"not {condition.name}" if condition.negated else condition.name
    return f"{{{name}: {_word(condition.value)}}}" if condition.value else name


def _targets(targets: tuple[Match, ...]) -> str:
    if targets == EXISTING:
        return "exist"
    shown = [_target(match) for match in targets]
    return shown[0] if len(shown) == 1 else f"[{', '.join(shown)}]"


def _target(match: Match) -> str:
    values = [*(_place(t) for t in match.places), *(_dotted(n) for n in match.names), *match.words]
    return f"{{{match.kind}: {_list(values)}}}" if values or match.kind not in ("exist", "permitted", "outside") \
        else match.kind


def _place(target: Target) -> str:
    return target.part + ("@any" if target.scope == "any" else "") + ("/" + "/".join(target.sub) if target.sub else "")


def _dotted(name: tuple[str, ...]) -> str:
    return f".{name[1]}" if len(name) == 2 and not name[0] else ".".join(name)


def _one_or_list(items: tuple[str, ...]) -> str:
    return _word(items[0]) if len(items) == 1 else _list(items)


def _list(items: Iterable[str]) -> str:
    return f"[{', '.join(item if item.startswith('{') else _word(item) for item in items)}]"


def _word(text: str) -> str:
    return text if PLAIN.fullmatch(text) and text not in ("true", "false", "null", "yes", "no") else _quoted(text)


def _quoted(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)
