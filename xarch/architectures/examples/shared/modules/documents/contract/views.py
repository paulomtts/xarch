from app.modules.documents.domain.values import DocumentId

# DTO: what comes back
@dataclass(frozen=True)
class DocumentView:
    id: DocumentId
    title: str
