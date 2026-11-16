from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.application.logic.answers import cache_folder, record_file
from xarch.modules.review.application.logic.evaluation import floor, held_as, orders, verdict
from xarch.modules.review.application.logic.judging import asked_of, example_value, unasked_of
from xarch.modules.review.application.logic.masking import masked
from xarch.modules.review.application.logic.questions import characters, tokens
from xarch.modules.review.application.logic.sending import needs_key
from xarch.modules.review.application.ports.calibrations import Calibrations
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.decision_model import DecisionModel
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.application.services.answering import AnsweringService
from xarch.modules.review.contract import Calibrate, Calibrated, CalibrationPlanned
from xarch.modules.review.domain.errors import NoKey, NoSuchEval
from xarch.modules.review.domain.published import CLEAN, FLAGGED, EvalHeld, ExampleRead, Request, Unasked
from xarch.modules.review.domain.values import Answer, Calibration, EvalText, Run

Example = tuple[EvalText, bool, str, tuple[Request, ...]]
"""One example file of an eval: the eval, whether the file is a flagged example, its path, and one question about each
thing the eval reads in it."""


class CalibrationService:
    """Holds the evals of the profile's own to their examples: asks the decision model of each example file, as review
    would ask of the app's files, reads the verdict and the line, and records them in the project."""

    def __init__(self, code: Code, profile: Profile, model: DecisionModel, answering: AnsweringService,
                 calibrations: Calibrations):
        self._code, self._profile, self._model, self._answering = code, profile, model, answering
        self._calibrations = calibrations

    def calibrate(self, cmd: Calibrate) -> CalibrationPlanned | Calibrated:
        """What holding the evals asked for (every one with none) to their examples would send, with a dry run; else
        each eval held to them, and the record rewritten for each eval whose every example has its answer, an eval no
        longer in the profile dropped from it; raises NoSuchEval for an id the profile writes no eval of, Refused, and
        NoKey for a question to send with no key set, before anything is sent."""
        words = self._profile.words(cmd.profile)
        known = tuple(asked.asked for asked in words.evals)
        unknown = tuple(name for name in cmd.evals if name not in known)
        if unknown:
            raise NoSuchEval(unknown, known)
        evals = tuple(asked for asked in words.evals if not cmd.evals or asked.asked in cmd.evals)
        sends = self._model.sends()
        going, answering = Run(cache_folder(cmd.app, cmd.cache), cmd.offline), self._answering
        examples = tuple(example for asked in evals for example in self._examples(cmd, asked, words.mask))
        each = tuple((item, order) for asked, _, _, items in examples for item in items
                     for order in orders(asked.question))
        later = tuple(answering.kept(going, item.text, order) for item, order in each)
        if cmd.dry_run:
            shown = tuple(replace(item, cached=kept is not None, body=self._model.body(item.text, order))
                          for (item, order), kept in zip(each, later, strict=True))
            sent = sum(characters((item,), order) for item, order in each)
            return CalibrationPlanned(shown, tuple(asked.asked for asked in evals), sent, tokens(sent), words.mask,
                                      sends)
        if needs_key(later, cmd.offline, sends.keyed):
            raise NoKey(sends.key)
        record = self._calibrations.get(record_file(cmd.app))
        held: list[EvalHeld] = []
        unasked: list[Unasked] = []
        for asked in evals:
            read: list[ExampleRead] = []
            models: list[str] = []
            for of, flagged, path, items in examples:
                if of is not asked:
                    continue
                each_answer: list[tuple[Answer, ...] | None] = []
                for item in items:
                    found_answers, going = answering.all(going, item.text, orders(asked.question))
                    each_answer.append(found_answers)
                answered = tuple(each_answer)
                unasked += unasked_of(asked, items, answered, bool(going.failure))
                models += [answers[0].model for answers in answered if answers]
                found = example_value(asked, items, answered)
                if found is not None:
                    read.append(ExampleRead(path, flagged, found))
            complete = len(read) == len(asked.flagged_examples) + len(asked.clean_examples)
            if not complete:
                held.append(EvalHeld(asked.asked, tuple(read), False, 0.0, "", False))
                continue
            flagged_read = tuple((item.path, item.value) for item in read if item.flagged)
            clean_read = tuple((item.path, item.value) for item in read if not item.flagged)
            passed, line, crossed = verdict(flagged_read, clean_read, asked.line, floor(asked.question, asked.flagged))
            held.append(EvalHeld(asked.asked, tuple(read), passed, line, crossed, by_hand=asked.line is not None))
            record[asked.asked] = Calibration(held_as(asked), sends.model, models[0] if models else sends.model, passed,
                                              line, flagged_read, clean_read, crossed)
        written = any(item.complete for item in held)
        if written:
            self._calibrations.put(record_file(cmd.app), {name: entry for name, entry in record.items()
                                                          if name in known})
        return Calibrated(tuple(held), record_file(cmd.app) if written else None, tuple(unasked), sends,
                          len(going.asked), len(going.reused), sum(a.input_tokens for a in going.asked),
                          sum(a.output_tokens for a in going.asked), going.failure)

    def _examples(self, cmd: Calibrate, asked: EvalText, mask: tuple[str, ...]) -> tuple[Example, ...]:
        """Each example file of the eval, flagged ones first, with one question about each thing it reads in it, its
        text masked as a file of the app is."""
        found: list[Example] = []
        for flagged, files in ((True, asked.flagged_examples), (False, asked.clean_examples)):
            code = dict(files)
            for reads in self._code.reads(cmd.profile, cmd.app.name, asked.asked, files):
                text = masked(code[reads.path], reads.imports, cmd.app.name, mask)
                found.append((asked, flagged, reads.path, tuple(replace(item, example=FLAGGED if flagged else CLEAN)
                                                                for item in asked_of(asked, reads.path, "", text, reads))))
        return tuple(found)
