from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.application.logic.answers import cache_folder, record_file, versions
from xarch.modules.review.application.logic.evaluation import floor, held_as, orders, verdict
from xarch.modules.review.application.logic.evaluation import named as eval_named
from xarch.modules.review.application.logic.judging import asked_of, example_value, unasked_of
from xarch.modules.review.application.logic.masking import masked
from xarch.modules.review.application.logic.placing import groups, verdicts
from xarch.modules.review.application.logic.placing import held_as as held_as_placed
from xarch.modules.review.application.logic.questions import carried, placement, request, tokens
from xarch.modules.review.application.logic.ruling import ruled
from xarch.modules.review.application.logic.sending import needs_key, unusable_key, why_unasked
from xarch.modules.review.application.logic.withholding import examples_held, files_held, kept_examples, kept_files, too_few
from xarch.modules.review.application.ports.calibrations import Calibrations
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.decision_model import DecisionModel
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.application.services.answering import AnsweringService
from xarch.modules.review.contract import Calibrate, Calibrated, CalibrationPlanned
from xarch.modules.review.domain.errors import NoKey, NoSuchEval, Refused
from xarch.modules.review.domain.published import (
    CLEAN,
    FEWEST_EXAMPLES,
    FLAGGED,
    PLACEMENT,
    Choice,
    EvalHeld,
    ExampleRead,
    PlacementHeld,
    Request,
    Unasked,
)
from xarch.modules.review.domain.values import Answer, Calibration, CodeFile, EvalText, Run, Words

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
        """What holding the evals asked for (every one, and placement, with none) to their examples would send, with a
        dry run; else each eval held to them, and the record rewritten for each eval whose every example has its
        answer, an eval no longer in the profile dropped from it, and placement's for placement when every example of
        it has its answer. An example review.never matches is never sent and is said held back; each eval, and
        placement, is held to (and held as) the examples that remain, and an eval left with too few is not held, sends
        nothing and is recorded failed; each example of placement is read once the parts whose `holds` it would break
        are ruled out of its answer, as review reads a file of the app; raises NoSuchEval for an id of no eval,
        Refused, and NoKey for a question to send with no key set, before anything is sent."""
        words = self._profile.words(cmd.profile)
        known = (PLACEMENT, *(asked.asked for asked in words.evals))
        unknown = tuple(name for name in cmd.evals if name not in known)
        if unknown:
            raise NoSuchEval(unknown, known)
        chosen = tuple(asked for asked in words.evals if not cmd.evals or asked.asked in cmd.evals)
        evals = tuple(kept_examples(asked, words.never) for asked in chosen)
        given = self._profile.examples(cmd.profile) if not cmd.evals or PLACEMENT in cmd.evals else ((), ())
        clean, flagged = (kept_files(side, words.never) for side in given)
        withheld = (*(item for side, examples in zip((CLEAN, FLAGGED), given, strict=True)
                      for item in files_held(side, examples, words.never)),
                    *(item for asked in chosen for item in examples_held(asked, words.never)))
        short = tuple((asked.asked, kind) for asked in evals if (kind := too_few(asked)))
        question = placement(words.parts)
        placed = tuple((example, side, request(example, cmd.app.name, words.mask, (words.examples_root,)))
                       for side, examples in ((CLEAN, clean), (FLAGGED, flagged)) for example in examples if example.part)
        sends = self._model.sends()
        going, answering = Run(cache_folder(cmd.app, cmd.cache), cmd.offline), self._answering
        examples = tuple(example for asked in evals if not too_few(asked)
                         for example in self._examples(cmd, asked, words.mask))
        each = tuple((item, eval_named(asked)) for asked, _, _, items in examples for item in items)
        each += tuple((replace(item, asked=PLACEMENT, example=side), ((PLACEMENT, question),)) for _, side, item in placed)
        later = tuple(answering.kept(going, item.text, asked) for item, named in each for _, asked in named)
        if cmd.dry_run:
            shown = tuple(self._shown(going, item, named) for item, named in each)
            sent = sum(carried(item, tuple(asked for _, asked in self._sending(going, item, named) or named))
                       for item, named in each)
            return CalibrationPlanned(shown, (*((PLACEMENT,) if placed else ()), *(asked.asked for asked in evals)),
                                      sent, tokens(sent), words.mask, sends, withheld, short,
                                      groups(words.parts) if placed else ())
        if needs_key(later, cmd.offline, sends.keyed):
            raise NoKey(sends.key)
        if unusable := unusable_key(later, cmd.offline, sends):
            raise Refused(unusable)
        record = self._calibrations.get(record_file(cmd.app))
        held: list[EvalHeld] = []
        unasked: list[Unasked] = []
        for asked in evals:
            if kind := too_few(asked):
                why = f"fewer than {FEWEST_EXAMPLES} of its {kind} examples remain once review.never holds some back"
                line = asked.line if asked.line is not None else 0.0
                held.append(EvalHeld(asked.asked, (), False, line, why, by_hand=asked.line is not None, too_few=True))
                record[asked.asked] = Calibration(held_as(asked, (cmd.app.name,), words.mask), sends.model, sends.model,
                                                  False, line, crossed=why)
                continue
            read: list[ExampleRead] = []
            models: list[str] = []
            for of, on_flagged, path, items in examples:
                if of is not asked:
                    continue
                each_answer: list[tuple[Answer, ...] | None] = []
                for item in items:
                    got, going = answering.batch(going, item.text, eval_named(asked))
                    each_answer.append(None if any(answer is None for answer in got) else tuple(a for a in got if a))
                answered = tuple(each_answer)
                unasked += unasked_of(asked, items, answered, bool(going.failure),
                                      tuple(answering.refusal(going, item.text, orders(asked.question)) for item in items))
                models += [answers[0].model for answers in answered if answers]
                found = example_value(asked, items, answered)
                if found is not None:
                    read.append(ExampleRead(path, on_flagged, found))
            complete = len(read) == len(asked.flagged_examples) + len(asked.clean_examples)
            if not complete:
                held.append(EvalHeld(asked.asked, tuple(read), False, 0.0, "", False))
                continue
            flagged_read = tuple((item.path, item.value) for item in read if item.flagged)
            clean_read = tuple((item.path, item.value) for item in read if not item.flagged)
            passed, line, crossed = verdict(flagged_read, clean_read, asked.line, floor(asked.question, asked.flagged))
            held.append(EvalHeld(asked.asked, tuple(read), passed, line, crossed, by_hand=asked.line is not None))
            record[asked.asked] = Calibration(held_as(asked, (cmd.app.name,), words.mask), sends.model,
                                              models[0] if models else sends.model, passed,
                                              line, flagged_read, clean_read, crossed)
        reads: dict[str, list[tuple[CodeFile, dict[str, float]]]] = {CLEAN: [], FLAGGED: []}
        answered_by = ""
        unfit = tuple(breaks for examples in (clean, flagged)
                      for breaks in self._breaks(cmd, words, tuple(example for example in examples if example.part)))
        for (example, side, item), breaks in zip(placed, unfit, strict=True):
            answer, going = answering.answer(going, item.text, question)
            if answer is None:
                said = answering.refusal(going, item.text, (question,))
                unasked.append(Unasked(example.file, why_unasked(bool(going.failure), said), "", PLACEMENT, side, said))
            else:
                remains, _ = ruled(answer, example.part, breaks)
                reads[side].append((example, dict(remains.probabilities)))
                answered_by = answered_by or answer.model
        whole = placed and not any(item.asked == PLACEMENT for item in unasked)
        held_placement = PlacementHeld(held_as_placed(question, words.parts, (clean, flagged),
                                                      (cmd.app.name, words.examples_root), words.mask),
                                       sends.model, answered_by,
                                       verdicts(words.parts, tuple(reads[CLEAN]), tuple(reads[FLAGGED]))) if whole else None
        if held_placement is not None:
            self._calibrations.put_placement(record_file(cmd.app), held_placement)
        written = any(item.complete for item in held)
        if written:
            self._calibrations.put(record_file(cmd.app), {name: entry for name, entry in record.items()
                                                          if name in known})
        return Calibrated(tuple(held), record_file(cmd.app) if written or held_placement else None, tuple(unasked),
                          sends, len(going.asked), len(going.reused), sum(a.input_tokens for a in going.asked),
                          sum(a.output_tokens for a in going.asked), going.failure, held_placement,
                          versions(*going.asked, *going.reused), withheld)

    def _sending(self, going: Run, item: Request,
                 named: tuple[tuple[str, Choice], ...]) -> tuple[tuple[str, Choice], ...]:
        """The questions of a request whose answers are not kept: those it would send."""
        return tuple((name, asked) for name, asked in named if self._answering.kept(going, item.text, asked) is None)

    def _shown(self, going: Run, item: Request, named: tuple[tuple[str, Choice], ...]) -> Request:
        """A request as a dry run shows it: whether its answers are all kept, and the body it would send (with every
        question when none is to be sent); the names of its questions when it carries several orders of an eval's."""
        sending = self._sending(going, item, named)
        return replace(item, cached=not sending, body=self._model.body_all(item.text, sending or named),
                       questions=tuple(name for name, _ in sending or named) if len(named) > 1 else ())

    def _breaks(self, cmd: Calibrate, words: Words, examples: tuple[CodeFile, ...]) -> tuple[tuple[str, ...], ...]:
        """The parts whose `holds` each example of placement would break were it to lie there, read as a small project
        of the examples given, written for the app their code imports."""
        if not examples:
            return ()
        return self._code.breaks(cmd.profile, words.examples_root or cmd.app.name,
                                 tuple((example.file, example.text) for example in examples))

    def _examples(self, cmd: Calibrate, asked: EvalText, mask: tuple[str, ...]) -> tuple[Example, ...]:
        """Each example file of the eval, flagged ones first, with one question about each thing it reads in it, its
        text masked as a file of the app is."""
        found: list[Example] = []
        for flagged, files in ((True, asked.flagged_examples), (False, asked.clean_examples)):
            for reads in self._code.reads(cmd.profile, cmd.app.name, asked.asked, files):
                file = reads.file
                text = masked(file.text, file.imports, cmd.app.name, mask, comments=file.comments)
                found.append((asked, flagged, file.file, tuple(replace(item, example=FLAGGED if flagged else CLEAN)
                                                               for item in asked_of(asked, file.file, "", text, reads))))
        return tuple(found)
