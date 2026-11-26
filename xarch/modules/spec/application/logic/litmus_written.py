"""What a part's or a tier's `litmus` says: one text, as before, or a list of entries.

    litmus: <text> | [<text> | {ask, label, mode}, ...]

An entry written as a text alone is its ask. Its label is its own among the entries, its position counted from 1 when
it writes none; its mode is `any` (an alternative) unless written `all` (a condition). An entry is refused at its
address, `<where>[<i>]`: an empty text, a label another entry has, an unknown mode or a key that is none of these.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of, required_of
from xarch.profile_values.litmus import ALL, ANY, Litmus

MODES = (ANY, ALL)
"""The modes an entry may be written with, ANY its default."""
ENTRY = "{ask, label, mode}"
"""How an entry written as a map is shown in a refusal."""


def litmus(value: Any, where: str, scope: str, belongs: str, problems: list[str]) -> tuple[str, tuple[Litmus, ...]]:
    """The litmus written at where: its one text (the entries none), or its entries in the order written (the text
    ""); scope is the scope of an entry's keys and belongs what a question tells, said in a refusal. A litmus refused
    adds its problems and reads as none."""
    if isinstance(value, str):
        return value, ()
    if not isinstance(value, list):
        problems.append(f"{where}: must be a string, or a list of entries, each a text or {ENTRY}")
        return "", ()
    if not value:
        problems.append(f"{where}: must hold at least one entry: a text, or {ENTRY}")
        return "", ()
    count = len(problems)
    entries = [_entry(item, f"{where}[{i}]", i, scope, belongs, problems) for i, item in enumerate(value)]
    labels: dict[str, int] = {}
    for i, entry in enumerate(entries):
        if entry is None:
            continue
        if entry.label in labels:
            problems.append(f"{where}[{i}].label: '{entry.label}' is the label of litmus[{labels[entry.label]}] too: "
                            "give each entry its own")
        labels.setdefault(entry.label, i)
    if len(problems) != count:
        return "", ()
    return "", tuple(entry for entry in entries if entry is not None)


def _entry(item: Any, at: str, i: int, scope: str, belongs: str, problems: list[str]) -> Litmus | None:
    question = f"must be text: a question that tells {belongs}"
    if isinstance(item, str):
        if not ck.text(item):
            problems.append(f"{at}: {question}")
            return None
        return Litmus(item.strip("\n"), str(i + 1))
    if not isinstance(item, Mapping):
        problems.append(f"{at}: must be a text, or a map {ENTRY}")
        return None
    count = len(problems)
    problems += ck.unknown_keys(item, names_of(scope), at, scope)
    problems += [f"{at}: missing `{key}`" for key in required_of(scope) if key not in item]
    ask, label, mode = item.get("ask"), item.get("label", str(i + 1)), item.get("mode", ANY)
    if "ask" in item and not ck.text(ask):
        problems.append(f"{at}.ask: {question}")
    if not ck.line(label):
        problems.append(f"{at}.label: must be one line of text: a short name of the entry")
    if mode not in MODES:
        problems.append(f"{at}.mode: '{mode}' is no mode: use {', '.join(sorted(MODES))}")
    if len(problems) != count:
        return None
    return Litmus(ask.strip("\n"), label.strip(), mode)
