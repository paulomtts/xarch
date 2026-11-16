"""How an eval of the profile's own reads an answer, and when it may run. The value of an answer is in 0 to 1, higher
meaning more like the fault: for a yes or no, the probability of yes; for a score, the expected level over 4; for a
choice, the probability of the options flagged, the mean of two orders of the options (as written, and reversed).
An eval runs only when it was held to its examples (calibrated) as it is written now, by the model review asks, and
passed: its flagged examples all read above its clean ones, by GAP at least on the mean, and on the right side of its
line (the one the profile writes, else midway between the lowest flagged and the highest clean value, never below
LOWEST_LINE, nor, for a score, below the first level flagged)."""
from __future__ import annotations

import hashlib
import json

from xarch.modules.review.domain.published import (
    CALIBRATED,
    CHOOSE,
    FAILED_EXAMPLES,
    GAP,
    LOWEST_LINE,
    SCORE,
    STALE,
    UNCALIBRATED,
    UNHELD,
    Choice,
)
from xarch.modules.review.domain.values import Answer, Calibration, EvalText

LEVELS = 4
"""The highest level of a score: its value is the expected level over it."""


def orders(question: Choice) -> tuple[Choice, ...]:
    """The orders of its options a question of an eval is asked in: a choice as written and reversed, since the order
    of a choice's options moves its answer; any other once."""
    if question.form != CHOOSE:
        return (question,)
    return question, Choice(question.ask, tuple(reversed(question.options)), question.form)


def value(answers: tuple[Answer, ...], question: Choice, flagged: tuple[str, ...]) -> float:
    """The value of the answers to the orders of one question (see the module)."""
    each = [dict(answer.probabilities) for answer in answers]
    if question.form == SCORE:
        return sum(int(level) * p for found in each for level, p in found.items()) / len(each) / LEVELS
    return sum(found.get(name, 0.0) for found in each for name in flagged) / len(each)


def floor(question: Choice, flagged: tuple[str, ...]) -> float:
    """The lowest line calibration sets the eval: for a score, the value of its first level flagged; else LOWEST_LINE."""
    return min(int(level) for level in flagged) / LEVELS if question.form == SCORE else LOWEST_LINE


def held_as(asked: EvalText) -> str:
    """The hash of what an eval is held to its examples as: its question in order, its options flagged, what it reads
    and where, the line it writes, and its examples; a change to any of them makes its record stale."""
    canonical = json.dumps({"ask": asked.question.ask, "form": asked.question.form,
                            "options": [[option.name, option.description] for option in asked.question.options],
                            "flagged": list(asked.flagged), "reads": asked.reads, "line": asked.line,
                            "examples": [list(map(list, asked.flagged_examples)), list(map(list, asked.clean_examples))]},
                           ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def state(asked: EvalText, record: Calibration | None, model: str) -> tuple[str, str]:
    """Whether an eval runs, and why not: CALIBRATED ("") when its record passed, as it is written now and by the model
    asked; else UNCALIBRATED, STALE or FAILED_EXAMPLES, with why."""
    if record is None:
        return UNCALIBRATED, UNHELD
    if record.held != held_as(asked):
        return STALE, "its question, answer, scope, line or examples changed since it was held to its examples"
    if record.model != model:
        return STALE, f"it was held to its examples by {record.model}, and {model} is asked now"
    if not record.passed:
        return FAILED_EXAMPLES, f"its examples failed: {record.crossed}"
    return CALIBRATED, ""


def verdict(flagged: tuple[tuple[str, float], ...], clean: tuple[tuple[str, float], ...], written: float | None,
            lowest: float) -> tuple[bool, float, str]:
    """Whether an eval passes its examples, by the value of each file (see the module), its line, and what crossed
    when it does not pass ("" when it does)."""
    low = min(flagged, key=lambda item: item[1])
    high = max(clean, key=lambda item: item[1])
    line = written if written is not None else max(round((low[1] + high[1]) / 2, 2), lowest)
    gap = sum(v for _, v in flagged) / len(flagged) - sum(v for _, v in clean) / len(clean)
    if high[1] >= low[1]:
        return False, line, (f"clean example {high[0]} reads {high[1]:.2f}, not below flagged example {low[0]} at "
                             f"{low[1]:.2f}")
    if round(gap, 9) < GAP:
        return False, line, f"the flagged examples read {gap:.2f} above the clean ones on the mean, under {GAP}"
    if low[1] < line:
        return False, line, f"flagged example {low[0]} reads {low[1]:.2f}, below the line {line:.2f}"
    if high[1] >= line:
        return False, line, f"clean example {high[0]} reads {high[1]:.2f}, not below the line {line:.2f}"
    return True, line, ""


def cut(text: str, lines: tuple[int, int]) -> str:
    """The text of the lines given, counted from 1, ((0, 0): the whole text)."""
    if lines == (0, 0):
        return text
    return "".join(text.splitlines(keepends=True)[lines[0] - 1:lines[1]])


def said(sentence: str, file: str, line: int, name: str, found: float) -> str:
    """A message or a fix of an eval said of one reading: {file}, {line}, {name} and {value} (two decimals) filled
    in."""
    return (sentence.replace("{file}", file).replace("{line}", str(line)).replace("{name}", name or file)
            .replace("{value}", f"{found:.2f}"))
