"""Use case: publish a document."""

@pytest.mark.parametrize("given, when, then", [
    pytest.param([a_document(title="Hello")], PublishDocument(A_ID), Published(DocumentView(A_ID, "Hello")),
                 id="a document with a title is published"),
    pytest.param([],                          PublishDocument(A_ID), Missing(),
                 id="a document that does not exist is missing"),
    pytest.param([a_document(title="")],      PublishDocument(A_ID), Rejected("The document needs a title."),
                 id="a document without a title is rejected"),
])
def test_publish(given, when, then):
    assert controller(given).publish(when) == then
