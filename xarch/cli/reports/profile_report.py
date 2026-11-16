"""How the `xarch profile` commands show what they found: as text lines, or (for explain and check) as one JSON
document, `{"ok": ...}` first, a refusal being `{"ok": false, "error": ...}`.

explain, no key: {"ok", "format", "shape", "symbols", "smallest", "deeper"}, each shape entry {"key", "depth",
"meaning", "required", "enforced"}. explain, one key: {"ok", "key", "where", "meaning", "accepts", "required",
"enforced", "rules", "example", "choices", "keys", "needs", "language"}, each need {"fact", "meaning", "grade",
"note"}: a fact of the source the key's check reads, and how the language named supplies it. explain, a profile:
{"ok", "profile", "name", "tree", "imports"}.
check: {"ok", "profile", "problems", "files", "compared_with"}, each problem {"check", "message"} and
compared_with {"profile", "looser"} (null for a bundled profile or one that resembles none), each looser entry
{"key", "part", "what", "sentence"}.
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from textwrap import fill
from typing import Any

from xarch.modules.spec.contract import (
    EXAMPLES,
    LOAD,
    FormatExplained,
    KeyExplained,
    Migrated,
    ProfileChecked,
    ProfileCreated,
    ProfileViewed,
    Shown,
    UnknownKey,
)

WIDTH = 100
KEY = 28
"""The width of the column of keys in the overview."""
NEED = 10
"""The width of the column that says whether a key is required."""
NO_RULE = "yes (the loader, or the `enforcement` section of `check`, not a rule id)"
DEEPER = ("xarch profile explain parts.may_import        one key in full: what it accepts, its rule, an example\n"
          "xarch profile explain parts.names --rule      the rules a key expands to, written as checks\n"
          "xarch profile explain checks                  how a check is written, and the words it is written in\n"
          "xarch profile explain --profile <name|path>   the folder tree and the imports of a profile")
"""How to go deeper than the overview of the format."""
NEXT = ("edit {profile}", "xarch profile explain                 # the format, key by key",
        "xarch profile check {profile}")


def _need(shown: Shown) -> str:
    return "required" if shown.required else "optional"


def _enforcement(shown_enforced: bool) -> str:
    return "enforced" if shown_enforced else "documentary"


def _row(shown: Shown) -> str:
    key = ("  " if shown.depth else "") + shown.key
    return f"{key:<{KEY}} {_need(shown):<{NEED}} {_enforcement(shown.enforced):<12} {shown.meaning}"


def overview_lines(whole: FormatExplained) -> list[str]:
    lines = [f"xarch profile format {whole.version}: one yaml file; `check` enforces what is marked enforced, "
             "the rest only fills the docs",
             "need: a key under another is needed in the map it sits in, such as parts.path in each part", "",
             f"{'key':<{KEY}} {'need':<{NEED}} {'check':<12} what it is"]
    lines += [_row(shown) for shown in whole.shape]
    lines += ["", "symbols"]
    width = max(len(symbol.symbol) for symbol in whole.symbols)
    lines += [f"  {symbol.symbol:<{width}}  {symbol.meaning}" for symbol in whole.symbols]
    lines += ["", "smallest valid profile", *(f"  {line}" for line in whole.smallest.splitlines())]
    lines += ["", "go deeper", *(f"  {line}" for line in DEEPER.splitlines())]
    return lines


def key_lines(found: KeyExplained) -> list[str]:
    lines = [found.key, f"  in: {found.where}", *_wrapped("what", found.meaning), *_wrapped("accepts", found.accepts)]
    if found.choices:
        lines += _wrapped("one of", ", ".join(found.choices))
    lines.append(f"  required: {'yes' if found.required else 'no'}")
    lines.append(f"  enforced: {_enforced(found)}")
    if found.needs:
        lines += _wrapped("needs", _needs(found))
    lines += ["  example:", *(f"    {line}" for line in found.example.splitlines())]
    if found.keys:
        lines.append("  keys:")
        lines += [f"    {_row(shown).strip()}" for shown in found.keys]
    else:
        lines.append("  keys: none")
    return lines


def _enforced(found: KeyExplained) -> str:
    if not found.enforced:
        return "no, it is documentary: it only fills the generated docs or a report"
    if not found.rules:
        return NO_RULE
    noun = "rule" if len(found.rules) == 1 else "rules"
    return f"yes, by the {noun} {', '.join(f'`{rule}`' for rule in found.rules)}"


def _needs(found: KeyExplained) -> str:
    """The facts a key's check reads, then how the default language's reader supplies them."""
    facts = ", ".join(need.fact for need in found.needs)
    if not found.language or any(not need.grade for need in found.needs):
        return f"{facts}: the facts of the source its check reads"
    short = [f"{need.fact} partly ({need.note})" if need.note else f"not {need.fact}" for need in found.needs
             if need.grade != "exact"]
    if not short:
        return f"{facts}: the facts of the source its check reads, which {found.language} supplies exactly"
    return f"{facts}: the facts of the source its check reads; {found.language} supplies {', '.join(short)}"


def _wrapped(label: str, text: str) -> list[str]:
    return fill(f"{label}: {text}", width=WIDTH, initial_indent="  ", subsequent_indent="    ").splitlines()


def unknown_message(found: UnknownKey, words: Sequence[str] = ()) -> str:
    also = f"; of the words of a check, {', '.join(words)}" if words else ""
    return f"no key `{found.key}` in the format: the nearest are {', '.join(found.nearest)}{also}"


def overview_document(whole: FormatExplained) -> str:
    return _dump({"ok": True, "format": whole.version, "shape": [_shown(shown) for shown in whole.shape],
                  "symbols": [{"symbol": s.symbol, "meaning": s.meaning} for s in whole.symbols],
                  "smallest": whole.smallest, "deeper": DEEPER})


def key_document(found: KeyExplained) -> str:
    return _dump({"ok": True, "key": found.key, "where": found.where, "meaning": found.meaning,
                  "accepts": found.accepts, "required": found.required, "enforced": found.enforced,
                  "rules": list(found.rules), "example": found.example, "choices": list(found.choices),
                  "keys": [_shown(shown) for shown in found.keys],
                  "needs": [{"fact": need.fact, "meaning": need.meaning, "grade": need.grade or None,
                             "note": need.note or None} for need in found.needs],
                  "language": found.language})


def unknown_document(found: UnknownKey, words: Sequence[str] = ()) -> str:
    return _dump({"ok": False, "error": unknown_message(found, words), "key": found.key,
                  "nearest": [*found.nearest, *words]})


def _shown(shown: Shown) -> dict[str, Any]:
    return {"key": shown.key, "depth": shown.depth, "meaning": shown.meaning, "required": shown.required,
            "enforced": shown.enforced}


def view_lines(seen: ProfileViewed) -> list[str]:
    where = "bundled" if seen.bundled else f"custom, named {seen.name}"
    return [f"{seen.location} ({where})", "folders", *(f"  {line}" for line in seen.tree.splitlines()), "imports",
            *(f"  {line}" for line in seen.imports.splitlines())]


def view_document(seen: ProfileViewed) -> str:
    return _dump({"ok": True, "profile": seen.location, "name": seen.name, "tree": seen.tree,
                  "imports": seen.imports})


def check_lines(checked: ProfileChecked) -> list[str]:
    origin = checked.origin
    if origin is not None and origin.bundled:
        where = "bundled"
    elif origin is not None and origin.closest is not None:
        where = f"custom; closest bundled: {origin.closest}"
    else:
        where = "custom"
    lines = [f"checking {checked.location} ({where})"]
    loads = [p for p in checked.problems if p.check == LOAD]
    examples = [p for p in checked.problems if p.check == EXAMPLES]
    lines += _section("loads", loads, "ok")
    if origin is None:
        lines.append("  examples: not checked: the profile does not load")
    else:
        lines.append(f"  files: all {checked.files} it points to are present")
        lines += _section("examples", examples, "ok: they import only what their part may")
        lines += _compared(checked)
    lines.append("OK: the profile is valid" if checked.ok
                 else f"INVALID: {len(checked.problems)} problem{'' if len(checked.problems) == 1 else 's'}")
    return lines


def _section(name: str, problems: Sequence[Any], ok: str) -> list[str]:
    if not problems:
        return [f"  {name}: {ok}"]
    return [f"  {name}: {len(problems)} problem{'' if len(problems) == 1 else 's'}",
            *(f"    {problem.text}" for problem in problems)]


def _compared(checked: ProfileChecked) -> list[str]:
    origin = checked.origin
    if origin is None or origin.bundled or origin.closest is None:
        return []
    if not origin.looser:
        return [f"  compared: no looser than {origin.closest}"]
    return [f"  compared: looser than {origin.closest} (information, never a failure):",
            *(f"    {item.sentence}" for item in origin.looser)]


def check_document(checked: ProfileChecked) -> str:
    origin = checked.origin
    compared = None
    if origin is not None and not origin.bundled and origin.closest is not None:
        compared = {"profile": origin.closest,
                    "looser": [{"key": i.key, "part": i.part, "what": i.what,
                                "sentence": i.sentence} for i in origin.looser]}
    return _dump({"ok": checked.ok, "profile": checked.location,
                  "problems": [{"check": p.check, "message": p.text} for p in checked.problems],
                  "files": checked.files, "compared_with": compared})


def created_lines(done: ProfileCreated, source: str) -> list[str]:
    profile = done.profile.as_posix()
    lines = [f"wrote {done.folder.as_posix()}/, a copy of {source} named {done.profile.stem}, based_on: {source}"]
    lines += [f"  {line}" for line in _summary(done.files)]
    lines += ["to put it in force, add this under [tool.xarch] in pyproject.toml (`new` never edits it):",
              f'  profile = "{done.location}"', "next:", *(f"  {step.format(profile=profile)}" for step in NEXT)]
    return lines


def _summary(files: Sequence[str]) -> list[str]:
    folders: dict[str, list[str]] = {}
    for name in files:
        head, _, rest = name.partition("/")
        folders.setdefault(head if rest else "", []).append(name)
    lines = list(folders.get("", []))
    for head, names in folders.items():
        if head:
            lines.append(f"{head}/ ({len(names)} file{'' if len(names) == 1 else 's'})")
    return lines


def _dump(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False)


COMMENTS = "YAML comments are not carried over: the converted file has none, so copy the ones you need by hand."


def migrated_lines(done: Migrated) -> list[str]:
    where = done.folder.as_posix()
    lines = [f"{'dry run, nothing written: would write' if done.dry_run else 'wrote'} to {where}/"]
    for file in done.files:
        notes = []
        if file.source is not None:
            notes.append(f"from {file.source}")
        if file.rewritten:
            notes.append(f"{file.rewritten} example placeholder{'s' if file.rewritten > 1 else ''} rewritten")
        lines.append(f"  {file.path}" + (f"  ({', '.join(notes)})" if notes else ""))
    if done.changes:
        lines += ["changed:", *(f"  {item}" for item in done.changes)]
    if done.by_hand:
        lines += ["by hand:", *(f"  {item}" for item in done.by_hand)]
    lines.append(COMMENTS)
    lines.append("the old profile and its files are untouched; check the new one with `xarch check --profile "
                 f"{done.profile.as_posix()}`")
    return lines
