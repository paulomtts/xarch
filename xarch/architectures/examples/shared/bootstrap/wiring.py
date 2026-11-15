from app.kernel.time import Clock
from app.platform.sql import Session
from app.modules.documents.adapters.db_document_repo import DbDocumentRepo
from app.modules.documents.application.controller import DocumentController
from app.modules.documents.application.ports.content_review import ContentReview
from app.modules.documents.application.services.document_service import DocumentService
# ... and the same three imports for moderation: DbFlagRepo, ModerationService, ModerationController

def build_documents(session: Session, clock: Clock, review: ContentReview) -> DocumentController:
    repo = DbDocumentRepo(session)                             # the adapter fills the port
    service = DocumentService(repo, review, clock)             # injected into the service
    return DocumentController(service)

def build_moderation(session: Session) -> ModerationController:
    repo = DbFlagRepo(session)                                 # the same shape for every module
    service = ModerationService(repo)
    return ModerationController(service)
