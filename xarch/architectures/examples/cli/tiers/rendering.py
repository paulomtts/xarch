@pytest.mark.parametrize("result, shown", [
    pytest.param(Published(DocumentView(A_ID, "Hello")), "Published Hello", id="a published document shows its title"),
    pytest.param(Missing(), "No such document", id="a missing document says so"),
    pytest.param(Rejected("The document needs a title."), "The document needs a title.",
                 id="a rejected document shows the reason"),
])
def test_publish(client, result, shown):
    output = client(Mock(publish=lambda cmd: result))(["documents", "publish", str(A_ID)]).output
    assert shown in output
