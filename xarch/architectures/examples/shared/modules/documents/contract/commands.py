from app.modules.documents.domain.values import DocumentId

# input: what a caller sends the controller
@dataclass(frozen=True)
class PublishDocument:
    id: DocumentId

# input for the create use case
@dataclass(frozen=True)
class CreateDocument:
    title: str
