from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.modules.review.application.logic.answers import cache_folder, request_key
from xarch.modules.review.application.logic.doubt import (
    asked_again,
    averaged,
    by_part,
    pieces_read,
    ranked,
    ranks,
    reading,
)
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
from xarch.modules.review.application.logic.sending import asks, needs_key, why_unasked
from xarch.modules.review.application.logic.withholding import held_back
from xarch.modules.review.application.ports.answers import Answers
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.decision_model import DecisionModel
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.contract import Review, ReviewPlanned, ReviewReading
from xarch.modules.review.domain.errors import NoKey, Unanswered
from xarch.modules.review.domain.published import Choice, PiecesRead, Reading, Request, Unasked
from xarch.modules.review.domain.values import Answer


class ReviewService:
    """Reads the files chosen, says what placement would ask of each, and asks it of the decision model, an answer
    kept being read instead of asked again."""

    def __init__(self, code: Code, profile: Profile, model: DecisionModel, answers: Answers):
        self._code, self._profile, self._model, self._answers = code, profile, model, answers

    def review(self, cmd: Review) -> ReviewPlanned | ReviewReading:
        """What placement would send for each file judged (and each piece of it, with pieces), with a dry run; else
        the reading of each, from the answers kept and those asked, a file whose first answer is near its part's line
        asked again in other orders of the options and read on their mean, and the pieces of each ranked inside it;
        raises NoSelection, AllWithOthers, InPieces, OverCap, Refused, and NoKey for a question to send with no key
        set, before anything is sent."""
        paths = chosen(cmd.paths, cmd.listed, cmd.every, cmd.app, cmd.pieces)
        found = self._code.files(paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        words = self._profile.words(cmd.profile)
        question, parts = placement(words.parts), {part.name: part for part in words.parts}
        files = held_back(found, words.never)
        judging = within_cap(judged(files), cmd.max_files, cmd.pieces)
        sends = self._model.sends()
        folder = cache_folder(cmd.app, cmd.cache)
        requests = tuple(request(file, cmd.app.name, words.mask) for file in judging)
        kept = tuple(self._kept(folder, sends.model, item.text, question) for item in requests)
        pieced = tuple((file, *piece_requests(file, cmd.app.name, words.mask, cmd.context)) for file in judging
                       if cmd.pieces)
        piece = of_piece(question)
        asking = tuple(item for _, items, _ in pieced if ranks(items) for item in items)
        held = tuple(self._kept(folder, sends.model, item.text, piece) for item in asking)
        total, by = len(found.read) + len(found.unread), ways(cmd.paths, cmd.listed, cmd.every)
        if cmd.dry_run:
            shown = self._shown(requests, kept, question) + self._shown(asking, held, piece)
            sent = characters(requests, question) + characters(asking, piece)
            return ReviewPlanned(by, total, shown, left_out(files), question, role_only(words.parts), sent,
                                 tokens(sent), words.mask, sends, len(reordered(question)),
                                 piece.ask if cmd.pieces else "", cmd.context)
        others = reordered(question)
        again = tuple(self._kept(folder, sends.model, item.text, other) for item, answer in zip(requests, kept, strict=True)
                      if answer is not None and asked_again(answer, parts[item.part]) for other in others)
        if needs_key(kept + again + held, cmd.offline, sends.keyed):
            raise NoKey(sends.key)
        readings: list[Reading] = []
        unasked: list[Unasked] = []
        asked: list[Answer] = []
        reused: list[Answer] = []
        failure = ""
        for item, answer in zip(requests, kept, strict=True):
            answers = [answer]
            answers[0], failure = self._answer(folder, sends.model, item.text, question, answer, cmd, failure,
                                               (asked, reused))
            if answers[0] is not None and asked_again(answers[0], parts[item.part]):
                for other in others:
                    known = self._kept(folder, sends.model, item.text, other)
                    again_found, failure = self._answer(folder, sends.model, item.text, other, known, cmd, failure,
                                                        (asked, reused))
                    answers.append(again_found)
            if any(answer is None for answer in answers):
                unasked.append(Unasked(item.file, why_unasked(bool(failure))))
            else:
                readings.append(reading(item, averaged(tuple(a for a in answers if a is not None)), parts[item.part],
                                        len(answers)))
        ranked_pieces: list[PiecesRead] = []
        for file, items, too_small in pieced:
            pieces: list[Answer | None] = []
            for item in items if ranks(items) else ():
                known = self._kept(folder, sends.model, item.text, piece)
                answer, failure = self._answer(folder, sends.model, item.text, piece, known, cmd, failure,
                                               (asked, reused))
                pieces.append(answer)
                if answer is None:
                    unasked.append(Unasked(item.file, why_unasked(bool(failure)), item.piece))
            ranked_pieces.append(pieces_read(file, items, tuple(pieces), too_small, cmd.context))
        return ReviewReading(by, total, ranked(tuple(readings)), left_out(files), tuple(unasked), sends, len(asked),
                             len(reused), sum(a.input_tokens for a in asked), sum(a.output_tokens for a in asked),
                             failure, role_only(words.parts), by_part(tuple(readings), words.parts),
                             tuple(ranked_pieces))

    def _shown(self, requests: tuple[Request, ...], kept: tuple[Answer | None, ...], question: Choice,
               ) -> tuple[Request, ...]:
        """The requests as a dry run shows them: each with whether its answer is kept, and the body it would send."""
        return tuple(replace(item, cached=answer is not None, body=self._model.body(item.text, question))
                     for item, answer in zip(requests, kept, strict=True))

    def _kept(self, folder: Path, model: str, text: str, question: Choice) -> Answer | None:
        return self._answers.get(folder, request_key(model, text, question))

    def _answer(self, folder: Path, model: str, text: str, question: Choice, kept: Answer | None, cmd: Review,
                failure: str, tally: tuple[list[Answer], list[Answer]]) -> tuple[Answer | None, str]:
        """The answer kept, which is added to the second list of tally, else the decision model's, which is kept and
        added to the first; and the failure so far, the decision model's words when it fails now."""
        if not asks(kept, cmd.offline, bool(failure)):
            if kept is not None:
                tally[1].append(kept)
            return kept, failure
        try:
            answer = self._model.ask(text, question)
        except Unanswered as e:
            return None, e.reason
        self._answers.put(folder, request_key(model, text, question), answer)
        tally[0].append(answer)
        return answer, failure
