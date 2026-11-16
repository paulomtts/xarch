from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from xarch.modules.review.application.logic.answers import cache_folder, request_key
from xarch.modules.review.application.logic.doubt import asked_again, averaged, by_part, ranked, reading
from xarch.modules.review.application.logic.questions import (
    characters,
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
from xarch.modules.review.domain.published import Choice, Reading, Unasked
from xarch.modules.review.domain.values import Answer


class ReviewService:
    """Reads the files chosen, says what placement would ask of each, and asks it of the decision model, an answer
    kept being read instead of asked again."""

    def __init__(self, code: Code, profile: Profile, model: DecisionModel, answers: Answers):
        self._code, self._profile, self._model, self._answers = code, profile, model, answers

    def review(self, cmd: Review) -> ReviewPlanned | ReviewReading:
        """What placement would send for each file judged, with a dry run; else the reading of each, from the answers
        kept and those asked, a file whose first answer is near its part's line asked again in other orders of the
        options and read on their mean; raises NoSelection, AllWithOthers, OverCap, Refused, and NoKey for a question
        to send with no key set, before anything is sent."""
        paths = chosen(cmd.paths, cmd.listed, cmd.every, cmd.app)
        found = self._code.files(paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        words = self._profile.words(cmd.profile)
        question = placement(words.parts)
        parts = {part.name: part for part in words.parts}
        files = held_back(found, words.never)
        judging = within_cap(judged(files), cmd.max_files)
        sends = self._model.sends()
        folder = cache_folder(cmd.app, cmd.cache)
        requests = tuple(request(file, cmd.app.name, words.mask) for file in judging)
        kept = tuple(self._kept(folder, sends.model, item.text, question) for item in requests)
        total = len(found.read) + len(found.unread)
        by = ways(cmd.paths, cmd.listed, cmd.every)
        if cmd.dry_run:
            shown = tuple(replace(item, cached=answer is not None, body=self._model.body(item.text, question))
                          for item, answer in zip(requests, kept, strict=True))
            sent = characters(requests, question)
            return ReviewPlanned(by, total, shown, left_out(files), question, role_only(words.parts), sent,
                                 tokens(sent), words.mask, sends, len(reordered(question)))
        others = reordered(question)
        again = tuple(self._kept(folder, sends.model, item.text, other) for item, answer in zip(requests, kept, strict=True)
                      if answer is not None and asked_again(answer, parts[item.part]) for other in others)
        if needs_key(kept + again, cmd.offline, sends.keyed):
            raise NoKey(sends.key)
        readings: list[Reading] = []
        unasked: list[Unasked] = []
        asked: list[Answer] = []
        failure, cached = "", 0
        for item, answer in zip(requests, kept, strict=True):
            answers = [answer]
            answer, failure = self._answer(folder, sends.model, item.text, question, answer, cmd, failure, asked)
            answers[0] = answer
            if answer is not None and asked_again(answer, parts[item.part]):
                for other in others:
                    known = self._kept(folder, sends.model, item.text, other)
                    cached += known is not None
                    found, failure = self._answer(folder, sends.model, item.text, other, known, cmd, failure, asked)
                    answers.append(found)
            if any(found is None for found in answers):
                unasked.append(Unasked(item.file, why_unasked(bool(failure))))
            else:
                readings.append(reading(item, averaged(tuple(found for found in answers if found is not None)),
                                        parts[item.part], len(answers)))
        cached += sum(answer is not None for answer in kept)
        return ReviewReading(by, total, ranked(tuple(readings)), left_out(files), tuple(unasked), sends, len(asked),
                             cached, sum(a.input_tokens for a in asked), sum(a.output_tokens for a in asked), failure,
                             role_only(words.parts), by_part(tuple(readings), words.parts))

    def _kept(self, folder: Path, model: str, text: str, question: Choice) -> Answer | None:
        return self._answers.get(folder, request_key(model, text, question))

    def _answer(self, folder: Path, model: str, text: str, question: Choice, kept: Answer | None, cmd: Review,
                failure: str, asked: list[Answer]) -> tuple[Answer | None, str]:
        """The answer kept, else the decision model's, which is kept and added to asked; and the failure so far, the
        decision model's words when it fails now."""
        if not asks(kept, cmd.offline, bool(failure)):
            return kept, failure
        try:
            answer = self._model.ask(text, question)
        except Unanswered as e:
            return None, e.reason
        self._answers.put(folder, request_key(model, text, question), answer)
        asked.append(answer)
        return answer, failure
