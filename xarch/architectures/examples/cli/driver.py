def test_publish_prints_the_title_and_exits_zero(runner):
    controller = Mock(publish=lambda cmd: Published(DocumentView(cmd.id, "Hello", True)))
    result = runner.invoke(cli_app(controller), ["documents", "publish", str(A_DOCUMENT_ID)])
    assert result.exit_code == 0 and "Published Hello" in result.output
