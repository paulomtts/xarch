"""What `evals` says of the questions review asks: today the line of each part below which a file reads as doubtful
there (`evals.placement.lines`), each refused at its address when it is written wrong. `check` never reads it."""
from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Any

from xarch.modules.spec.application.logic import profile_checks as ck
from xarch.modules.spec.application.logic.key_lookup import names_of
from xarch.modules.spec.domain.profile_keys import EVALS, PLACEMENT


def lines(value: Any, declared: Collection[str], problems: list[str]) -> dict[str, float]:
    """The line of each part the profile writes one for, by part, in the order of the file."""
    if not isinstance(value, Mapping):
        problems.append("evals: must be a mapping of the evals review asks, by id, such as "
                        "{placement: {lines: {documents: 0.2}}}")
        return {}
    problems += ck.unknown_keys(value, names_of(EVALS), "evals")
    placement = value.get("placement")
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
