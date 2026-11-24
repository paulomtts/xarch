"""How a profile writes a target, a place a part may import or a check names; checked against the parts declared, each
by its path, the part that writes it and the profile's repeating folders, each problem said at its address. Spec reads
a part's `imports` and a tier's with it, and rules the places a check of the profile's own names.

A value whose head (the text before its first `/` or `:`) holds a dot is a reference: `parts.<part>`, the part in every
instance of its repeating folder or, outside one, the part itself; or `<word>.<part>`, the part in the importer's own
instance of the folder the word repeats, a word of the profile's repeating folders; each optionally followed by
`/<path>` and, where the key takes one, `:<pattern>`. Any other value is read in the old forms: `<part>`, `<part>@any`,
`<part>/<path>` and `<part>:<pattern>`."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from typing import Any

from xarch.kernel.logic.placement import repeat_of, root_of
from xarch.kernel.placement import EACH
from xarch.profile_values.placement import Repeat, Target

TARGET = re.compile(r"(?P<part>[^@/:]*)(?:@(?P<scope>[^/:]*))?(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?")
NAME_PATTERN = re.compile(r"[^\s@/:]+")
"""A name pattern: any text but whitespace and the separators of a target, `*` standing for any text."""
_HEAD = re.compile(r"[^/:]*")
_REFERENCE = re.compile(r"(?P<part>[^/:]*)(?:/(?P<sub>[^:]*))?(?::(?P<names>.*))?", re.DOTALL)


def target(value: Any, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
           declared: Collection[str], where: str, problems: list[str], patterns: bool = False,
           mirrored: bool = False, *, alone: str, repeats: Collection[Repeat], place: bool = False) -> Target | None:
    """The target a profile writes as value, for the part owner (its name and path; None for what names no part, which
    the caller words as alone, such as "a tier's folder"), each part by its path, repeats the profile's repeating
    folders, whose words a reference names; None, with the problem said at where, when it is not one. A target that
    names a part declared but not placed is None, with no problem of its own. When mirrored, the reader is a test, whose
    own instance of the repeating folder is the one it mirrors: a bare name, or `<word>.<part>`, there is that
    instance. place says the value is a check's `place`, where a prefix that is no word may be a dotted name of code."""
    if isinstance(value, str) and "." in _HEAD.match(value)[0]:
        return _reference(value, owner, parts, declared, where, problems, patterns, mirrored, alone, repeats, place)
    match = TARGET.fullmatch(value) if isinstance(value, str) else None
    if match is None or not match["part"]:
        problems.append(f"{where}: {value!r} is not a target: use <part>, <part>@any, optionally followed by /<path>")
        return None
    name, scope, sub, names = match["part"], match["scope"], match["sub"], match["names"]
    problem = _pattern_problem(value, names, patterns)
    if problem is not None:
        problems.append(f"{where}: {problem}")
        return None
    path = parts.get(name)
    if path is None:
        if name not in declared:
            problems.append(f"{where}: {value!r} names no part {name!r}")
        return None
    in_instance = EACH in path
    owned = owner is not None and EACH in owner[1]
    if scope is not None and scope not in ("own", "any"):
        problems.append(f"{where}: {value!r} has an unknown scope '@{scope}': the only scope is @any, any instance of "
                        "the repeating folder")
        return None
    inside = mirrored or (owner is not None and owned and root_of(owner[1]) == root_of(path))
    if in_instance and scope == "own" and inside:
        problems.append(f"{where}: {value!r} says what a bare name already says: write {name}")
        return None
    if in_instance and not inside and scope != "any":
        if owner is not None and owned:
            problems.append(f"{where}: {value!r} lies in another repeating folder than part '{owner[0]}', which has "
                            f"no own instance of it: write {name}@any")
            return None
        importer = f"{owner[0]} is" if owner is not None else f"{alone} is"
        problems.append(f"{where}: {value!r} lies in the repeating folder, which {importer} not in: say {name}@any")
        return None
    if not in_instance and scope is not None:
        problems.append(f"{where}: {value!r} does not lie in the repeating folder: drop '@{scope}'")
        return None
    steps = _steps(sub)
    if steps is None:
        problems.append(f"{where}: {value!r} has an invalid path after the part")
        return None
    chosen = "any" if scope == "any" else ("own" if in_instance else "none")
    if owner is not None and name == owner[0] and chosen != "any":
        problems.append(_implied(where, value, owner, f"{name}@any"))
        return None
    return Target(name, chosen, steps, names or "")


def _reference(value: str, owner: tuple[str, tuple[str, ...]] | None, parts: Mapping[str, tuple[str, ...]],
               declared: Collection[str], where: str, problems: list[str], patterns: bool, mirrored: bool, alone: str,
               repeats: Collection[Repeat], place: bool) -> Target | None:
    """The target a reference writes (see target); None with its one problem, that of the first of its checks that
    fails: the shape, the prefix, the pattern, the part, the path, the instance, the part itself."""
    prefix, _, rest = value.partition(".")
    match = _REFERENCE.fullmatch(rest)
    if not prefix or match is None or not match["part"] or "." in match["part"] or "@" in value.partition(":")[0]:
        problems.append(f"{where}: {value!r} is not a reference: write parts.<part> or <word>.<part>, optionally followed "
                        "by /<path> and :<pattern>")
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
                  owner: tuple[str, tuple[str, ...]] | None, repeats: Collection[Repeat], mirrored: bool,
                  alone: str) -> str | None:
    """What is wrong with `<word>.<part>`: the part (its name and path) must lie in the word's folder and, but for the
    instance a test mirrors, so must the importer, owner, or what the caller words as alone; None when both do."""
    instead = f"write parts.{rest}"
    held = repeat_of(repeats, part[1])
    if held is None:
        return f"{value!r}: part {part[0]!r} lies in no <{prefix}> folder: {instead}"
    if held.word != prefix:
        return f"{value!r}: part {part[0]!r} lies in the <{held.word}> folder, not <{prefix}>: {instead}"
    if mirrored:
        return None
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
