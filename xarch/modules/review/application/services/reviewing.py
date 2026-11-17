from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.application.logic.answers import cache_folder, record_file, versions
from xarch.modules.review.application.logic.doubt import (
    asked_again,
    averaged,
    by_part,
    pieces_read,
    ranked,
    ranks,
    reading,
)
from xarch.modules.review.application.logic.evaluation import orders
from xarch.modules.review.application.logic.judging import asked_of, below_app, in_order, standing, unasked_of, went
from xarch.modules.review.application.logic.masking import masked
from xarch.modules.review.application.logic.placing import held_as, marked, undoubted
from xarch.modules.review.application.logic.placing import standing as placed
from xarch.modules.review.application.logic.questions import (
    characters,
    of_piece,
    piece_requests,
    placement,
    reordered,
    request,
    role_only,
    tokens,
)
from xarch.modules.review.application.logic.selection import chosen, judged, left_out, ways, within_cap
from xarch.modules.review.application.logic.sending import needs_key, why_unasked
from xarch.modules.review.application.logic.withholding import held_back, unmatched
from xarch.modules.review.application.ports.calibrations import Calibrations
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.decision_model import DecisionModel
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.application.services.answering import AnsweringService
from xarch.modules.review.contract import Review, ReviewPlanned, ReviewReading
from xarch.modules.review.domain.errors import NoKey
from xarch.modules.review.domain.published import CALIBRATED, Choice, EvalRead, PiecesRead, Reading, Request, Unasked
from xarch.modules.review.domain.values import Answer, CodeFile, EvalText, Run, Words

Asking = tuple[EvalText, EvalRead, tuple[Request, ...]]
"""An eval of the profile's own that runs: the eval, how it stands, and one question about each thing it reads."""


