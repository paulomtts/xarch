from app.kernel.time import Clock
from app.modules.documents.domain.document import Document
from app.modules.documents.domain.errors import DocumentNotFound, ContentRejected
from app.modules.documents.domain.values import DocumentId
from app.modules.documents.application.ports.content_review import ContentReview, Denied
from app.modules.documents.application.ports.document_repo import DocumentRepo

class DocumentService:
    def __init__(self, repo: DocumentRepo, review: ContentReview, clock: Clock):   # review: another module, see section 6
        self._repo, self._review, self._clock = repo, review, clock

    def publish(self, id: DocumentId) -> Document:
        doc = self._repo.get(id)                                 # load
        if doc is None:
            raise DocumentNotFound(id)                           # precondition: it must exist
        doc.publish(self._clock.now())                           # the domain decides if it is legal
        self._repo.save(doc)                                     # persist
        return doc

    def create(self, title: str) -> Document:
        match self._review.review(title):                        # another module, through a port (section 6)
            case Denied(why): raise ContentRejected(why)         # the controller maps this to Rejected
        doc = Document.new(title)
        self._repo.save(doc)                                     # persist
        return doc                                               # the entity; the controller builds the DTO
