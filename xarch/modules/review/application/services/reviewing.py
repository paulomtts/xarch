from __future__ import annotations

from xarch.modules.review.application.logic.questions import characters, placement, request, role_only, tokens
from xarch.modules.review.application.logic.selection import chosen, judged, left_out, ways, within_cap
from xarch.modules.review.application.logic.withholding import held_back
from xarch.modules.review.application.ports.code import Code
from xarch.modules.review.application.ports.profile import Profile
from xarch.modules.review.contract import Review, ReviewPlanned
from xarch.modules.review.domain.errors import Unsendable


class ReviewService:
    """Reads the files chosen, and says what placement would ask of each."""

    def __init__(self, code: Code, profile: Profile):
        self._code, self._profile = code, profile

    def review(self, cmd: Review) -> ReviewPlanned:
        """What placement would send for each file judged; raises NoSelection, AllWithOthers, OverCap, Refused, and
        Unsendable for a review that would send."""
        paths = chosen(cmd.paths, cmd.listed, cmd.every, cmd.app)
        found = self._code.files(paths, cmd.cwd, cmd.app, cmd.profile, cmd.tests)
        words = self._profile.words(cmd.profile)
        question = placement(words.parts)
        files = held_back(found, words.never)
        asked = within_cap(judged(files), cmd.max_files)
        if not cmd.dry_run:
            raise Unsendable()
        requests = tuple(request(file, cmd.app.name, words.mask) for file in asked)
        sent = characters(requests, question)
        return ReviewPlanned(ways(cmd.paths, cmd.listed, cmd.every), len(found.read) + len(found.unread), requests,
                             left_out(files), question, role_only(words.parts), sent, tokens(sent), words.mask)
