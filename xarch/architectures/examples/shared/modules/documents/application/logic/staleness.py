from app.modules.documents.domain.document import Document

def is_stale(doc: Document, now: datetime) -> bool:
    return doc.published_at is not None and now - doc.published_at > timedelta(days=365)
