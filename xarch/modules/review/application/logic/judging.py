"""What an eval of the profile's own asks, and what it reads, in a run: how it stands (whether it may run, and if not
why); one question about each thing it reads in a file (the file whole, a class, a function), its text cut from the
file's text, masked; the reading of each answer, listed when its value is at or above the eval's line, with what is
said of it; and the value of an example file, the highest of what the eval read in it."""
from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.application.logic.evaluation import cut, said, state, value
from xarch.modules.review.application.logic.sending import why_unasked
from xarch.modules.review.domain.published import CALIBRATED, EvalRead, EvalReading, Request, Unasked
from xarch.modules.review.domain.values import Answer, Calibration, EvalText, Reads


def in_order(found: tuple[EvalRead, ...], evals: tuple[EvalText, ...]) -> tuple[EvalRead, ...]:
    """How each eval went, in the profile's order of its evals."""
    order = {asked.asked: index for index, asked in enumerate(evals)}
    return tuple(sorted(found, key=lambda item: order[item.asked]))


def below_app(file: str) -> str:
    """The path below the app of a file shown from the folder holding the app."""
    return file.split("/", 1)[1] if "/" in file else file


def standing(asked: EvalText, record: dict[str, Calibration], model: str, roots: tuple[str, ...] = (),
             mask: tuple[str, ...] = ()) -> EvalRead:
    """How an eval stands before it runs, its examples masked with roots and mask as state takes them: its state and
    why it does not run; for one that runs, its line, its examples and the model version that answered them."""
    found, why = state(asked, record.get(asked.asked), model, roots, mask)
    held = record.get(asked.asked)
    question = asked.question
    if found != CALIBRATED or held is None:
        return EvalRead(asked.asked, found, why, ask=question.ask, form=question.form)
    return EvalRead(asked.asked, found, "", held.line, len(held.flagged), len(held.clean), held.answered,
                    ask=question.ask, form=question.form)


def asked_of(asked: EvalText, file: str, part: str, text: str, found: Reads) -> tuple[Request, ...]:
    """One question about each thing the eval reads in a file (shown as file, in part, its text masked): the text of
    what it reads, its name and its lines."""
    return tuple(Request(file, part, len(piece), piece, piece=read.name, lines=read.lines, asked=asked.asked)
                 for read in found.read for piece in (cut(text, read.lines),))


def went(asked: EvalText, stood: EvalRead, requests: tuple[Request, ...],
        answers: tuple[tuple[Answer, ...] | None, ...]) -> EvalRead:
    """How an eval that may run went: how many things it was asked of, and the reading of each answer at or above its
    line, the highest first (by file and line on a tie), with its message and its fix said of it."""
    found: list[EvalReading] = []
    for item, answered in zip(requests, answers, strict=True):
        if answered is None:
            continue
        read = value(answered, asked.question, asked.flagged)
        if read >= stood.line:
            found.append(EvalReading(item.file, item.lines[0], item.piece, read,
                                     said(asked.message, item.file, item.lines[0], item.piece, read),
                                     said(asked.fix, item.file, item.lines[0], item.piece, read)))
    found.sort(key=lambda reading: (-reading.value, reading.file, reading.line))
    return replace(stood, read=len(requests), readings=tuple(found))


def unasked_of(asked: EvalText, requests: tuple[Request, ...], answers: tuple[tuple[Answer, ...] | None, ...],
               failed: bool) -> list[Unasked]:
    """Each thing an eval was to read whose question has no answer, with why."""
    return [Unasked(item.file, why_unasked(failed), item.piece, asked.asked, item.example)
            for item, answered in zip(requests, answers, strict=True) if answered is None]


def example_value(asked: EvalText, requests: tuple[Request, ...],
                  answers: tuple[tuple[Answer, ...] | None, ...]) -> float | None:
    """The value of an example file: the highest of what the eval read in it; None when one has no answer, and 0 when
    it reads nothing there."""
    if any(answered is None for answered in answers):
        return None
    return max((value(answered, asked.question, asked.flagged) for answered in answers if answered is not None),
               default=0.0)
