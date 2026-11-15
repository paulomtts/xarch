@dataclass(frozen=True)
class Allowed: ...
@dataclass(frozen=True)
class Denied: why: str

class ContentReview(Protocol):
    def review(self, title: str) -> Allowed | Denied: ...
