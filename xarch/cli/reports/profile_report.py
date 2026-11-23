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
profile's own) and compared_with {"profile", "chosen_by", "match", "low", "counts", "only_here", "only_there",
"elsewhere", "higher", "looser"} (null when nothing is compared: a bundled profile without --against, or one that
resembles none), chosen_by "based_on", "closest" or "against", counts {"parts",
"part_keys", "tiers", "guards", "profile"} each [comparable, all], higher null or {"profile", "match"}, each looser
entry {"key", "part", "what", "sentence"}; `check`'s JSON holds the same compared_with under enforcement.profile.
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
    AGAINST,
    CLOSEST,
    FilesTaken,
    FormatExplained,
    KeyExplained,
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
DEEPER = ("xarch profile explain parts.imports.may       one key in full: what it accepts, its rule, an example\n"
          "xarch profile explain parts.holds --rule      the rules a key expands to, written as checks\n"
          "xarch profile explain checks                  how a check is written, and the words it is written in\n"
          "xarch profile explain --profile <name|path>   the folder tree and the imports of a profile")
"""How to go deeper than the overview of the format."""
NEXT = ("edit {profile}", "xarch profile explain                 # the format, key by key",
        "xarch profile check {profile}")

LOAD, EXAMPLES, CHECKS, EVALS = "load", "examples", "checks", "evals"
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
    lines = ["xarch profile format: one yaml file; `check` enforces what is marked enforced, "
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
        lines += [f"  {item.note}" for item in found.short if item.unread]
    lines += ["  example:", *(f"    {line}" for line in found.example.splitlines())]
    if found.keys:
        lines.append("  keys:")
        lines += [f"    {_row(shown).strip()}" for shown in found.keys]
    else:
        lines.append("  keys: none")
    return lines


def _enforced(found: KeyExplained) -> str:
    if not found.enforced and found.read_by:
        return (f"no: check never acts on it (written wrong, the profile is invalid for every command); only xarch "
                f"{found.read_by} reads what it says")
    if not found.enforced:
        return "no, it is documentary: it only fills the generated docs or a report"
    if not found.rules:
        return NO_RULE
    noun = "rule" if len(found.rules) == 1 else "rules"
    return f"yes, by the {noun} {', '.join(f'`{rule}`' for rule in found.rules)}"


def _needs(found: KeyExplained) -> str:
    """The facts a key's check reads, then how the default language's reader supplies them; one its check reads only
    when supplied, which is not, is said as not supplied, and what the check then reads less on a line of its own."""
    facts = ", ".join(need.fact for need in found.needs)
    if not found.language or not found.graded:
        return f"{facts}: the facts of the source its check reads"
    short = [f"{item.fact} partly ({item.note})" if item.note is not None and not item.unread else f"not {item.fact}"
             for item in found.short]
    if not short:
        return f"{facts}: the facts of the source its check reads, which {found.language} supplies exactly"
    return f"{facts}: the facts of the source its check reads; {found.language} supplies {', '.join(short)}"


def _wrapped(label: str, text: str) -> list[str]:
    return fill(f"{label}: {text}", width=WIDTH, initial_indent="  ", subsequent_indent="    ").splitlines()


def unknown_message(found: UnknownKey, words: Sequence[str] = ()) -> str:
    also = f"; of the words of a check, {', '.join(words)}" if words else ""
    retired = f"{found.retired}; " if found.retired else ""
    return f"no key `{found.key}` in the format: {retired}the nearest are {', '.join(found.nearest)}{also}"


def overview_document(whole: FormatExplained) -> str:
    return document({"ok": True, "shape": [_shown(shown) for shown in whole.shape],
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
                  "nearest": list(found.nearest), "words": list(words), "retired": found.retired or None})


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


NAMED = 5
"""How many names a line of the match names in a group before it counts the rest."""
COUNTED = {"parts": "parts", "part_keys": "part keys", "tiers": "tier entries", "guards": "guards",
           "profile": "profile keys"}
"""How the match line says each kind of thing it counts, by the kind."""
GIVEN = "--against"
"""How the text says why a profile is compared with the one --against names."""


def _origin_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as `profile check` heads it: bundled, or custom and the profile it is
    compared with and why (with the match, when it is the closest), if any; with --against, either and the profile it
    names, then what the profile's own based_on names."""
    if origin.chosen_by == AGAINST:
        based_on = f"; based_on: {origin.based_on}" if origin.based_on else ""
        return f"{_kind(origin)}; against {origin.compared}, given with {GIVEN}{based_on}"
    if origin.bundled:
        return "bundled"
    if origin.compared is None:
        return "custom; no bundled profile resembles it"
    if origin.chosen_by == CLOSEST:
        return f"custom; closest bundled: {origin.compared}, match {percent(origin.match)}"
    return f"custom; {origin.chosen_by}: {origin.compared}"


def compared_words(origin: Origin | Resemblance) -> str:
    """Where a profile comes from, in words, as the enforcement section of `check` says it: bundled, or custom and the
    profile it is compared with, why, and the match, if any; a bundled one compared with the one --against names says
    that too."""
    if origin.compared is None:
        return _origin_words(origin)
    return f"{_kind(origin)}; compared with {origin.compared}, {_why(origin)}; match {percent(origin.match)}"


def _kind(origin: Origin | Resemblance) -> str:
    return "bundled" if origin.bundled else "custom"


def _why(origin: Origin | Resemblance) -> str:
    """Why the profile is compared with the one it is, as the text says it: --against for the one it names, else the
    word of the JSON."""
    return GIVEN if origin.chosen_by == AGAINST else str(origin.chosen_by)


def percent(match: float | None) -> str:
    """A match as a whole percentage, e.g. 80%."""
    return f"{round((match or 0) * 100)}%"


def low_reason(origin: Origin | Resemblance) -> str:
    """Why a low match says little of how `check` would do under the profile compared with."""
    why = ("no part in common" if not next((comparable for kind, comparable, _ in origin.counts if kind == "parts"), 0)
           else f"{100 - round((origin.match or 0) * 100)}% of what check reads under either profile has nothing to "
                "compare with in the other")
    return f"{why}, so the list below says little about how check would do under {origin.compared}"


def _match_lines(resemblance: Resemblance) -> list[str]:
    """The match with the profile compared with, its counts, what pairs with nothing, the parts at another path, and
    whether it is low or another bundled profile matches higher; nothing when nothing is compared."""
    if resemblance.compared is None:
        return []
    counts = ", ".join(f"{comparable} of {every} {COUNTED[kind]}" for kind, comparable, every in resemblance.counts)
    lines = [f"  match: {percent(resemblance.match)} with {resemblance.compared} ({_why(resemblance)}): {counts} "
             "sit where both profiles have them"]
    sides = [f"{label}: {_unpaired(names)}" for label, names in (("only here", resemblance.only_here),
                                                                  (f"only in {resemblance.compared}", resemblance.only_there))
             if names]
    if sides:
        lines.append(f"    {'. '.join(sides)}")
    if resemblance.elsewhere:
        lines.append(f"    same name, other path: {_named(resemblance.elsewhere)}")
    if resemblance.low:
        lines.append(f"    low: {low_reason(resemblance)}")
    if resemblance.higher is not None:
        lines.append(f"    {resemblance.higher[0]} matches {percent(resemblance.higher[1])}")
    return lines


def _unpaired(names: Sequence[str]) -> str:
    """The parts, then the tiers, of one side, each group by its noun, e.g. "parts a, b; tier t"."""
    groups = []
    for noun in ("part", "tier"):
        found = [name for kind, _, name in (entry.partition(" ") for entry in names) if kind == noun]
        if found:
            groups.append(f"{noun}{'s' if len(found) > 1 else ''} {_named(found)}")
    return "; ".join(groups)


def _named(names: Sequence[str]) -> str:
    """Up to NAMED names, then how many more there are."""
    return ", ".join(names[:NAMED]) + (f" and {len(names) - NAMED} more" if len(names) > NAMED else "")


def compared_document(origin: Origin | Resemblance) -> dict[str, Any] | None:
    """The profile compared with, as both JSON documents hold it under compared_with; None when nothing is compared."""
    if origin.compared is None:
        return None
    return {"profile": origin.compared, "chosen_by": origin.chosen_by, "match": origin.match, "low": origin.low,
            "counts": {kind: [comparable, every] for kind, comparable, every in origin.counts},
            "only_here": list(origin.only_here), "only_there": list(origin.only_there),
            "elsewhere": list(origin.elsewhere),
            "higher": None if origin.higher is None else {"profile": origin.higher[0], "match": origin.higher[1]},
            "looser": [{"key": item.key, "part": item.part, "what": item.what, "sentence": item.sentence}
                       for item in origin.looser]}


def check_lines(checked: ProfileHeld | ProfileUnloaded) -> list[str]:
    """What `profile check` found, as text: a section per check, then the match with the profile it is compared with
    and how it differs from it, and the verdict."""
    match checked:
        case ProfileUnloaded(location, problems):
            return [f"checking {location} (custom)", *_section("loads", problems, "ok"),
                    "  examples: not checked: the profile does not load", _verdict(len(problems))]
        case ProfileHeld(reviewed, own):
            pass
    lines = [f"checking {reviewed.location} ({_origin_words(reviewed.resemblance)})", *_section("loads", (), "ok"),
             f"  files: {_files(reviewed.files)}",
             *_section("examples", reviewed.examples, "ok: they import only what their part may")]
    if own.checks or own.problems:
        lines += _section("checks", own.problems, "ok: its check finds what its examples say" if own.checks == 1 else
                          f"ok: its {own.checks} checks find what their examples say")
    if own.asked or own.evals:
        lines += _section("evals", own.evals, "ok: each reads something in each of its examples")
    return [*lines, *_match_lines(reviewed.resemblance), *_compared(reviewed.resemblance),
            _verdict(len(reviewed.examples) + len(own.problems) + len(own.evals))]


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
    if resemblance.compared is None:
        return []
    if not resemblance.looser:
        return [f"  compared: no looser than {resemblance.compared}"]
    return [f"  compared: looser than {resemblance.compared} (information; a part left without the litmus it gives "
            "fails `check --strict`):",
            *(f"    {item.sentence}" for item in resemblance.looser)]


def check_document(checked: ProfileHeld | ProfileUnloaded) -> str:
    """What `profile check` found, as the JSON document."""
    match checked:
        case ProfileUnloaded(location, problems):
            return _check_document(False, location, [(LOAD, text) for text in problems], None, None, None)
        case ProfileHeld(reviewed, own):
            pass
    problems = [*((EXAMPLES, text) for text in reviewed.examples), *((CHECKS, text) for text in own.problems),
                *((EVALS, text) for text in own.evals)]
    return _check_document(checked.ok, reviewed.location, problems, reviewed.files, own.checks,
                           compared_document(reviewed.resemblance))


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
