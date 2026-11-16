from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.review.application.services.reviewing import ReviewService
from xarch.modules.review.contract import (
    AllAndOthers,
    NothingChosen,
    NotSendable,
    Review,
    ReviewRefused,
    ReviewResult,
    TooManyFiles,
)
from xarch.modules.review.domain.errors import AllWithOthers, NoSelection, OverCap, Unsendable


class ReviewController:
    def __init__(self, reviewing: ReviewService):
        self._reviewing = reviewing

    def review(self, cmd: Review) -> ReviewResult:
        """No file chosen, every file asked for with others, more files than one run judges and a review that would
        send with nothing to send it with each come back as their own Result; files or a profile that cannot be read
        are refused with why. Nothing is sent before every refusal is known."""
        try:
            return self._reviewing.review(cmd)
        except NoSelection:
            return NothingChosen()
        except AllWithOthers:
            return AllAndOthers()
        except OverCap as e:
            return TooManyFiles(e.chosen, e.cap)
        except Unsendable:
            return NotSendable()
        except DomainError as e:
            return ReviewRefused(e.reason)
