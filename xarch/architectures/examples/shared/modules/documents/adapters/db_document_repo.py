from app.modules.documents.domain.document import Document
from app.modules.documents.domain.values import DocumentId
# the engine and sessions are platform clients
from app.platform.sql import Session
# the table model, defined once in platform/
from app.platform.sql.tables.documents import DocumentRow

# satisfies DocumentRepo
class DbDocumentRepo:
    def __init__(self, session: Session): self._s = session

    def get(self, id: DocumentId) -> Document | None:
        row = self._s.get(DocumentRow, id)
        return self._to_domain(row) if row else None

    def save(self, doc: Document) -> None:
        self._s.merge(self._from_domain(doc))

    # table row in, domain entity out
    def _to_domain(self, row: DocumentRow) -> Document:
        return Document(DocumentId(row.id), row.title, row.published_at)

    # domain entity in, table row out
    def _from_domain(self, doc: Document) -> DocumentRow:
        return DocumentRow(id=doc.id, title=doc.title, published_at=doc.published_at)
