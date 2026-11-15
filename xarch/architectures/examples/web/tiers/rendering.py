@pytest.mark.parametrize("result, shown", [
    pytest.param(Published(DocumentView(A_ID, "Hello")), "Hello", id="a published document shows its title"),
    pytest.param(Missing(), t("documents.missing"), id="a missing document says so"),
    pytest.param(Rejected("The document needs a title."), "The document needs a title.",
                 id="a rejected document shows the reason"),
])
def test_publish(client, result, shown):
    page = client(Mock(publish=lambda cmd: result)).post(f"/documents/{A_ID}/publish")
    assert shown in page.text
