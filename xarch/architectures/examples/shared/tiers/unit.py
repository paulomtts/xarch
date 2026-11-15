@pytest.mark.parametrize("published_at, now, stale", [
    pytest.param(None, NOW, False, id="a draft is never stale"),
    pytest.param(NOW - timedelta(days=365), NOW, False, id="a document published a year ago is not stale"),
    pytest.param(NOW - timedelta(days=366), NOW, True, id="a document published over a year ago is stale"),
])
def test_is_stale(published_at, now, stale):
    assert is_stale(a_document(published_at=published_at), now) is stale

# an invariant that raises is its own test: tests/modules/documents/domain/test_document.py
def test_a_document_without_a_title_cannot_be_published():
    with pytest.raises(DocumentIncomplete):
        a_document(title="").publish(NOW)

# an adapter's translation: tests/modules/documents/adapters/test_db_document_repo.py
def test_a_row_is_translated_to_a_document():
    session = Mock(get=lambda model, id: DocumentRow(id=A_ID, title="Hello", published_at=None))
    doc = DbDocumentRepo(session).get(A_ID)
    assert (doc.id, doc.title, doc.published_at) == (A_ID, "Hello", None)
