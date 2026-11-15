def test_a_document_without_a_title_cannot_be_published():
    with pytest.raises(DocumentIncomplete):
        a_document(title="").publish(NOW)

# an adapter's translation: tests/modules/documents/adapters/test_db_document_repo.py
def test_a_row_is_translated_to_a_document():
    session = Mock(get=lambda model, id: DocumentRow(id=A_ID, title="Hello", published_at=None))
    doc = DbDocumentRepo(session).get(A_ID)
    assert (doc.id, doc.title, doc.published_at) == (A_ID, "Hello", None)
