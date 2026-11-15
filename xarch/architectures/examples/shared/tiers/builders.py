NOW = datetime(2026, 1, 1)
A_ID = DocumentId(UUID(int=1))

def a_document(id: DocumentId = A_ID, title: str = "Hello", published_at: datetime | None = None) -> Document:
    return Document(id, title, published_at)
