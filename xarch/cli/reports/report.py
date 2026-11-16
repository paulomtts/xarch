"""How `xarch check` shows what it found: the violations as text lines, each with the fix and the profile's hint when it
has one, then the state of its enforcement; or all of it as one JSON document.

The JSON document is a contract (see the README): {"ok", "strict", "profile", "violations", "enforcement"}, each
violation {"rule", "file", "line", "message", "fix", "hint"}, a line of 0 (the whole file or folder) shown as null,
the fix what to do about it and the hint the profile's own advice for the rule (null when it has none), the
violations in order of file, then line, then rule. A refusal is {"ok": false, "error"}.

The text section leaves out a line with nothing to report; the JSON object always holds every key, but `checks` (each
check the profile writes itself, {"id", "read", "said"}), which a profile that writes none does not have.
"""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import AppChecked, At, EnforcementView, FindingView
from xarch.modules.spec.contract import Origin

LABEL = 13
"""The width of a label of the enforcement section, its colon and the spaces after it."""
INDENT = "    "
"""How far the fix and the hint of a finding are indented under its line."""
SHOWN = 5
"""How many places a text line of skips or dynamic imports names before it counts the rest."""
_KEYS = {"guards_off": "guards off", "ungoverned": "ungoverned", "init_files": "init files",
         "skipped": "skipped", "dynamic": "dynamic", "weak": "weak", "approximate": "approximate",
         "vacuous": "reads nothing"}


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


def enforcement_lines(origin: Origin, state: EnforcementView, strict: bool,
                      hints: Mapping[str, str] | None = None) -> list[str]:
    """The enforcement section: where the profile comes from and how loose it is, then the state of the check's
    enforcement; with strict, the findings it fails on after it. A weak check that has a fix shows it under its line,
    then the profile's hint for its rule when there is one."""
    if origin.bundled:
        where = "bundled"
    elif origin.closest is not None:
        where = f"custom; closest bundled: {origin.closest}"
    else:
        where = "custom; no bundled profile resembles it"
    lines = ["enforcement", _line("profile", f"{origin.location} ({where})", 2)]
    if origin.guards_off:
        lines.append(_line("guards off", ", ".join(origin.guards_off), 4))
    lines += [_line(item.key, item.sentence, 4) for item in origin.looser]
    if state.ungoverned:
        count = len(state.ungoverned)
        lines.append(_line("ungoverned", f"{_count(count, f'{state.language or "source"} file')} outside every part "
                                         f"({', '.join(state.ungoverned_folders)})", 2))
    lines += [_line("excluded", f"{item.folder}/ ({item.reason})", 2) for item in state.excluded]
    lines += [_line("init files", f"{item.file} is {item.state}", 2) for item in state.init_files]
    if state.skipped:
        lines.append(_line("skipped", f"{_count(len(state.skipped), 'skip')} ({_places(state.skipped)})", 2))
    if state.dynamic:
        lines.append(_line("dynamic", f"{_count(len(state.dynamic), 'dynamic import')} ({_places(state.dynamic)})", 2))
    for weak in state.weak:
        lines.append(_line("weak", f"{weak.file}{f':{weak.line}' if weak.line else ''}: {weak.message}", 2))
        if weak.fix:
            lines.append(f"{INDENT}{' ' * 2}fix: {weak.fix}")
            if weak.rule in (hints or {}):
                lines.append(f"{INDENT}{' ' * 2}hint: {(hints or {})[weak.rule]}")
    lines += [_line("approximate", item.sentence, 2) for item in state.approximate]
    lines += [_line("own check" if check.read else "reads nothing", check.said, 2) for check in state.checks]
    if strict and state.strict:
        lines.append(_line("strict", f"{_count(len(state.strict), 'finding')} fail the check", 0)
                     if len(state.strict) > 1 else _line("strict", "1 finding fails the check", 0))
        lines += [f"    {_KEYS.get(f.key, f.key)}: {f.detail}" for f in state.strict]
    return lines


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


def enforcement_document(origin: Origin, state: EnforcementView) -> dict[str, Any]:
    return {
        "profile": {"location": origin.location, "bundled": origin.bundled, "closest": origin.closest,
                    "guards_off": list(origin.guards_off), "baseline_off": list(origin.baseline_off),
                    "looser": [{"key": item.key, "part": item.part, "what": item.what, "sentence": item.sentence}
                               for item in origin.looser]},
        "ungoverned": {"count": len(state.ungoverned), "folders": list(state.ungoverned_folders),
                       "files": list(state.ungoverned)},
        "excluded": [{"folder": item.folder, "reason": item.reason} for item in state.excluded],
        "init_files": [{"file": item.file, "state": item.state} for item in state.init_files],
        "skipped": {"count": len(state.skipped), "at": _at(state.skipped)},
        "dynamic": {"count": len(state.dynamic), "at": _at(state.dynamic)},
        "weak": [{"rule": weak.rule, "file": weak.file, "line": weak.line, "message": weak.message,
                  "fix": weak.fix or None} for weak in state.weak],
        "approximate": [{"key": item.key, "fact": item.fact, "note": item.note} for item in state.approximate],
        "strict_failures": [_finding(f) for f in state.strict],
        **({"checks": [{"id": check.id, "read": check.read, "said": check.said} for check in state.checks]}
           if state.checks else {}),
    }


def _at(places: Sequence[At]) -> list[dict[str, Any]]:
    return [{"file": at.file, "line": at.line} for at in places]


def _finding(finding: FindingView) -> dict[str, str]:
    return {"key": finding.key, "detail": finding.detail}


def json_document(profile: str, origin: Origin, checked: AppChecked, strict: bool) -> str:
    document = {"ok": checked.ok, "strict": strict, "profile": profile,
                "violations": [violation_document(v, checked.hints) for v in ordered(checked.violations)],
                "enforcement": enforcement_document(origin, checked.enforcement)}
    return json.dumps(document, indent=2, ensure_ascii=False)
