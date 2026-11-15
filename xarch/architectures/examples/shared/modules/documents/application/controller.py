from app.modules.documents.contract import (
    PublishDocument, CreateDocument, PublishResult, CreateResult, DocumentView, Published, Missing, Rejected, Created,
)
from app.modules.documents.domain.document import Document
from app.modules.documents.domain.errors import DocumentNotFound, DocumentIncomplete, ContentRejected
from app.modules.documents.application.services.document_service import DocumentService

class DocumentController:
    def __init__(self, service: DocumentService):
        self._service = service

    def publish(self, cmd: PublishDocument) -> PublishResult:
        try:
            doc = self._service.publish(cmd.id)
        except DocumentNotFound:                         # exception -> Result
            return Missing()
        except DocumentIncomplete as e:
            return Rejected(e.reason)
        return Published(self._view(doc))                 # entity -> DTO

    def create(self, cmd: CreateDocument) -> CreateResult:
        try:
            doc = self._service.create(cmd.title)
        except ContentRejected as e:                     # raised after another module said no, see section 6
            return Rejected(e.reason)
        return Created(self._view(doc))

    def _view(self, doc: Document) -> DocumentView:      # the DTO is built here: contract/ cannot import the entity
        return DocumentView(id=doc.id, title=doc.title)
