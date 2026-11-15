"""How `xarch check` shows what it found: the violations as text lines, each with the fix and the profile's hint when it
has one, then the state of its enforcement; or all of it as one JSON document.

The JSON document is a contract (see the README): {"ok", "strict", "profile", "violations", "enforcement"}, each
violation {"rule", "file", "line", "message", "fix", "hint"}, a line of 0 (the whole file or folder) shown as null,
the fix what to do about it and the hint the profile's own advice for the rule (null when it has none), the
violations in order of file, then line, then rule. A refusal is {"ok": false, "error"}.

The text section leaves out a line with nothing to report; the JSON object always holds every key.
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import At, Enforcement, Finding

LABEL = 13
"""The width of a label of the enforcement section, its colon and the spaces after it."""
INDENT = "    "
"""How far the fix and the hint of a finding are indented under its line."""
SHOWN = 5
"""How many places a text line of skips or dynamic imports names before it counts the rest."""
_KEYS = {"guards_off": "guards off", "ungoverned": "ungoverned", "init_files": "init files",
         "skipped": "skipped", "dynamic": "dynamic", "weak": "weak"}


def text_lines(found: Iterable[Violation], hints: Mapping[str, str] | None = None) -> list[str]:
    """The violations as the terminal shows them, in the order the checks found them, then the summary line. A
    finding is its line, `<file>:<line>: <message>`, then an indented `fix:` line and, when the profile has a hint
    for its rule, an indented `hint:` line."""
    found = list(found)
    hints = hints or {}
    if not found:
        return ["OK: no violations"]
    files = len({v.file for v in found})
    lines: list[str] = []
    for v in found:
        lines += [str(v), f"{INDENT}fix: {v.fix}"]
        if v.rule in hints:
            lines.append(f"{INDENT}hint: {hints[v.rule]}")
    return [*lines, f"{len(found)} violation(s) in {files} file(s)"]


def enforcement_lines(state: Enforcement, strict: bool) -> list[str]:
    """The enforcement section; with strict, the findings it fails on after it."""
    origin = state.origin
    if origin.bundled:
        where = "bundled"
    elif origin.closest is not None:
        where = f"custom; closest bundled: {origin.closest}"
    else:
        where = "custom; no bundled profile resembles it"
    lines = ["enforcement", _line("profile", f"{origin.location} ({where})", 2)]
    if origin.guards_off:
        lines.append(_line("guards off", ", ".join(origin.guards_off), 4))
    lines += [_line(item.key.replace("_", " "), item.sentence, 4) for item in origin.looser]
    if state.ungoverned:
        count = len(state.ungoverned)
        lines.append(_line("ungoverned", f"{_count(count, 'Python file')} outside every part "
                                         f"({', '.join(folders(state.ungoverned))})", 2))
    lines += [_line("excluded", f"{item.folder}/ ({item.reason})", 2) for item in state.excluded]
    lines += [_line("init files", f"{item.file} is {item.state}", 2) for item in state.init_files]
    if state.skipped:
        lines.append(_line("skipped", f"{_count(len(state.skipped), 'skip')} ({_places(state.skipped)})", 2))
    if state.dynamic:
        lines.append(_line("dynamic", f"{_count(len(state.dynamic), 'dynamic import')} ({_places(state.dynamic)})", 2))
    lines += [_line("weak", f"{weak.file}:{weak.line}: {weak.message}", 2) for weak in state.weak]
    if strict and state.strict:
        lines.append(_line("strict", f"{_count(len(state.strict), 'finding')} fail the check", 0)
                     if len(state.strict) > 1 else _line("strict", "1 finding fails the check", 0))
        lines += [f"    {_KEYS.get(f.key, f.key)}: {f.detail}" for f in state.strict]
    return lines


def folders(files: Sequence[str]) -> list[str]:
    """The top folders below the app holding the files, each once, in order; a file at the app's root as itself."""
    tops = ["/".join(parts[:2]) + "/" if len(parts) > 2 else file
            for file in files for parts in [file.split("/")]]
    return list(dict.fromkeys(tops))


def _line(label: str, text: str, indent: int) -> str:
    return " " * indent + f"{label}:".ljust(max(LABEL, len(label) + 2)) + text


def _count(count: int, noun: str) -> str:
    return f"{count} {noun}{'' if count == 1 else 's'}"


def _places(places: Sequence[At]) -> str:
    shown = ", ".join(f"{at.file}:{at.line}" for at in places[:SHOWN])
    return shown + (f" and {len(places) - SHOWN} more" if len(places) > SHOWN else "")


def ordered(found: Iterable[Violation]) -> list[Violation]:
    """By file, then line (a whole file first), then rule; stable for the rest."""
    return sorted(found, key=lambda v: (v.file, v.line, v.rule))


def violation_document(violation: Violation, hints: Mapping[str, str] | None = None) -> dict[str, Any]:
    return {"rule": violation.rule, "file": violation.file, "line": violation.line or None,
            "message": violation.message, "fix": violation.fix, "hint": (hints or {}).get(violation.rule)}


def enforcement_document(state: Enforcement) -> dict[str, Any]:
    origin = state.origin
    return {
        "profile": {"location": origin.location, "bundled": origin.bundled, "closest": origin.closest,
                    "guards_off": list(origin.guards_off), "baseline_off": list(origin.baseline_off),
                    "looser": [{"key": item.key, "part": item.part, "what": item.what, "sentence": item.sentence}
                               for item in origin.looser]},
        "ungoverned": {"count": len(state.ungoverned), "folders": folders(state.ungoverned),
                       "files": list(state.ungoverned)},
        "excluded": [{"folder": item.folder, "reason": item.reason} for item in state.excluded],
        "init_files": [{"file": item.file, "state": item.state} for item in state.init_files],
        "skipped": {"count": len(state.skipped), "at": _at(state.skipped)},
        "dynamic": {"count": len(state.dynamic), "at": _at(state.dynamic)},
        "weak": [{"rule": weak.rule, "file": weak.file, "line": weak.line, "message": weak.message}
                 for weak in state.weak],
        "strict_failures": [_finding(f) for f in state.strict],
    }


def _at(places: Sequence[At]) -> list[dict[str, Any]]:
    return [{"file": at.file, "line": at.line} for at in places]


def _finding(finding: Finding) -> dict[str, str]:
    return {"key": finding.key, "detail": finding.detail}


def json_document(profile: str, found: Iterable[Violation], state: Enforcement, strict: bool,
                  hints: Mapping[str, str] | None = None) -> str:
    found = list(found)
    document = {"ok": passed(found, state, strict), "strict": strict, "profile": profile,
                "violations": [violation_document(v, hints) for v in ordered(found)],
                "enforcement": enforcement_document(state)}
    return json.dumps(document, indent=2, ensure_ascii=False)


def passed(found: Sequence[Violation], state: Enforcement, strict: bool) -> bool:
    """No violation, and under strict no enforcement finding."""
    return not found and not (strict and state.strict)


def json_error(reason: str) -> str:
    return json.dumps({"ok": False, "error": reason}, indent=2, ensure_ascii=False)
