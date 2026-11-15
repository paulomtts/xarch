def test_a_document_without_a_title_is_rejected():
    repo = FakeDocumentRepo()
    repo.save(doc := a_document(title=""))
    assert controller(repo).publish(PublishDocument(doc.id)) == Rejected("The document needs a title.")
