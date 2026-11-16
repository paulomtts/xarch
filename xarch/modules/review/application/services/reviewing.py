from __future__ import annotations

from dataclasses import replace

from xarch.modules.review.application.logic.answers import cache_folder, request_key
from xarch.modules.review.application.logic.doubt import ranked, reading
from xarch.modules.review.application.logic.questions import characters, placement, request, role_only, tokens
from xarch.modules.review.application.logic.selection import chosen, judged, left_out, ways, within_cap
from xarch.modules.review.application.logic.sending import asks, needs_key, why_unasked
from xarch.modules.review.application.logic.withholding import held_back
from xarch.modules.review.application.ports.answers import Answers
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.decision_model import DecisionModel
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.contract import Review, ReviewPlanned, ReviewReading
from xarch.modules.review.domain.errors import NoKey, Unanswered
from xarch.modules.review.domain.published import Reading, Unasked


class ReviewService:
    """Reads the files chosen, says what placement would ask of each, and asks it of the decision model, an answer
    kept being read instead of asked again."""

    def __init__(self, code: Code, profile: Profile, model: DecisionModel, answers: Answers):
        self._code, self._profile, self._model, self._answers = code, profile, model, answers

    def review(self, cmd: Review) -> ReviewPlanned | ReviewReading:
        """What placement would send for each file judged, with a dry run; else the reading of each, from the answers
        kept and those asked; raises NoSelection, AllWithOthers, OverCap, Refused, and NoKey for a question to send
        with no key set, before anything is sent."""
        paths = chosen(cmd.paths, cmd.listed, cmd.every, cmd.app)
        found = self._code.files(paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        words = self._profile.words(cmd.profile)
        question = placement(words.parts)
        files = held_back(found, words.never)
        asked = within_cap(judged(files), cmd.max_files)
        sends = self._model.sends()
        folder = cache_folder(cmd.app, cmd.cache)
        requests = tuple(request(file, cmd.app.name, words.mask) for file in asked)
        keys = tuple(request_key(sends.model, item.text, question) for item in requests)
        kept = tuple(self._answers.get(folder, key) for key in keys)
        total = len(found.read) + len(found.unread)
        by = ways(cmd.paths, cmd.listed, cmd.every)
        if cmd.dry_run:
            shown = tuple(replace(item, cached=answer is not None, body=self._model.body(item.text, question))
                          for item, answer in zip(requests, kept, strict=True))
            sent = characters(requests, question)
            return ReviewPlanned(by, total, shown, left_out(files), question, role_only(words.parts), sent,
                                 tokens(sent), words.mask, sends)
        if needs_key(kept, cmd.offline, sends.keyed):
            raise NoKey(sends.key)
        readings: list[Reading] = []
        unasked: list[Unasked] = []
        failure, sent_now, spent_in, spent_out = "", 0, 0, 0
        for item, key, answer in zip(requests, keys, kept, strict=True):
            if asks(answer, cmd.offline, bool(failure)):
                try:
                    answer = self._model.ask(item.text, question)
                except Unanswered as e:
                    failure = e.reason
                else:
                    self._answers.put(folder, key, answer)
                    sent_now, spent_in, spent_out = (sent_now + 1, spent_in + answer.input_tokens,
                                                     spent_out + answer.output_tokens)
            if answer is None:
                unasked.append(Unasked(item.file, why_unasked(bool(failure))))
            else:
                readings.append(reading(item, answer))
        return ReviewReading(by, total, ranked(tuple(readings)), left_out(files), tuple(unasked), sends, sent_now,
                             sum(answer is not None for answer in kept), spent_in, spent_out, failure,
                             role_only(words.parts))
