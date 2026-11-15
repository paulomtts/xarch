def test_publish_renders_the_title(client):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello")))
    page = client(controller).post(f"/documents/{A_ID}/publish")
    assert "Hello" in page.text
