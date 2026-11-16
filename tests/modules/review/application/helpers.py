"""The review module's controller around fakes, with its service, as bootstrap/ builds it around the adapters."""
from __future__ import annotations

from tests.fakes.review import FakeAnswers, FakeCode, FakeDecisionModel, FakeProfile
from xarch.modules.review.application.controller import ReviewController
from xarch.modules.review.application.services.reviewing import ReviewService


def controller(code: FakeCode, profile: FakeProfile, model: FakeDecisionModel, answers: FakeAnswers) -> ReviewController:
    return ReviewController(ReviewService(code, profile, model, answers))
