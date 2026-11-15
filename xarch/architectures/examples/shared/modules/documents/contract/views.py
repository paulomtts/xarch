from app.modules.documents.domain.values import DocumentId

@dataclass(frozen=True)
class DocumentView:               # DTO: what comes back
    id: DocumentId
    title: str
