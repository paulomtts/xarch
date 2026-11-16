"""How the `xarch profile` commands show what they found: as text lines, or (for explain and check) as one JSON
document, `{"ok": ...}` first, a refusal being `{"ok": false, "error": ...}`.

explain, no key: {"ok", "format", "shape", "symbols", "smallest", "deeper"}, each shape entry {"key", "depth",
"meaning", "required", "enforced", "read_by"}. explain, one key: {"ok", "key", "where", "meaning", "accepts", "required",
"enforced", "read_by", "rules", "example", "choices", "keys", "needs", "language"}, each need {"fact", "meaning", "grade",
"note"}: a fact of the source the key's check reads, and how the language named supplies it. explain, a key the
format has not: {"ok": false, "error", "key", "nearest", "words"}, nearest the format's keys near it and words the
words of a check near it. explain, a profile: {"ok", "profile", "name", "tree", "imports"}.
check: {"ok", "profile", "problems", "files", "checks", "compared_with"}, files the number of files the profile
points to and checks the number of checks it writes itself (made or not), both null for a profile that does not load,
each problem {"check", "message"} (check: load, examples, or checks, for a check of the
profile's own) and compared_with {"profile", "looser"} (null for a bundled profile or one that resembles none), each
looser entry {"key", "part", "what", "sentence"}.
"""
from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from textwrap import fill
from typing import Any

