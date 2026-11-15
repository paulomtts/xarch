from app.modules.moderation.contract import ReviewText, ReviewResult, Clean, Flagged
from app.modules.documents.application.ports.content_review import Allowed, Denied

class _Moderation(Protocol):                                  # the little we use of moderation's controller
    def review(self, cmd: ReviewText) -> ReviewResult: ...

class ModerationContentReview:                                # satisfies ContentReview, with no inheritance
    def __init__(self, moderation: _Moderation): self._m = moderation

    def review(self, title):
        match self._m.review(ReviewText(title)):       # moderation's contract, translated to documents' words
            case Clean():      return Allowed()
            case Flagged(why): return Denied(why)
