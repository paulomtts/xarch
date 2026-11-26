"""What `counterparts` says lies with what, each entry refused at its address when it is written wrong:

    counterparts:
      <id>:                lowercase words joined by `-`
        for: <path>        what must have a counterpart: a folder (ending in `/`) or a file, below the app or
                           tests/<path> below the tests; `<word>` binds the text of a step or part of one, `*` any text
        has: <path>        where its counterpart is, written as for, with the placeholders for binds
        when: [<path>, ...]  the paths that must match too for a match of for to need one, written as has
        accepted: [{path, why}, ...]  the matches of for that need none, each with why
        message: <sentence>  fix: <sentence>   with {source}, {expected}, {when}, {key} and each placeholder of for

A placeholder holds a name; two placeholders, or one and `*`, side by side in a step bind text more ways than one, and
are refused, as is a placeholder of has or when that for does not bind, and a has that is for itself."""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from xarch.kernel.violations import OWN_ID
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of
from xarch.modules.spec.domain.profile_keys import COUNTERPART
from xarch.modules.spec.domain.published import DEFAULT_TESTS, AcceptedPath, Counterpart, PathPattern

KEY = "counterparts"
"""The key the counterparts are written under."""
VARIABLES = ("source", "expected", "when", "key")
"""What a message or a fix of a counterpart prints, besides each placeholder of its for."""
_PLACEHOLDER = re.compile(r"<([^<>]*)>")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_TOKEN = re.compile(r"<[^<>]*>|\*")
_VARIABLE = re.compile(r"\{([^{}]*)\}")
_PATH = "must be a path below the app, or tests/<path> below the tests, such as documents/<name>/"


def counterparts(value: Any, problems: list[str]) -> tuple[Counterpart, ...]:
    """Every counterpart the profile writes, in the order of the file; one with a problem is left out."""
    if not isinstance(value, Mapping):
        problems.append(f"{KEY}: must be a map of counterparts by id, such as {{document-has-check: {{for: "
                        "documents/<name>/, has: tests/documents/<name>/}}")
        return ()
    found: list[Counterpart] = []
    for name, entry in value.items():
        if not isinstance(name, str) or not OWN_ID.fullmatch(name):
            problems.append(f"{KEY}: {str(name)!r} is no id of a counterpart: write lowercase words joined by -, such "
                            "as document-has-check")
            continue
        read = _counterpart(name, entry, problems)
        if read is not None:
            found.append(read)
    return tuple(found)


def _counterpart(name: str, entry: Any, problems: list[str]) -> Counterpart | None:
    at = f"{KEY}.{name}"
    if not isinstance(entry, Mapping):
        problems.append(f"{at}: must be a map {{for, has, when, accepted, message, fix}}")
        return None
    count = len(problems)
    problems += ck.unknown_keys(entry, names_of(COUNTERPART), at, COUNTERPART)
    problems += [f"{at}: missing `{key}`" for key in ("for", "has") if key not in entry]
    source = _pattern(entry["for"], f"{at}.for", problems) if "for" in entry else None
    bound = set(_placeholders(source)) if source is not None else None
    has = _pattern(entry["has"], f"{at}.has", problems) if "has" in entry else None
    _bound_by(has, bound, f"{at}.has", problems)
    if has is not None and source is not None and has == source:
        problems.append(f"{at}.has: is the path of for: a counterpart lies elsewhere")
    when = _when(entry.get("when", []), bound, f"{at}.when", problems)
    accepted = _accepted(entry["accepted"], f"{at}.accepted", problems) if "accepted" in entry else ()
    said = {slot: _sentence(entry[slot], bound, f"{at}.{slot}", problems) for slot in ("message", "fix")
            if slot in entry}
    if len(problems) > count or source is None or has is None:
        return None
    return Counterpart(name, source, has, when, accepted, said.get("message", ""), said.get("fix", ""))


def _pattern(value: Any, where: str, problems: list[str]) -> PathPattern | None:
    """The path as written, refused when it is no path below the app or the tests, or when a placeholder of it holds
    no name, or stands beside another or beside `*` in a step."""
    steps = tuple(value.strip("/").split("/")) if ck.text(value) else ()
    if not steps or steps == (DEFAULT_TESTS,) or any(step in ("", ".", "..") for step in steps):
        problems.append(f"{where}: {value!r}: {_PATH}")
        return None
    if any(not _NAME.fullmatch(held) for step in steps for held in _PLACEHOLDER.findall(step)) or any(
            "<" in rest or ">" in rest for step in steps for rest in [_PLACEHOLDER.sub("", step)]):
        problems.append(f"{where}: {value!r}: a placeholder holds a name, such as <name>")
        return None
    for step in steps:
        tokens = list(_TOKEN.finditer(step))
        if any(token.end() == after.start() for token, after in zip(tokens, tokens[1:])):
            problems.append(f"{where}: {value!r}: the step {step!r} puts two placeholders, or a placeholder and `*`, "
                            "side by side, which bind text more ways than one: write text between them")
            return None
    return PathPattern(steps, value.endswith("/"))


def _placeholders(pattern: PathPattern | None) -> list[str]:
    """The placeholders of the pattern, each once, in the order written."""
    return list(dict.fromkeys(held for step in (pattern.steps if pattern else ()) for held in _PLACEHOLDER.findall(step)))


def _bound_by(pattern: PathPattern | None, bound: set[str] | None, where: str, problems: list[str]) -> None:
    """Says each placeholder of the pattern that for does not bind, bound None when for is refused."""
    if bound is not None:
        problems += [f"{where}: <{held}> is bound by no step of for" for held in _placeholders(pattern)
                     if held not in bound]


def _when(value: Any, bound: set[str] | None, where: str, problems: list[str]) -> tuple[PathPattern, ...]:
    if not isinstance(value, list):
        problems.append(f"{where}: must be a list of paths, such as [tests/fakes/<name>/]")
        return ()
    found: list[PathPattern] = []
    for index, item in enumerate(value):
        pattern = _pattern(item, f"{where}.{index}", problems)
        _bound_by(pattern, bound, f"{where}.{index}", problems)
        if pattern is not None:
            found.append(pattern)
    return tuple(found)


def _accepted(value: Any, where: str, problems: list[str]) -> tuple[AcceptedPath, ...]:
    if not isinstance(value, list) or not value:
        problems.append(f"{where}: must be a list of {{path, why}}, such as [{{path: <a path for matches>, why: <the "
                        "reason>}]")
        return ()
    return ck.accepted_paths(value, where, "why it needs no counterpart", problems)


def _sentence(value: Any, bound: set[str] | None, where: str, problems: list[str]) -> str:
    """A message or a fix as written, one line whose variables are VARIABLES and the placeholders for binds."""
    if not ck.line(value):
        problems.append(f"{where}: must be one line of text")
        return ""
    known = (*VARIABLES, *sorted(bound or ()))
    shown = ", ".join(f"{{{name}}}" for name in VARIABLES)
    own = ", ".join(f"{{{name}}}" for name in sorted(bound or ()))
    shown += f" or a placeholder of for ({own})" if own else ""
    problems += [f"{where}: {{{name}}} is no variable: use {shown}"
                 for name in dict.fromkeys(_VARIABLE.findall(value)) if name not in known]
    return value