class ReviewService:
    """Reads the files chosen, says what placement and each eval of the profile's own that may run would ask of each,
    and asks it of the decision model, an answer kept being read instead of asked again."""

    def __init__(self, code: Code, profile: Profile, model: DecisionModel, answering: AnsweringService,
                 calibrations: Calibrations):
        self._code, self._profile, self._model, self._answering = code, profile, model, answering
        self._calibrations = calibrations

    def review(self, cmd: Review) -> ReviewPlanned | ReviewReading:
        """What placement and the evals that may run would send for each file judged (and each piece of it, with
        pieces), with a dry run; else the reading of each, from the answers kept and those asked, a file whose first
        answer is near its part's line asked again in other orders of the options and read on their mean, the pieces of
        each ranked inside it, and the readings of each eval of the profile's own at or above its line; raises
        NoSelection, AllWithOthers, InPieces, OverCap, Refused (the files, the profile, its examples or the record
        cannot be read), and NoKey for a question to send with no key set, before anything is sent."""
        paths = chosen(cmd.paths, cmd.listed, cmd.every, cmd.app, cmd.pieces)
        found = self._code.files(paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        words = self._profile.words(cmd.profile)
        examples = self._profile.examples(cmd.profile)
        question, parts = placement(words.parts), {part.name: part for part in words.parts}
        files = held_back(found, words.never)
        judging = within_cap(judged(files), cmd.max_files, cmd.pieces)
        sends = self._model.sends()
        calibration = placed(self._calibrations.placement(record_file(cmd.app)),
                             held_as(question, words.parts, examples, (cmd.app.name, words.examples_root), words.mask),
                             sends.model)
        going, answering = Run(cache_folder(cmd.app, cmd.cache), cmd.offline), self._answering
        requests = tuple(request(file, cmd.app.name, words.mask) for file in judging)
        kept = tuple(answering.kept(going, item.text, question) for item in requests)
        pieced = tuple((file, *piece_requests(file, cmd.app.name, words.mask, cmd.context)) for file in judging
                       if cmd.pieces)
        piece = of_piece(question)
        asking = tuple(item for _, items, _ in pieced if ranks(items) for item in items)
        held = tuple(answering.kept(going, item.text, piece) for item in asking)
        evals, idle = self._evals(cmd, words, judging, sends.model)
        each = tuple((item, order) for asked, _, items in evals for item in items for order in orders(asked.question))
        later = tuple(answering.kept(going, item.text, order) for item, order in each)
        total, by = len(found.read) + len(found.unread), ways(cmd.paths, cmd.listed, cmd.every)
        if cmd.dry_run:
            shown = (self._shown(requests, kept, (question,) * len(requests))
                     + self._shown(asking, held, (piece,) * len(asking))
                     + self._shown(tuple(item for item, _ in each), later, tuple(order for _, order in each)))
            sent = (characters(requests, question) + characters(asking, piece)
                    + sum(characters((item,), order) for item, order in each))
            return ReviewPlanned(by, total, shown, left_out(files), question, role_only(words.parts), sent,
                                 tokens(sent), words.mask, sends, len(reordered(question)),
                                 piece.ask if cmd.pieces else "", cmd.context,
                                 in_order(idle + tuple(s for _, s, _ in evals), words.evals), words.never,
                                 unmatched(found, words.never))
        others = reordered(question)
        again = tuple(answering.kept(going, item.text, other) for item, answer in zip(requests, kept, strict=True)
                      if answer is not None and asked_again(answer, parts[item.part]) for other in others)
        if needs_key(kept + again + held + later, cmd.offline, sends.keyed):
            raise NoKey(sends.key)
        readings: list[Reading] = []
        unasked: list[Unasked] = []
        for item in requests:
            first, going = answering.answer(going, item.text, question)
            answers = [first]
            if first is not None and asked_again(first, parts[item.part]):
                for other in others:
                    answer, going = answering.answer(going, item.text, other)
                    answers.append(answer)
            if any(answer is None for answer in answers):
                said = answering.refusal(going, item.text, (question, *others))
                unasked.append(Unasked(item.file, why_unasked(bool(going.failure), said), said=said))
            else:
                readings.append(reading(item, averaged(tuple(a for a in answers if a is not None)), parts[item.part],
                                        len(answers)))
        ranked_pieces: list[PiecesRead] = []
        for file, items, too_small in pieced:
            pieces: list[Answer | None] = []
            for item in items if ranks(items) else ():
                answer, going = answering.answer(going, item.text, piece)
                pieces.append(answer)
                if answer is None:
                    said = answering.refusal(going, item.text, (piece,))
                    unasked.append(Unasked(item.file, why_unasked(bool(going.failure), said), item.piece, said=said))
            ranked_pieces.append(pieces_read(file, items, tuple(pieces), too_small, cmd.context))
        ran: list[EvalRead] = []
        for asked, stood, items in evals:
            answered: list[tuple[Answer, ...] | None] = []
            for item in items:
                found_answers, going = answering.all(going, item.text, orders(asked.question))
                answered.append(found_answers)
            unasked += unasked_of(asked, items, tuple(answered), bool(going.failure),
                                  tuple(answering.refusal(going, item.text, orders(asked.question)) for item in items))
            ran.append(went(asked, stood, items, tuple(answered)))
        judged_files = undoubted(tuple(readings), calibration)
        return ReviewReading(by, total, ranked(judged_files), left_out(files), tuple(unasked), sends,
                             len(going.asked), len(going.reused), sum(a.input_tokens for a in going.asked),
                             sum(a.output_tokens for a in going.asked), going.failure, role_only(words.parts),
                             marked(by_part(judged_files, words.parts), calibration), tuple(ranked_pieces),
                             in_order(idle + tuple(ran), words.evals), calibration, versions(*going.asked, *going.reused))

    def _evals(self, cmd: Review, words: Words, judging: tuple[CodeFile, ...],
               model: str) -> tuple[tuple[Asking, ...], tuple[EvalRead, ...]]:
        """Each eval of the profile's own that may run, with how it stands and what it would ask of the files judged;
        and how each other one stands, which does not run."""
        record = self._calibrations.get(record_file(cmd.app))
        running: list[Asking] = []
        idle: list[EvalRead] = []
        for asked in words.evals:
            stood = standing(asked, record, model, (cmd.app.name,), words.mask)
            if stood.state != CALIBRATED:
                idle.append(stood)
                continue
            shown = {below_app(file.file): file for file in judging}
            files = tuple((path, file.text) for path, file in shown.items())
            reads = self._code.reads(cmd.profile, cmd.app.name, asked.asked, files) if files else ()
            running.append((asked, stood, tuple(
                item for found in reads for file in (shown[found.path],)
                for item in asked_of(asked, file.file, file.part, masked(file.text, file.imports, cmd.app.name,
                                                                          words.mask), found))))
        return tuple(running), tuple(idle)

    def _shown(self, requests: tuple[Request, ...], kept: tuple[Answer | None, ...],
               questions: tuple[Choice, ...]) -> tuple[Request, ...]:
        """The requests as a dry run shows them: each with whether its answer is kept, and the body it would send."""
        return tuple(replace(item, cached=answer is not None, body=self._model.body(item.text, asked))
                     for item, answer, asked in zip(requests, kept, questions, strict=True))