from xarch.cli.reports.document import document
from xarch.cli.reports.shown import shown
from xarch.modules.rules.contract import ProfileHeld, ProfileUnloaded, Resemblance
from xarch.modules.spec.contract import (
    FilesTaken,
    FormatExplained,
    KeyExplained,
    Migrated,
    Need,
    Origin,
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

LOAD, EXAMPLES, CHECKS = "load", "examples", "checks"
"""The check a problem of `profile check` is named by in the JSON document: the loader, the examples' imports, or the
checks the profile writes itself."""

ABSENT = "absent"
"""How the JSON document grades a fact the language's reader does not supply."""


def _need(shown: Shown) -> str:
    return "required" if shown.required else "optional"


def _enforcement(shown: Shown) -> str:
    return "enforced" if shown.enforced else shown.read_by or "documentary"


def _row(shown: Shown) -> str:
    key = ("  " if shown.depth else "") + shown.key
    return f"{key:<{KEY}} {_need(shown):<{NEED}} {_enforcement(shown):<12} {shown.meaning}"


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
    if not found.enforced and found.read_by:
        return f"no: check never reads it; only xarch {found.read_by} does"
    if not found.enforced:
        return "no, it is documentary: it only fills the generated docs or a report"
    if not found.rules:
        return NO_RULE
    noun = "rule" if len(found.rules) == 1 else "rules"
    return f"yes, by the {noun} {', '.join(f'`{rule}`' for rule in found.rules)}"


def _needs(found: KeyExplained) -> str:
    """The facts a key's check reads, then how the default language's reader supplies them."""
    facts = ", ".join(need.fact for need in found.needs)
    if not found.language or not found.graded:
        return f"{facts}: the facts of the source its check reads"
    short = [f"{item.fact} partly ({item.note})" if item.note is not None else f"not {item.fact}"
             for item in found.short]
    if not short:
        return f"{facts}: the facts of the source its check reads, which {found.language} supplies exactly"
    return f"{facts}: the facts of the source its check reads; {found.language} supplies {', '.join(short)}"


def _wrapped(label: str, text: str) -> list[str]:
    return fill(f"{label}: {text}", width=WIDTH, initial_indent="  ", subsequent_indent="    ").splitlines()


def unknown_message(found: UnknownKey, words: Sequence[str] = ()) -> str:
    also = f"; of the words of a check, {', '.join(words)}" if words else ""
    return f"no key `{found.key}` in the format: the nearest are {', '.join(found.nearest)}{also}"


def overview_document(whole: FormatExplained) -> str:
    return document({"ok": True, "format": whole.version, "shape": [_shown(shown) for shown in whole.shape],
                  "symbols": [{"symbol": s.symbol, "meaning": s.meaning} for s in whole.symbols],
                  "smallest": whole.smallest, "deeper": DEEPER})


def key_document(found: KeyExplained) -> str:
    return document({"ok": True, "key": found.key, "where": found.where, "meaning": found.meaning,
                  "accepts": found.accepts, "required": found.required, "enforced": found.enforced,
                  "read_by": found.read_by or None, "rules": list(found.rules), "example": found.example, "choices": list(found.choices),
                  "keys": [_shown(shown) for shown in found.keys],
                  "needs": [{"fact": need.fact, "meaning": need.meaning, "grade": _grade(need, found.graded),
                             "note": need.supply.note or None if need.supply is not None else None}
                            for need in found.needs],
                  "language": found.language})


def _grade(need: Need, graded: bool) -> str | None:
    """How a fact is supplied, as the JSON names it: its grade, absent when it is not supplied, null when ungraded."""
    if need.supply is not None:
        return need.supply.grade
    return ABSENT if graded else None


def unknown_document(found: UnknownKey, words: Sequence[str] = ()) -> str:
    return document({"ok": False, "error": unknown_message(found, words), "key": found.key,
                  "nearest": list(found.nearest), "words": list(words)})


def _shown(shown: Shown) -> dict[str, Any]:
    return {"key": shown.key, "depth": shown.depth, "meaning": shown.meaning, "required": shown.required,
            "enforced": shown.enforced, "read_by": shown.read_by or None}


def view_lines(seen: ProfileViewed) -> list[str]:
    where = "bundled" if seen.bundled else f"custom, named {seen.name}"
    return [f"{seen.location} ({where})", "folders", *(f"  {line}" for line in seen.tree.splitlines()), "imports",
            *(f"  {line}" for line in seen.imports.splitlines())]


def view_document(seen: ProfileViewed) -> str:
    return document({"ok": True, "profile": seen.location, "name": seen.name, "tree": seen.tree,
                  "imports": seen.imports})


def origin_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words: bundled, or custom and the bundled profile closest to it, if any."""
    if origin.bundled:
        return "bundled"
    if origin.closest is not None:
        return f"custom; closest bundled: {origin.closest}"
    return "custom; no bundled profile resembles it"


def check_lines(checked: ProfileHeld | ProfileUnloaded) -> list[str]:
    """What `profile check` found, as text: a section per check, then how the profile differs from the bundled one it
    is based on, and the verdict."""
    match checked:
        case ProfileUnloaded(location, problems):
            return [f"checking {location} (custom)", *_section("loads", problems, "ok"),
                    "  examples: not checked: the profile does not load", _verdict(len(problems))]
        case ProfileHeld(reviewed, own):
            pass
    lines = [f"checking {reviewed.location} ({origin_words(reviewed.resemblance)})", *_section("loads", (), "ok"),
             f"  files: {_files(reviewed.files)}",
             *_section("examples", reviewed.examples, "ok: they import only what their part may")]
    if own.checks or own.problems:
        lines += _section("checks", own.problems, "ok: its check finds what its examples say" if own.checks == 1 else
                          f"ok: its {own.checks} checks find what their examples say")
    return [*lines, *_compared(reviewed.resemblance), _verdict(len(reviewed.examples) + len(own.problems))]


def _files(count: int) -> str:
    """Whether the files the profile points to are present, as many as they are."""
    match count:
        case 0:
            return "it points to none"
        case 1:
            return "the one it points to is present"
    return f"all {count} it points to are present"


def _section(name: str, problems: Sequence[str], ok: str) -> list[str]:
    if not problems:
        return [f"  {name}: {ok}"]
    return [f"  {name}: {len(problems)} problem{'' if len(problems) == 1 else 's'}",
            *(f"    {problem}" for problem in problems)]


def _verdict(problems: int) -> str:
    return "OK: the profile is valid" if not problems else f"INVALID: {problems} problem{'' if problems == 1 else 's'}"


def _compared(resemblance: Resemblance) -> list[str]:
    if resemblance.bundled or resemblance.closest is None:
        return []
    if not resemblance.looser:
        return [f"  compared: no looser than {resemblance.closest}"]
    return [f"  compared: looser than {resemblance.closest} (information; a part left without the litmus it gives "
            "fails `check --strict`):",
            *(f"    {item.sentence}" for item in resemblance.looser)]


def check_document(checked: ProfileHeld | ProfileUnloaded) -> str:
    """What `profile check` found, as the JSON document."""
    match checked:
        case ProfileUnloaded(location, problems):
            return _check_document(False, location, [(LOAD, text) for text in problems], None, None, None)
        case ProfileHeld(reviewed, own):
            pass
    resemblance = reviewed.resemblance
    compared = None
    if not resemblance.bundled and resemblance.closest is not None:
        compared = {"profile": resemblance.closest,
                    "looser": [{"key": i.key, "part": i.part, "what": i.what,
                                "sentence": i.sentence} for i in resemblance.looser]}
    problems = [*((EXAMPLES, text) for text in reviewed.examples), *((CHECKS, text) for text in own.problems)]
    return _check_document(checked.ok, reviewed.location, problems, reviewed.files, own.checks, compared)


def _check_document(ok: bool, location: str, problems: Sequence[tuple[str, str]], files: int | None,
                    checks: int | None, compared: dict[str, Any] | None) -> str:
    return document({"ok": ok, "profile": location,
                     "problems": [{"check": check, "message": text} for check, text in problems],
                     "files": files, "checks": checks, "compared_with": compared})


TAKEN = 3
"""How many files that exist a refusal to write over them names before it counts the rest."""


def _taken_phrase(taken: Sequence[Path]) -> str:
    """The files, at least one, as a phrase ending in the verb ("a, b and 2 more already exist")."""
    names = [path.as_posix() for path in taken]
    verb = "exists" if len(names) == 1 else "exist"
    shown = ", ".join(names[:TAKEN]) + (f" and {len(names) - TAKEN} more" if len(names) > TAKEN else "")
    return f"{shown} already {verb}"


def migrate_taken(refused: FilesTaken) -> str:
    """Why migrate wrote nothing: the files it would write over, and how to write elsewhere."""
    return f"{_taken_phrase(refused.taken)}: migrate writes only new files; pass `--out <folder>` to write somewhere else"


def new_taken(refused: FilesTaken) -> str:
    """Why new wrote nothing: the files it would write over, and how to write elsewhere."""
    return (f"{_taken_phrase(refused.taken)}: nothing was written; `new` writes only new files, so pass `--out <folder>` "
            "to write somewhere else, or choose another name")


def created_lines(done: ProfileCreated, source: str, cwd: Path) -> list[str]:
    """What `profile new` wrote, and how to put the copy in force, each path shown from the working folder cwd when it
    lies below it."""
    profile = shown(done.profile, cwd)
    lines = [f"wrote {shown(done.folder, cwd)}/, a copy of {source} named {done.profile.stem}, based_on: {source}"]
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




COMMENTS = "YAML comments are not carried over: the converted file has none, so copy the ones you need by hand."


def migrated_lines(done: Migrated) -> list[str]:
    where = done.folder.as_posix()
    lines = [f"{'dry run, nothing written: would write' if done.dry_run else 'wrote'} to {where}/",
             f"  {done.profile.relative_to(done.folder).as_posix()}"]
    for file in done.files:
        notes = [f"from {file.source}"]
        if file.placeholders:
            notes.append(f"{file.placeholders} example placeholder{'s' if file.placeholders > 1 else ''} rewritten")
        lines.append(f"  {file.destination}  ({', '.join(notes)})")
    if done.changes:
        lines += ["changed:", *(f"  {item}" for item in done.changes)]
    if done.by_hand:
        lines += ["by hand:", *(f"  {item}" for item in done.by_hand)]
    lines.append(COMMENTS)
    lines.append("the old profile and its files are untouched; check the new one with `xarch check --profile "
                 f"{done.profile.as_posix()}`")
    return lines
