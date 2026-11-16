from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.review.application.services.reviewing import ReviewService
from xarch.modules.review.contract import (
    AllAndOthers,
    KeyMissing,
    NothingChosen,
    Review,
    ReviewRefused,
    ReviewResult,
    TooManyFiles,
)
from xarch.modules.review.domain.errors import AllWithOthers, NoKey, NoSelection, OverCap


class ReviewController:
    def __init__(self, reviewing: ReviewService):
        self._reviewing = reviewing

    def review(self, cmd: Review) -> ReviewResult:
        """No file chosen, every file asked for with others, more files than one run judges and a review that would
        send with no key set each come back as their own Result; files or a profile that cannot be read are refused
        with why. Nothing is sent before every refusal is known."""
        try:
            return self._reviewing.review(cmd)
        except NoSelection:
            return NothingChosen()
        except AllWithOthers:
            return AllAndOthers()
        except OverCap as e:
            return TooManyFiles(e.chosen, e.cap)
        except NoKey as e:
            return KeyMissing(e.variable)
        except DomainError as e:
            return ReviewRefused(e.reason)
