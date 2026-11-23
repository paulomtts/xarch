"""How `xarch check` shows what it found: the violations as text lines, each with the fix and the profile's hint when it
has one, then the state of its enforcement; or all of it as one JSON document.

The JSON document is a contract (see the README): {"ok", "strict", "profile", "violations", "enforcement"}, each
violation {"rule", "file", "line", "message", "fix", "hint"}, a line of 0 (the whole file or folder) shown as null,
the fix what to do about it and the hint the profile's own advice for the rule (null when it has none), the
violations in the order the check gives them: of file, then line, then rule. A refusal is {"ok": false, "error"}.

The text section leaves out a line with nothing to report; the JSON object always holds every key, but `checks` (each
check the profile writes itself, {"id", "read", "said"}), which a profile that writes none does not have.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from xarch.cli.reports.document import document
from xarch.cli.reports.profile_report import compared_document, compared_words, low_reason, percent
from xarch.cli.reports.shown import shown
from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import (
    APPROXIMATE,
    DYNAMIC,
    GUARDS_OFF,
    INIT_FILES,
    SKIPPED,
    UNGOVERNED,
    UNPLACED,
    UNRESOLVED,
    VACUOUS,
    WEAK,
    AppChecked,
    At,
    EnforcementView,
    FindingView,
)
from xarch.modules.spec.contract import Origin

LABEL = 13
"""The width of a label of the enforcement section, its colon and the spaces after it."""
INDENT = "    "
"""How far the fix and the hint of a finding are indented under its line."""
SHOWN = 5
"""How many places a text line of skips or dynamic imports names before it counts the rest."""
LABELS = {GUARDS_OFF: "guards off", UNGOVERNED: "ungoverned", INIT_FILES: "init files", SKIPPED: "skipped",
          DYNAMIC: "dynamic", UNRESOLVED: "unresolved", WEAK: "weak", APPROXIMATE: "approximate",
          VACUOUS: "reads nothing", UNPLACED: "litmus"}
"""How each section of the enforcement is labelled, by its key."""


def _text_lines(found: Iterable[Violation], hints: Mapping[str, str] | None = None) -> list[str]:
    """The violations as the terminal shows them, in the order rules gives them, then the summary line. A
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


def check_lines(origin: Origin, checked: AppChecked, strict: bool, cwd: Path) -> list[str]:
    """What `xarch check` shows as text: the violations, then the enforcement section, a profile file named from the
    working folder cwd when it lies below it."""
    return [*_text_lines(checked.violations, checked.hints),
            *_enforcement_lines(origin, checked.enforcement, strict, cwd, checked.hints)]


def _enforcement_lines(origin: Origin, state: EnforcementView, strict: bool, cwd: Path,
                      hints: Mapping[str, str] | None = None) -> list[str]:
    """The enforcement section: where the profile comes from and how loose it is, then the state of the check's
    enforcement; with strict, the findings it fails on after it. A weak check that has a fix shows it under its line,
    then the profile's hint for its rule when there is one."""
    lines = ["enforcement", _line("profile", f"{shown(Path(origin.location), cwd)} ({compared_words(origin)})", 2)]
    if origin.low:
        lines.append(_line("match", f"{percent(origin.match)}, low: {low_reason(origin)}", 4))
    if origin.guards_off:
        lines.append(_line(LABELS[GUARDS_OFF], ", ".join(_guard(name) for name in origin.guards_off), 4))
    lines += [_line(item.key, item.sentence, 4) for item in origin.looser]
    if state.ungoverned:
        count = len(state.ungoverned)
        lines.append(_line(LABELS[UNGOVERNED], f"{_count(count, f'{state.language or "source"} file')} outside every part "
                                         f"({', '.join(state.ungoverned_folders)})", 2))
    lines += [_line("excluded", f"{item.folder}/ ({item.reason})", 2) for item in state.excluded]
    lines += [_line("known", f"{item.file}:{item.line}: {item.name} is public, a test names it and no other file "
                             "of the app does, which the profile accepts (guards.dead-code.known)", 2) for item in state.known]
    lines += [_line("translated", f"{item.file}:{item.line}: {item.function} names {item.built}, which its file "
                                  f"builds, and {item.other}: no-twins accepts the pair as a translation "
                                  "(guards.no-twins.translated)", 2) for item in state.translated]
    lines += [_line(LABELS[INIT_FILES], f"{'/'.join(item.path)} is {item.state}", 2) for item in state.init_files]
    if state.skipped:
        lines.append(_line(LABELS[SKIPPED], f"{_count(len(state.skipped), 'skip')} ({_places(state.skipped)})", 2))
    if state.dynamic:
        lines.append(_line(LABELS[DYNAMIC], f"{_count(len(state.dynamic), 'dynamic import')} ({_places(state.dynamic)})", 2))
    lines += [_line(LABELS[UNRESOLVED], item.sentence, 2) for item in state.unresolved]
    for weak in state.weak:
        lines.append(_line(LABELS[WEAK], f"{weak.file}{f':{weak.line}' if weak.line else ''}: {weak.message}", 2))
        if weak.fix:
            lines.append(f"{INDENT}{' ' * 2}fix: {weak.fix}")
            if weak.rule in (hints or {}):
                lines.append(f"{INDENT}{' ' * 2}hint: {(hints or {})[weak.rule]}")
    lines += [_line(LABELS[APPROXIMATE], item.sentence, 2) for item in state.approximate]
    lines += [_line("own check" if check.read else LABELS[VACUOUS], check.said, 2) for check in state.checks]
    if strict and state.strict:
        lines.append(_line("strict", f"{_count(len(state.strict), 'finding')} fail the check", 0)
                     if len(state.strict) > 1 else _line("strict", "1 finding fails the check", 0))
        lines += [f"    {LABELS[f.key]}: {_guard(f.detail) if f.key == GUARDS_OFF else f.detail}" for f in state.strict]
    return lines


