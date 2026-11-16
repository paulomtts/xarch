"""The review module's controller around fakes, with its service, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.review import FakeCode, FakeParts
from xarch.modules.review.application.controller import ReviewController
from xarch.modules.review.application.services.reviewing import ReviewService


def controller(code: FakeCode, parts: FakeParts) -> ReviewController:
    return ReviewController(ReviewService(code, parts))
