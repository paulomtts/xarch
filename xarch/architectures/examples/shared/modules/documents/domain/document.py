from app.kernel.identifiers import new_id
from app.modules.documents.domain.errors import DocumentIncomplete
from app.modules.documents.domain.values import DocumentId

class Document:
    def __init__(self, id: DocumentId, title: str, published_at: datetime | None):
        self.id, self.title, self.published_at = id, title, published_at

    @classmethod
    def new(cls, title: str) -> "Document":
        return cls(DocumentId(new_id()), title, None)                  # new_id comes from kernel/

    def publish(self, now: datetime) -> None:
        if not self.title.strip():                                     # the rule: a document needs a title
            raise DocumentIncomplete(self.id)
        self.published_at = now