SET_ON_A_PART = {"package-only": "parts.<part>.package_only"}
"""The guards a profile switches on by a key of a part, not of `guards`, each with that key."""


def _guard(name: str) -> str:
    """A guard by its name, and the key that switches it on when that is no key of `guards`."""
    return f"{name} ({SET_ON_A_PART[name]})" if name in SET_ON_A_PART else name


def _line(label: str, text: str, indent: int) -> str:
    return " " * indent + f"{label}:".ljust(max(LABEL, len(label) + 2)) + text


def _count(count: int, noun: str) -> str:
    return f"{count} {noun}{'' if count == 1 else 's'}"


def _places(places: Sequence[At]) -> str:
    shown = ", ".join(f"{at.file}:{at.line}" for at in places[:SHOWN])
    return shown + (f" and {len(places) - SHOWN} more" if len(places) > SHOWN else "")


def _violation_document(violation: Violation, hints: Mapping[str, str] | None = None) -> dict[str, Any]:
    return {"rule": violation.rule, "file": violation.file, "line": violation.line or None,
            "message": violation.message, "fix": violation.fix, "hint": (hints or {}).get(violation.rule)}


def _enforcement_document(origin: Origin, state: EnforcementView) -> dict[str, Any]:
    return {
        "profile": {"location": origin.location, "bundled": origin.bundled, "compared_with": compared_document(origin),
                    "guards_off": list(origin.guards_off), "baseline_off": list(origin.baseline_off),
                    "looser": [{"key": item.key, "part": item.part, "what": item.what, "sentence": item.sentence}
                               for item in origin.looser]},
        "ungoverned": {"count": len(state.ungoverned), "folders": list(state.ungoverned_folders),
                       "files": list(state.ungoverned)},
        "excluded": [{"folder": item.folder, "reason": item.reason} for item in state.excluded],
        "known": [{"file": item.file, "line": item.line, "name": item.name} for item in state.known],
        "translated": [{"file": item.file, "line": item.line, "function": item.function, "built": item.built,
                        "other": item.other} for item in state.translated],
        "init_files": [{"file": "/".join(item.path), "state": item.state} for item in state.init_files],
        "skipped": {"count": len(state.skipped), "at": _at(state.skipped)},
        "dynamic": {"count": len(state.dynamic), "at": _at(state.dynamic)},
        "unresolved": [{"file": item.item.file, "line": item.item.line, "written": item.item.written}
                       for item in state.unresolved],
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
    return document({"ok": checked.ok, "strict": strict, "profile": profile,
                     "violations": [_violation_document(v, checked.hints) for v in checked.violations],
                     "enforcement": _enforcement_document(origin, checked.enforcement)})
