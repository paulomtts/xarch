from app.kernel.time import Clock
from app.modules.documents.contract import DocumentView
from app.modules.documents.domain.document import Document
from app.modules.documents.domain.errors import DocumentNotFound, ContentRejected
from app.modules.documents.domain.values import DocumentId
from app.modules.documents.application.ports.content_review import ContentReview, Denied
from app.modules.documents.application.ports.document_repo import DocumentRepo

class DocumentService:
    # review: another module, see section 6
    def __init__(self, repo: DocumentRepo, review: ContentReview, clock: Clock):
        self._repo, self._review, self._clock = repo, review, clock

    def publish(self, id: DocumentId) -> DocumentView:
        # load
        doc = self._repo.get(id)
        if doc is None:
            # precondition: it must exist
            raise DocumentNotFound(id)
        # the domain decides if it is legal
        doc.publish(self._clock.now())
        # persist
        self._repo.save(doc)
        return self._view(doc)

    def create(self, title: str) -> DocumentView:
        # another module, through a port (section 6)
        match self._review.review(title):
            # the controller maps this to Rejected
            case Denied(why): raise ContentRejected(why)
        doc = Document.new(title)
        # persist
        self._repo.save(doc)
        return self._view(doc)

    # the DTO is built here: contract/ cannot import the entity
    def _view(self, doc: Document) -> DocumentView:
        return DocumentView(id=doc.id, title=doc.title)
