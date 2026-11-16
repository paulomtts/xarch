"""What `evals` says of the questions review asks, each refused at its address when it is written wrong; `check` never
reads it. Under `placement`, the built-in eval, the line of each part below which a file reads as doubtful there
(`evals.placement.lines`); under any other id, an eval of the profile's own:

    <id>:                 lowercase words joined by `-`, never `placement`
      ask: <question>     one line, at most MAX_ASK characters and one question mark
      answer: yes-no | {score: [<level 0>, ..., <level 4>], flagged_from: <1 to 4>}
              | {choice: {<option>: <description>, ...}, flagged: [<option>, ...]}   (3 options or more)
      yes: <sentence>     no: <sentence>      only with yes-no: what each answer means
      reads: file | class | function
      in: {part, where}   as a check's, the app's files only
      keep: [<filter>, ...]
      line: <above 0 and below 1>
      message: <sentence> fix: <sentence>     with {file}, {line}, {name} and {value}
      examples: {flagged: {<path>: <code>, ...}, clean: {<path>: <code>, ...}}   at least 2 of each

The words of the vocabulary in `in.where` and `keep` are the rules module's to read, as for a check."""
from __future__ import annotations

import re
from collections.abc import Collection, Mapping
from typing import Any

from xarch.kernel.violations import OWN_ID
from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of
from xarch.modules.spec.application.logic.written_checks import filters, scope
from xarch.modules.spec.domain.profile_keys import EVAL, PLACEMENT
from xarch.modules.spec.domain.published import CHOICE, READS, SCORE, YES_NO, Eval
from xarch.modules.spec.domain.values import Language
from xarch.profile_values.checks import STRUCTURE, Scope

BUILT_IN = "placement"
"""The id of the eval review always asks, which no eval of the profile's own may take."""
MAX_ASK = 400
"""The most characters the question of an eval holds: a long compound question was the one that failed the trials."""
LEVELS = 5
"""How many levels a score has: 0 to 4."""
FEWEST_EXAMPLES = 2
"""The fewest example files of each kind an eval is held to."""
VARIABLES = ("file", "line", "name", "value")
"""What a message or a fix of an eval prints of a reading."""
_VARIABLE = re.compile(r"\{([^{}]*)\}")
_ANSWER = ("answer: write yes-no, {score: [<5 levels>], flagged_from: <1 to 4>} or {choice: {<option>: <description>, "
           "...}, flagged: [<option>, ...]}")
_WRITTEN = ("ask", "answer", "reads", "message", "fix", "examples")
"""The slots every eval of the profile's own writes."""
_SIDES = {True: "yes", False: "no"}
"""The slot a key read as true or false was written as: a profile file reads `yes:` and `no:` as true and false."""


def evals(value: Any, declared: Collection[str], language: Language,
          problems: list[str]) -> tuple[dict[str, float], dict[str, Eval]]:
    """The line of each part the profile writes one for, by part, and every eval of the profile's own, by id, each in
    the order of the file; an eval with a problem is left out."""
    if not isinstance(value, Mapping):
        problems.append("evals: must be a mapping of the evals review asks, by id, such as "
                        "{placement: {lines: {documents: 0.2}}}")
        return {}, {}
    own: dict[str, Eval] = {}
    for name, body in value.items():
        if name == BUILT_IN:
            continue
        if not isinstance(name, str) or not OWN_ID.fullmatch(name):
            problems.append(f"evals: {name!r} is no id of an eval of your own, lowercase words joined by - such as "
                            "rule-outside-entity, nor a key of evals: use placement")
            continue
        count = len(problems)
        found = _own(body, f"evals.{name}", declared, language, problems)
        if found is not None and len(problems) == count:
            own[name] = found
    return _placement(value.get(BUILT_IN), declared, problems), own


def _placement(placement: Any, declared: Collection[str], problems: list[str]) -> dict[str, float]:
    if placement is None:
        return {}
    if not isinstance(placement, Mapping):
        problems.append("evals.placement: must be a mapping {lines}: the line of each part, below which a file reads "
                        "as doubtful there")
        return {}
    problems += ck.unknown_keys(placement, names_of(PLACEMENT), "evals.placement")
    return _lines(placement["lines"], declared, problems) if "lines" in placement else {}


