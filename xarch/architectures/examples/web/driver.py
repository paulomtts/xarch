def test_publish_renders_the_title_and_answers_200(client):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello", True)))
    response = client(controller).post(f"/documents/{A_DOCUMENT_ID}/publish")
    assert response.status_code == 200 and "Hello" in response.text
