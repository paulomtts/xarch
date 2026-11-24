"""The folder tree a profile writes under `parts`, walked once, depth first, in the order the file writes its keys: a
key ending in `/` is a folder of one or more steps, a key holding a dot is a file, and any other key is a key of the
part the folder or file is. A folder holding a key of a part is a part, and a file always is; a part is named by
`name:`, else by its folder's last step or its file's name before the first dot, and two parts of one name are refused,
never renamed. The walk yields the parts in reading order, a part before the parts inside it, each with its own keys;
the folders that are no part, each with its note; the problems of the tree, each addressed by part name where the
place is a part; and, for a profile whose parts write their `path` as before 0.3.0, only a refusal for each such part,
so that nothing is read from parts that were never written as a tree."""
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from xarch.kernel.placement import EACH
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of, required_of
from xarch.modules.spec.domain.profile_keys import PART
from xarch.modules.spec.domain.values import Language

_REPEATING = re.compile(r"<([A-Za-z_][A-Za-z0-9_-]*)>")
_TREE = "parts: must be the folder tree of the app: folders ending in /, files with their extension"


@dataclass(frozen=True)
class TreePart:
    """A part of the tree: its name, its steps from the app (EACH for a repeating step) and the words of its repeating
    steps, its place in the reading order from 0, its own keys, its path as written (a folder's ending in /), and
    whether it is a file."""
    name: str
    steps: tuple[str, ...]
    words: tuple[str, ...]
    order: int
    keys: Mapping[str, Any]
    shown: str
    file: bool


@dataclass(frozen=True)
class TreeFolder:
    """A folder of the tree that is no part: its steps from the app (EACH for a repeating step) and its note, "" for
    none."""
    steps: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class PartsTree:
    """What the tree holds: its parts in reading order, its folders that are no part, the refusals of the parts
    written as before 0.3.0 (when there is one, nothing else is read), and its problems."""
    parts: tuple[TreePart, ...] = ()
    folders: tuple[TreeFolder, ...] = ()
    old: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()


@dataclass(frozen=True)
class _Found:
    """What the walk has found so far: the parts, the folders that are no part, the problems, the path each name was
    first given at, the path of every node read as a part, refused or not, and the language."""
    parts: list[TreePart]
    folders: list[TreeFolder]
    problems: list[str]
    named: dict[str, str]
    met: list[str]
    language: Language


def parts_tree(value: Any, language: Language) -> PartsTree:
    """The tree a profile writes under `parts`; language gives the endings a file key must have, none checked when it
    lists none."""
    if not isinstance(value, Mapping):
        return PartsTree(problems=(_TREE,))
    old = tuple(_old(str(key), spec) for key, spec in value.items() if _own(key) and _holds_path(spec))
    if old:
        return PartsTree(old=old)
    found = _Found([], [], [], {}, [], language)
    _walk(value, (), found)
    return PartsTree(tuple(found.parts), tuple(found.folders), (), tuple(found.problems))


def _own(key: Any) -> bool:
    """Whether a key of the tree is a key of a part: it ends in no `/` and holds no dot."""
    return not isinstance(key, str) or (not key.endswith("/") and "." not in key)


def _holds_path(spec: Any) -> bool:
    return isinstance(spec, Mapping) and "path" in spec


def _known() -> str:
    return ", ".join(sorted(names_of(PART)))


def _old(key: str, spec: Mapping[Any, Any]) -> str:
    """The refusal of a part written as before 0.3.0, saying the folder or file to write it as and where."""
    path = spec["path"]
    steps = path.strip("/").split("/") if ck.text(path) else []
    if not steps or "" in steps:
        what = "a folder ending in /"
    else:
        *parent, last = steps
        given = last.split(".")[0] if "." in last else last
        shown = f"the file {last}" if "." in last else f"the folder {last}/"
        named = f"with name: {key}, " if key != given else ""
        where = f"under the folder it lies in ({'/'.join(parent)}/)" if parent else "at the top of parts"
        what = f"{shown}: {named}{where}"
    return f"parts.{key}: unknown key 'path': moved in 0.3.0: write the part as {what}; use {_known()}"


def _walk(node: Mapping[Any, Any], at: tuple[str, ...], found: _Found) -> None:
    """The folders and files a node holds, in the order written, below the folder whose steps as written are at."""
    firsts: dict[str, tuple[str, tuple[str, ...]]] = {}
    for key, value in node.items():
        if _own(key):
            if not at:
                found.problems.append(f"parts: unknown key {str(key)!r}: a key under parts is a folder ending in / or "
                                      f"a file ending in {ck.endings(found.language)}")
            continue
        steps = _steps(key, found.problems)
        if steps is None:
            continue
        if steps[0] in firsts:
            prior, written = firsts[steps[0]]
            common = _common(written, steps)
            found.problems.append(f"parts: the folder '{'/'.join(at + common)}/' is written twice, in '{prior}' and "
                                  f"'{key}': write it once and nest what lies in it")
            continue
        firsts[steps[0]] = (key, steps)
        met = len(found.met)
        if key.endswith("/"):
            _folder(at + steps, value, found)
        else:
            _file(at + steps, key, value, found)
        repeat = next((i for i, step in enumerate(steps) if _REPEATING.fullmatch(step)), None)
        if repeat is not None and len(found.met) == met:
            found.problems.append(f"parts: '{'/'.join(at + steps[:repeat + 1])}/' is a repeating folder with no part "
                                  "below it: write a part in it, or drop it")


