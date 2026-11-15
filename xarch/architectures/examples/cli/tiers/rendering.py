def test_publish_prints_the_title(client):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello")))
    result = client(controller)(["documents", "publish", str(A_ID)])
    assert "Published Hello" in result.output
