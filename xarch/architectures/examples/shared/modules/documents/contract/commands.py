from app.modules.documents.domain.values import DocumentId

@dataclass(frozen=True)
class PublishDocument:            # input: what a caller sends the controller
    id: DocumentId

@dataclass(frozen=True)
class CreateDocument:             # input for the create use case
    title: str
