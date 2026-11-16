"""How `xarch profile explain` shows the words a check is written in, and the rules a key expands to: as text lines, or
as one JSON document, `{"ok": ...}` first.

checks: {"ok", "reading", "slots", "categories", "example": {"key", "profile", "check"}}, each slot {"name", "meaning",
"accepts"}, each category {"name", "meaning", "words"}, each word {"name", "meaning"}. A category: {"ok", "category",
"meaning", "words"}. A word: {"ok", "address", "category", "name", "meaning", "about", "applies_to", "side", "value",
"fields", "needs", "verb", "example"}, each field {"name", "meaning", "when"}; an example {"key", "profile",
"check"}, its profile null for a check written as one's own.
--rule: {"ok", "key", "profile", "rules", "checks"}. A refusal: {"ok": false, "error", ...}.
"""
from __future__ import annotations

from textwrap import fill
from typing import Any

from xarch.cli.reports.document import document
from xarch.modules.rules.contract import (
    CategoryShown,
    ChecksShown,
    KeyUnset,
    NoRuleShown,
    RuleShown,
    UnknownWords,
    WordShown,
    WordsShown,
)

WIDTH = 100
NAME = 22
"""The width of the column of names in a list of words."""
DEEPER = ("xarch profile explain <category>.<word>      one word in full, with an example, such as filters.public",
          "xarch profile explain <key> --rule           the rules a key of your profile expands to, as checks")
"""How to go deeper than the overview of a check."""


def checks_lines(shown: ChecksShown) -> list[str]:
    lines = ["how a check reads", *_filled(shown.reading, "  "), "", "slots"]
    width = max(len(slot.name) for slot in shown.slots)
    for slot in shown.slots:
        lines += _filled(f"{slot.name:<{width}}  {slot.meaning}: {slot.accepts}", "  ", " " * (width + 4))
    lines += ["", "words"]
    lines += [f"  {category.name:<12} {len(category.words):>2}  {category.meaning}" for category in shown.categories]
    if shown.example:
        lines += ["", f"example: {_source(shown.example_key, shown.example_profile)}",
                  *(f"  {line}" for line in shown.example.splitlines())]
    return [*lines, "", "go deeper", *(f"  {line}" for line in DEEPER)]


def _source(key: str, profile: str) -> str:
    """Where an example comes from, in words: a rule of a profile, or a check written as one's own."""
    return f"the rule {key} of {profile} expands to" if profile else f"a check of your own, {key}"


def checks_document(shown: ChecksShown) -> str:
    return document({"ok": True, "reading": shown.reading,
                  "slots": [{"name": s.name, "meaning": s.meaning, "accepts": s.accepts} for s in shown.slots],
                  "categories": [_category(c) for c in shown.categories],
                  "example": {"key": shown.example_key, "profile": shown.example_profile or None,
                              "check": shown.example} if shown.example else None})


def category_lines(shown: WordsShown) -> list[str]:
    category = shown.category
    lines = [category.name, *_filled(category.meaning, "  "), ""]
    for word in category.words:
        lines += _filled(f"{word.name:<{NAME}} {word.meaning}", "  ", " " * (NAME + 3))
    return [*lines, "", f"xarch profile explain {category.name}.<name>   one of them in full, with an example"]


def category_document(shown: WordsShown) -> str:
    return document({"ok": True, **{("category" if k == "name" else k): v for k, v in _category(shown.category).items()}})


def word_lines(shown: WordShown) -> list[str]:
    lines = [shown.address, *_filled(f"what: {shown.meaning}", "  ", "    ")]
    if shown.about_said:
        lines += [f"  about: {shown.about_said}"]
    if shown.value:
        lines += [f"  value: {shown.value}"]
    if shown.side:
        lines += [f"  side: the files of the {shown.side} only"]
    if shown.applies_to:
        lines += _filled(f"applies to: {', '.join(shown.applies_to)}", "  ", "    ")
    if shown.fields:
        lines.append("  fields:")
        width = max(len(f.name) for f in shown.fields)
        lines += [line for f in shown.fields for line in _filled(
            f"{f.name:<{width}}  {f.meaning}{f' (when {f.when} holds)' if f.when else ''}", "    ", " " * (width + 6))]
    if shown.needs:
        lines += _filled(f"needs of the language: {', '.join(shown.needs)}", "  ", "    ")
    if shown.verb:
        lines += [f"  verb: {shown.verb}"]
    if shown.example:
        lines += [f"  example: {_source(shown.example_key, shown.example_profile)}",
                  *(f"    {line}" for line in shown.example.splitlines())]
    else:
        lines += ["  example: none of the profiles' own rules uses it"]
    return lines


def word_document(shown: WordShown) -> str:
    return document({"ok": True, "address": shown.address, "category": shown.category, "name": shown.name,
                  "meaning": shown.meaning, "about": shown.about or None, "applies_to": list(shown.applies_to),
                  "side": shown.side or None, "value": shown.value or None,
                  "fields": [{"name": f.name, "meaning": f.meaning, "when": f.when or None} for f in shown.fields],
                  "needs": list(shown.needs), "verb": shown.verb or None,
                  "example": {"key": shown.example_key, "profile": shown.example_profile or None,
                              "check": shown.example} if shown.example else None})


def unknown_message(found: UnknownWords) -> str:
    return f"no word `{found.typed}` of a check: the nearest are {', '.join(found.nearest)}"


def unknown_document(found: UnknownWords) -> str:
    return document({"ok": False, "error": unknown_message(found), "typed": found.typed, "nearest": list(found.nearest)})


def rule_lines(shown: RuleShown) -> list[str]:
    noun = "rule" if shown.count == 1 else "rules"
    return [f"{shown.address} expands to {shown.count} {noun} in {shown.profile}, written as checks:", "",
            *shown.text.splitlines(), "",
            "to make one a check of your own: give it an id of your own, and examples (xarch profile explain checks)"]


def rule_document(shown: RuleShown) -> str:
    return document({"ok": True, "key": shown.address, "profile": shown.profile, "rules": shown.count,
                  "checks": shown.text, "needs": list(shown.needs)})


def unset_lines(unset: KeyUnset) -> list[str]:
    """A key the profile sets nowhere: where it would be set, and how a profile writes it."""
    lines = [f"{unset.address} in {unset.profile}: {_nowhere(unset)}, so it expands to no rule"]
    example = unset.facts.example
    return [*lines, "", "a profile writes it so:", *(f"  {line}" for line in example.splitlines())] if example else lines


def unset_document(unset: KeyUnset) -> str:
    return document({"ok": True, "key": unset.address, "profile": unset.profile, "rules": 0, "checks": "",
                  "set": False, "example": unset.facts.example or None})


def _nowhere(unset: KeyUnset) -> str:
    if not unset.facts.holder:
        return "the profile does not set it"
    return f"the profile sets {unset.facts.name} on no {unset.facts.holder}"


def no_rule_message(none: NoRuleShown) -> str:
    return f"{none.address} in {none.profile}: {none.reason}"


def _category(category: CategoryShown) -> dict[str, Any]:
    return {"name": category.name, "meaning": category.meaning,
            "words": [{"name": w.name, "meaning": w.meaning} for w in category.words]}


def _filled(text: str, indent: str, subsequent: str | None = None) -> list[str]:
    return fill(text, width=WIDTH, initial_indent=indent,
                subsequent_indent=subsequent if subsequent is not None else indent).splitlines()