def _steps(key: str, problems: list[str]) -> tuple[str, ...] | None:
    """The steps a folder or file key writes, `<word>` as written; None, said, when one of them is no step."""
    steps = tuple((key[:-1] if key.endswith("/") else key).split("/"))
    if any(step in ("", ".", "..") or "\\" in step for step in steps):
        problems.append(f"parts: '{key}' has an empty, `.` or `..` step")
    elif any(EACH in step for step in steps):
        problems.append(f"parts: '{key}' has a `*` step: write the repeating folder as one word between `<` and `>`")
    elif any(("<" in step or ">" in step) and not _REPEATING.fullmatch(step) for step in steps):
        problems.append(f"parts: '{key}' has a step with `<` or `>` that is not one word between them: write the "
                        "repeating folder as `<name>`")
    else:
        return steps
    return None


def _common(first: tuple[str, ...], second: tuple[str, ...]) -> tuple[str, ...]:
    """The steps two keys of one map both start with."""
    common: list[str] = []
    for one, other in zip(first, second, strict=False):
        if one != other:
            break
        common.append(one)
    return tuple(common)


def _folder(path: tuple[str, ...], value: Any, found: _Found) -> None:
    """A folder: a part when it holds a key of a part, else a folder with its note; then what lies in it."""
    if isinstance(value, Mapping):
        own = {key: item for key, item in value.items() if _own(key)}
        if not _part(path, f"{'/'.join(path)}/", False, own, found):
            found.folders.append(TreeFolder(_placed(path), ""))
        _walk(value, path, found)
    elif value is None or (isinstance(value, str) and "\n" not in value):
        found.folders.append(TreeFolder(_placed(path), value or ""))
    else:
        found.problems.append(f"parts: '{'/'.join(path)}/': a folder is a map, one line of text (its note), or "
                              "nothing")


def _file(path: tuple[str, ...], key: str, value: Any, found: _Found) -> None:
    """A file: always a part, a map with role, ending in one of the language's endings, holding nothing below it."""
    shown, stem = "/".join(path), path[-1].split(".")[0]
    if not isinstance(value, Mapping):
        found.met.append(shown)
        found.problems.append(f"parts.{stem}: a file is a part: write it as a map with role")
        return
    own = {name: item for name, item in value.items() if _own(name)}
    name = own.get("name", stem)
    if len(own) < len(value):
        found.problems.append(f"parts.{name}: '{shown}' is a file and holds nothing below it")
    extensions = tuple(found.language.checked.extensions)
    if extensions and not path[-1].endswith(extensions):
        found.met.append(shown)
        found.problems.append(f"parts.{name}: '{shown}' is a file, since its key holds a dot, but it does not end in "
                              f"{ck.endings(found.language)}: write a folder as {key}/")
        return
    _part(path, shown, True, own, found)


def _part(path: tuple[str, ...], shown: str, file: bool, own: Mapping[Any, Any], found: _Found) -> bool:
    """Whether the folder or file at path is a part (a file always is, a folder when it holds a key of a part), with
    the problems of its own keys and its name; a part of a good name not yet given is found."""
    known = names_of(PART)
    given = path[-1].split(".")[0] if file else path[-1]
    name = own.get("name", given)
    where = f"parts.{name}"
    if not file and not any(key in known for key in own):
        found.problems.extend(ck.unknown_keys(own, known, where, PART))
        return False
    found.met.append(shown)
    if not ck.text(name) or not ck.PART_NAME.fullmatch(name):
        found.problems.append(f"parts: '{shown}' is named '{name}', which is not a part name: write name: with "
                              "letters, digits, '_' and '-'")
        return True
    found.problems.extend(ck.unknown_keys(own, known, where, PART))
    found.problems.extend(f"{where}: missing `{key}`" for key in required_of(PART) if key not in own)
    if name in found.named:
        found.problems.append(f"{where}: '{found.named[name]}' and '{shown}' are both named {name}: write name: "
                              "<part name> on one of them")
        return True
    found.named[name] = shown
    words = tuple(match.group(1) for match in map(_REPEATING.fullmatch, path) if match)
    found.parts.append(TreePart(name, _placed(path), words, len(found.parts), dict(own), shown, file))
    return True


def _placed(path: tuple[str, ...]) -> tuple[str, ...]:
    """The steps as the layout holds them: a repeating step as EACH."""
    return tuple(EACH if _REPEATING.fullmatch(step) else step for step in path)
