from app.modules.documents.contract import (
    PublishDocument, CreateDocument, PublishResult, CreateResult, Published, Missing, Rejected, Created,
)
from app.modules.documents.domain.errors import DocumentNotFound, DocumentIncomplete, ContentRejected
from app.modules.documents.application.services.document_service import DocumentService

class DocumentController:
    def __init__(self, service: DocumentService):
        self._service = service

    def publish(self, cmd: PublishDocument) -> PublishResult:
        try:
            view = self._service.publish(cmd.id)
        # exception -> Result
        except DocumentNotFound:
            return Missing()
        except DocumentIncomplete as e:
            return Rejected(e.reason)
        # the service built the DTO
        return Published(view)

    def create(self, cmd: CreateDocument) -> CreateResult:
        try:
            view = self._service.create(cmd.title)
        # raised after another module said no, see section 6
        except ContentRejected as e:
            return Rejected(e.reason)
        return Created(view)