def _lines(value: Any, declared: Collection[str], problems: list[str]) -> dict[str, float]:
    where = "evals.placement.lines"
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a mapping of parts to their line, such as {{documents: 0.2}}")
        return {}
    found: dict[str, float] = {}
    for part, line in value.items():
        if part not in declared:
            problems.append(f"{where}: {part!r} is not a part of this profile: name a part under parts")
        elif not _line(line):
            problems.append(f"{where}.{part}: {line!r} is not a line: write a number above 0 and below 1, such as 0.2")
        else:
            found[str(part)] = float(line)
    return found


def _line(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and 0 < value < 1


def _own(body: Any, where: str, declared: Collection[str], language: Language, problems: list[str]) -> Eval | None:
    slots = names_of(EVAL)
    if not isinstance(body, Mapping):
        problems.append(f"{where}: must be a map of slots: {', '.join(sorted(slots))}")
        return None
    body = {_SIDES.get(key, key) if isinstance(key, bool) else key: value for key, value in body.items()}
    problems += ck.unknown_keys(body, slots, where)
    problems += [f"{where}: missing `{slot}`" for slot in _WRITTEN if slot not in body]
    ask = _ask(body.get("ask"), f"{where}.ask", problems) if "ask" in body else ""
    form, options, flagged = _answer(body.get("answer"), body, where, problems)
    reads = _reads(body.get("reads"), f"{where}.reads", language, problems)
    within = _within(body.get("in", {}), f"{where}.in", declared, problems)
    keep = filters(body.get("keep", []), f"{where}.keep", problems)
    line = body.get("line")
    if line is not None and not _line(line):
        problems.append(f"{where}.line: {line!r} is not a line: write a number above 0 and below 1, such as 0.6")
    message = _said(body.get("message"), f"{where}.message", problems)
    fix = _said(body.get("fix"), f"{where}.fix", problems)
    examples = body.get("examples")
    shown, clean = _examples(examples, f"{where}.examples", language, problems) if examples is not None else ((), ())
    if not form:
        return None
    return Eval(ask, form, options, flagged, reads, within, keep, None if line is None else float(line), message, fix,
                shown, clean)


def _ask(value: Any, where: str, problems: list[str]) -> str:
    if not ck.line(value) or len(value) > MAX_ASK or value.count("?") > 1:
        problems.append(f"{where}: must be one short question about what the text shows: one line, at most {MAX_ASK} "
                        "characters and one question mark")
        return ""
    return value.strip()


def _answer(value: Any, body: Mapping[Any, Any], where: str,
            problems: list[str]) -> tuple[str, tuple[tuple[str, str], ...], tuple[str, ...]]:
    """The form, the options in order and the options flagged; ("", (), ()) for an answer written wrong."""
    sides = {side: body[side] for side in ("yes", "no") if side in body}
    if value == YES_NO:
        said = {side: _sentence(text, f"{where}.{side}", problems) for side, text in sides.items()}
        return YES_NO, (("yes", said.get("yes", "")), ("no", said.get("no", ""))), ("yes",)
    problems += [f"{where}.{side}: only a yes-no answer says what {side} means" for side in sides]
    if isinstance(value, Mapping) and set(value) == {"score", "flagged_from"}:
        return _score(value, f"{where}.answer", problems)
    if isinstance(value, Mapping) and set(value) == {"choice", "flagged"}:
        return _choice(value, f"{where}.answer", problems)
    if value is not None:
        problems.append(f"{where}.{_ANSWER}")
    return "", (), ()


def _score(value: Mapping[Any, Any], where: str,
           problems: list[str]) -> tuple[str, tuple[tuple[str, str], ...], tuple[str, ...]]:
    levels, start = value["score"], value["flagged_from"]
    if not isinstance(levels, list) or len(levels) != LEVELS or not all(ck.line(level) for level in levels):
        problems.append(f"{where}.score: must be five levels, from 0 to 4, each a sentence saying what that level "
                        "means, the worst last")
        return "", (), ()
    if isinstance(start, bool) or not isinstance(start, int) or not 1 <= start < LEVELS:
        problems.append(f"{where}.flagged_from: must be the level from which a reading counts as flagged, 1 to 4")
        return "", (), ()
    return SCORE, tuple((str(level), text) for level, text in enumerate(levels)), tuple(map(str, range(start, LEVELS)))


def _choice(value: Mapping[Any, Any], where: str,
            problems: list[str]) -> tuple[str, tuple[tuple[str, str], ...], tuple[str, ...]]:
    options, flagged = value["choice"], value["flagged"]
    if isinstance(options, Mapping) and len(options) == 2:
        problems.append(f"{where}.choice: two options are a yes or no: write answer: yes-no, with yes: and no:")
        return "", (), ()
    if (not isinstance(options, Mapping) or len(options) < 3
            or not all(ck.line(name) and ck.line(text) for name, text in options.items())):
        problems.append(f"{where}.choice: must be a map of at least 3 options, each to its description")
        return "", (), ()
    if (not isinstance(flagged, list) or not flagged or not all(isinstance(name, str) for name in flagged)
            or len(set(flagged)) != len(flagged) or not set(flagged) < set(options)):
        problems.append(f"{where}.flagged: must list the options that count as flagged: some of the options, not all")
        return "", (), ()
    return CHOICE, tuple((str(name), str(text)) for name, text in options.items()), tuple(flagged)


def _reads(value: Any, where: str, language: Language, problems: list[str]) -> str:
    if value not in READS:
        if value is not None:
            problems.append(f"{where}: must be {', '.join(READS[:-1])} or {READS[-1]}: what one question is asked of")
        return ""
    supplied = language.checked.supplies
    if supplied is not None and value not in {supply.fact for supply in supplied}:
        problems.append(f"{where}: needs {value}, which the reader of {language.checked.title} does not supply: read "
                        "another kind")
    return value


def _within(value: Any, where: str, declared: Collection[str], problems: list[str]) -> Scope:
    if isinstance(value, Mapping) and ({"files", "tier"} & set(value)):
        problems.append(f"{where}: review reads the app's files only: write part and where")
        return Scope()
    found = scope(value, where, set(declared), set(), problems)
    if found.part == STRUCTURE:
        problems.append(f"{where}.part: review reads the files of a part only: name a part")
    return found


def _said(value: Any, where: str, problems: list[str]) -> str:
    if value is None:
        return ""
    text = _sentence(value, where, problems, variables=True)
    problems += [f"{where}: {{{name}}} is not a variable of an eval: use {_variables()}"
                 for name in _VARIABLE.findall(text) if name not in VARIABLES]
    return text


def _variables() -> str:
    return ", ".join("{" + name + "}" for name in VARIABLES)


def _sentence(value: Any, where: str, problems: list[str], variables: bool = False) -> str:
    if not ck.line(value):
        problems.append(f"{where}: must be a sentence" + (f", with {_variables()} for what it names" if variables else ""))
        return ""
    return value.strip()


def _examples(value: Any, where: str, language: Language,
              problems: list[str]) -> tuple[tuple[tuple[str, str], ...], tuple[tuple[str, str], ...]]:
    """The code an eval must read as flagged and as clean, each file by its path below the app, at least
    FEWEST_EXAMPLES of each."""
    if not isinstance(value, Mapping):
        problems.append(f"{where}: must be a map {{flagged: {{<path>: <code>}}, clean: {{<path>: <code>}}}}")
        return (), ()
    problems += ck.unknown_keys(value, ("flagged", "clean"), where)
    found: dict[str, tuple[tuple[str, str], ...]] = {}
    for side in ("flagged", "clean"):
        files = value.get(side)
        if not isinstance(files, Mapping) or len(files) < FEWEST_EXAMPLES:
            problems.append(f"{where}.{side}: must be a map of at least {FEWEST_EXAMPLES} files, {{<path>: <code>}}: "
                            f"the code the eval must read as {side}")
            found[side] = ()
            continue
        found[side] = tuple(_example(path, code, f"{where}.{side}", language, problems) for path, code in files.items())
    return tuple(item for item in found["flagged"] if item[0]), tuple(item for item in found["clean"] if item[0])


def _example(path: Any, code: Any, where: str, language: Language, problems: list[str]) -> tuple[str, str]:
    extension = language.checked.extension
    steps = path.split("/") if isinstance(path, str) else []
    if not steps or any(step in ("", ".", "..") for step in steps) or not path.endswith(extension):
        problems.append(f"{where}: {path!r} is not a path of a source file below the app, ending in {extension}")
        return "", ""
    if not isinstance(code, str):
        problems.append(f"{where}.{path}: must be the code of the file, as text")
        return "", ""
    return path, code
