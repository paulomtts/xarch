from app.modules.moderation.contract import ReviewText, ReviewResult, Clean, Flagged
from app.modules.documents.application.ports.content_review import Allowed, Denied

# the little we use of moderation's controller
class _Moderation(Protocol):
    def review(self, cmd: ReviewText) -> ReviewResult: ...

# satisfies ContentReview, with no inheritance
class ModerationContentReview:
    def __init__(self, moderation_controller: _Moderation): self._moderation = moderation_controller

    def review(self, title: str) -> Allowed | Denied:
        # moderation's contract, translated to documents' words
        match self._moderation.review(ReviewText(title)):
            case Clean():      return Allowed()
            case Flagged(why): return Denied(why)
