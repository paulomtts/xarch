"""How a profile writes a target, a place a part may import or a check names; checked against the parts declared, each
by its path, the part that writes it and the profile's repeating folders, each problem said at its address. Spec reads
a part's `imports` and a tier's with it, and rules the places a check of the profile's own names.

A value whose head (the text before its first `/` or `:`) holds a dot is a reference: `parts.<part>`, the part in every
instance of its repeating folder or, outside one, the part itself; or `<word>.<part>`, the part in the importer's own
instance of the folder the word repeats, a word of the profile's repeating folders; each optionally followed by
`/<path>` and, where the key takes one, `:<pattern>`. The old forms, `<part>@any`, `<part>@own` and the bare name of a
part, were removed in 0.3.0: each is refused with the reference to write, computed from the profile. A target is
written back as a reference (see written_target), which reads back as itself."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from typing import Any

from xarch.kernel.logic.placement import repeat_of
from xarch.kernel.placement import EACH
from xarch.profile_values.placement import Repeat, Target

NAME_PATTERN = re.compile(r"[^\s@/:]+")
"""A name pattern: any text but whitespace and the separators of a target, written as name_matches reads it."""
_HEAD = re.compile(r"[^/:]*")
_REFERENCE = re.compile(r"(?P<part>[^/:]*)(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?", re.DOTALL)
_NOT_A_REFERENCE = ("is not a reference: write parts.<part> or <word>.<part>, optionally followed by /<path> and "
                    ":<pattern>")
BARE = "a bare part name"
"""How a removal names the old form that writes a part by its name alone."""


def target(value: Any, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
           declared: Collection[str], where: str, problems: list[str], patterns: bool = False,
           mirrored: Collection[tuple[str, ...]] | None = None, *, alone: str, repeats: Collection[Repeat],
           place: bool = False) -> Target | None:
    """The target a profile writes as value, for the part owner (its name and path; None for what names no part, which
    the caller words as alone, such as "a tier's folder"), each part by its path, repeats the profile's repeating
    folders, whose words a reference names; None, with the problem said at where, when it is not one. A target that
    names a part declared but not placed is None, with no problem of its own. mirrored, None but for a test, holds the
    paths of the parts the test's tier tests, () for none: `<word>.<part>` there is the instance a test mirrors,
    refused when none of those parts lies in a `<word>` folder. place says the value is a check's `place`, where a
    prefix that is no word may be a dotted name of code. A value in an old form (see old_form) is None, refused with
    the reference to write: `parts.<part>` for `@any`; for `@own` and a bare name, `<word>.<part>` where that
    reference is accepted, else `parts.<part>`; or, when the reference would be the part itself, as implied."""
    if isinstance(value, str) and "." in _HEAD.match(value)[0]:
        return _reference(value, owner, parts, declared, where, problems, patterns, mirrored, alone, repeats, place)
    old = old_form(value)
    if old is None:
        problems.append(f"{where}: {value!r} {_NOT_A_REFERENCE}")
        return None
    name, scope, tail = old
    path = parts.get(name)
    if path is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    held = repeat_of(repeats, path)
    own = (scope != "any" and held is not None
           and _word_problem(value, held.word, name, (name, path), owner, repeats, mirrored, alone) is None)
    if owner is not None and name == owner[0] and (own or EACH not in path):
        problems.append(_implied(where, value, owner, f"parts.{name}"))
        return None
    everywhere = f"parts.{name}{tail}"
    if held is None or not own:
        instead = everywhere
    elif scope == "own":
        instead = f"{held.word}.{name}{tail}"
    else:
        instead = f"{held.word}.{name}{tail} (this {held.word}'s) or {everywhere} (any {held.word}'s)"
    problems.append(f"{where}: {removed(value, BARE if scope is None else f'@{scope}', instead)}")
    return None


def old_form(value: Any) -> tuple[str, str | None, str] | None:
    """What a value whose head holds no dot writes in the old forms: the name of the part, the scope (`any`, `own`,
    None for a bare name) and the tail, `/<path>` and `:<pattern>` as written, the scope taken out wherever it stands
    before the pattern; None when it writes none of them."""
    if not isinstance(value, str):
        return None
    before, colon, pattern = value.partition(":")
    body, at, after = before.partition("@")
    scope = None
    if at:
        scope, slash, below = after.partition("/")
        body += slash + below
        if scope not in ("any", "own"):
            return None
    name = body.partition("/")[0]
    if not name or "@" in body:
        return None
    return name, scope, body[len(name):] + colon + pattern


def removed(value: Any, form: str, instead: str) -> str:
    """The one wording of a value refused for a form 0.3.0 removed: the value, the form and what to write instead."""
    return f"{value!r}: {form} was removed in 0.3.0: write {instead}"


def written_target(made: Target, words: Mapping[str, str]) -> str:
    """The target as a reference, which target() reads back to it: `parts.<part>` for the part in every instance of its
    repeating folder or in none, `<word>.<part>` for the importer's own instance, the word that of the repeating folder
    the part lies in (words, by part); then the path below the part and the name pattern. Raises ValueError for the own
    instance of a part words gives no word, which lies in no repeating folder and has no own instance."""
    if made.scope == "own" and made.part not in words:
        raise ValueError(f"Target {made.part!r} is in its importer's own instance, but part {made.part!r} lies in no "
                         "repeating folder")
    prefix = words[made.part] if made.scope == "own" else "parts"
    return f"{prefix}.{made.part}" + "".join(f"/{step}" for step in made.sub) + (f":{made.names}" if made.names else "")


def _reference(value: str, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
               declared: Collection[str], where: str, problems: list[str], patterns: bool,
               mirrored: Collection[tuple[str, ...]] | None, alone: str, repeats: Collection[Repeat],
               place: bool) -> Target | None:
    """The target a reference writes (see target); None with its one problem, that of the first of its checks that
    fails: the shape, the prefix, the pattern, the part, the path, the instance, the part itself."""
    prefix, _, rest = value.partition(".")
    match = _REFERENCE.fullmatch(rest)
    if not prefix or match is None or not match["part"] or "." in match["part"] or "@" in value.partition(":")[0]:
        problems.append(f"{where}: {value!r} {_NOT_A_REFERENCE}")
        return None
    name, names = match["part"], match["names"]
    path = parts.get(name)
    problem = _prefix_problem(value, prefix, rest, path, repeats, place) or _pattern_problem(value, names, patterns)
    if problem is not None:
        problems.append(f"{where}: {problem}")
        return None
    if path is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    steps = _steps(match["sub"])
    if steps is None:
        problems.append(f"{where}: {value!r} has an invalid path after the part")
        return None
    if prefix == "parts":
        scope = "any" if EACH in path else "none"
    else:
        problem = _word_problem(value, prefix, rest, (name, path), owner, repeats, mirrored, alone)
        if problem is not None:
            problems.append(f"{where}: {problem}")
            return None
        scope = "own"
    if owner is not None and name == owner[0] and scope != "any":
        problems.append(_implied(where, value, owner, f"parts.{name}"))
        return None
    return Target(name, scope, steps, names or "")


def _prefix_problem(value: str, prefix: str, rest: str, path: tuple[str, ...] | None, repeats: Collection[Repeat],
                    place: bool) -> str | None:
    """What is wrong with the prefix of a reference: a word in brackets, or a prefix that is neither parts nor a word of
    the profile, told the reference to write for the part (its path, None when it places none) and, for a check's
    place, that a dotted name of code goes under path; None when the prefix is one."""
    if len(prefix) > 2 and prefix.startswith("<") and prefix.endswith(">"):
        return f"{value!r}: write the word without brackets: {prefix[1:-1]}.{rest}"
    words = [repeat.word for repeat in repeats]
    if prefix == "parts" or prefix in words:
        return None
    known = f" ({', '.join(words)})" if words else ", which has none"
    held = None if path is None else repeat_of(repeats, path)
    instead = ("parts.<part> or <word>.<part>" if path is None
               else f"parts.{rest}" if held is None else f"{held.word}.{rest} or parts.{rest}")
    hint = "; a dotted name of code goes under path" if place else ""
    return (f"{value!r}: {prefix!r} is neither parts nor a word of this profile{known}: a profile names no instance; "
            f"write {instead}{hint}")


def _word_problem(value: str, prefix: str, rest: str, part: tuple[str, tuple[str, ...]],
                  owner: tuple[str, tuple[str, ...]] | None, repeats: Collection[Repeat],
                  mirrored: Collection[tuple[str, ...]] | None, alone: str) -> str | None:
    """What is wrong with `<word>.<part>`: the part (its name and path) must lie in the word's folder, and so must the
    importer, owner, or what the caller words as alone; for a test, whose tier tests the parts at the paths mirrored,
    one of those parts must instead, the instance a test mirrors; None when both do."""
    instead = f"write parts.{rest}"
    held = repeat_of(repeats, part[1])
    if held is None:
        return f"{value!r}: part {part[0]!r} lies in no <{prefix}> folder: {instead}"
    if held.word != prefix:
        return f"{value!r}: part {part[0]!r} lies in the <{held.word}> folder, not <{prefix}>: {instead}"
    if mirrored is not None:
        words = {each.word for path in mirrored if (each := repeat_of(repeats, path)) is not None}
        return None if prefix in words else (f"{value!r}: no part the tier tests lies in a <{prefix}> folder, so its "
                                             f"tests mirror no {prefix}: {instead}")
    importer = alone if owner is None else f"part {owner[0]!r}"
    mine = None if owner is None else repeat_of(repeats, owner[1])
    if mine is None:
        return f"{value!r}: {importer} lies in no <{prefix}> folder, so it has no own {prefix}: {instead}"
    return None if mine.word == prefix else f"{value!r}: {importer} lies in no <{prefix}> folder: {instead}"


def _pattern_problem(value: str, names: str | None, patterns: bool) -> str | None:
    """What is wrong with the name pattern of a target: one where the key takes none (patterns false), an empty one, or
    one that is not one; None when it writes none or writes one."""
    if names is None:
        return None
    if not patterns:
        return f"{value!r} has a name pattern, which this key does not take: drop ':{names}'"
    if not names:
        return f"{value!r} has an empty name pattern after `:`"
    if not NAME_PATTERN.fullmatch(names):
        return (f"{value!r} has a name pattern that is not one: write it with no space, `@`, `/` or `:`, `*` standing "
                "for any text")
    return None


def _steps(sub: str | None) -> tuple[str, ...] | None:
    """The path below the part a target writes, step by step, () when it writes none; None when a step is empty, `.`,
    `..` or holds the repeating step."""
    steps = tuple(sub.split("/")) if sub is not None else ()
    return None if any(not step or step in (".", "..") or EACH in step for step in steps) else steps


def _implied(where: str, value: str, part: tuple[str, tuple[str, ...]], again: str) -> str:
    """A part may always import itself, so a target that only says so is refused: the part by its name and path, and
    again, how the target that names it in every instance is written."""
    if EACH not in part[1]:
        return f"{where}: {value!r} is implied: a part may always import itself; remove it"
    return (f"{where}: {value!r} is implied: a part may always import itself, its own instance of the repeating "
            f"folder; remove it ({again}, another instance's too, stays allowed)")


def outside_imports(value: Any, declared: Collection[str], words: Collection[str]) -> str | None:
    """What is wrong with a value of a key outside `imports` that names a part by its plain name, written as a
    reference: its prefix `parts` or one of words, the profile's, and its part declared, told the plain name to write;
    None for any other value, which the key's reader words."""
    if not isinstance(value, str):
        return None
    prefix, dot, rest = value.partition(".")
    name = re.split("[/:]", rest, maxsplit=1)[0]
    if not dot or (prefix != "parts" and prefix not in words) or name not in declared:
        return None
    return f"{value!r}: names a part outside imports: write {name}"
