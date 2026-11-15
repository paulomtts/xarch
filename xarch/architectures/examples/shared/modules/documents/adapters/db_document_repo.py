from app.modules.documents.domain.document import Document
from app.modules.documents.domain.values import DocumentId
from app.platform.sql import Session       # the engine and sessions are platform clients
from app.platform.sql.tables.documents import DocumentRow   # the table model, defined once in platform/

class DbDocumentRepo:                      # satisfies DocumentRepo
    def __init__(self, session: Session): self._s = session

    def get(self, id: DocumentId) -> Document | None:
        row = self._s.get(DocumentRow, id)
        return self._to_domain(row) if row else None

    def save(self, doc: Document) -> None:
        self._s.merge(self._from_domain(doc))

    def _to_domain(self, row: DocumentRow) -> Document:   # table row in, domain entity out
        return Document(DocumentId(row.id), row.title, row.published_at)

    def _from_domain(self, doc: Document) -> DocumentRow: # domain entity in, table row out
        return DocumentRow(id=doc.id, title=doc.title, published_at=doc.published_at)
