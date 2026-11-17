"""Whether a question is sent: only when its answer is not kept, the run may send, and nothing failed before it; and
whether a run is refused for want of a key, which happens before anything is sent."""
from __future__ import annotations

from xarch.modules.review.domain.published import FAILED, NOT_CACHED, REFUSED
from xarch.modules.review.domain.values import Answer


def asks(kept: Answer | None, offline: bool, failed: bool) -> bool:
    """Whether a question is sent: its answer is not kept, the run may send, and nothing failed before it."""
    return kept is None and not offline and not failed


def why_unasked(failed: bool, refused: str = "") -> str:
    """Why a question has no answer: the decision model refused it alone (refused, its words, is not ""); something
    failed, so nothing more was sent; or it was not kept, offline."""
    return REFUSED if refused else FAILED if failed else NOT_CACHED


def needs_key(kept: tuple[Answer | None, ...], offline: bool, keyed: bool) -> bool:
    """Whether a run must be refused for want of a key: a question would be sent (one answer is not kept and the run
    may send) and the key is not set."""
    return not offline and not keyed and any(answer is None for answer in kept)
