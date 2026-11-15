"""The test-tree rule on plain values: which folders of the tests mirror no folder of the app."""
import pytest

from xarch.modules.layout.application.logic.unmirrored import hidden, unmirrored


@pytest.mark.parametrize("path, is_hidden", [
    pytest.param(("docs", "__pycache__"), True, id="a cache folder is hidden"),
    pytest.param((".cache",), True, id="a dot folder is hidden"),
    pytest.param(("_private", "x"), True, id="a folder below a private one is hidden"),
    pytest.param(("docs", "domain"), False, id="a plain folder is not hidden"),
])
def test_hidden(path, is_hidden):
    assert hidden(path) == is_hidden


def test_unmirrored_reports_each_test_folder_that_mirrors_no_folder_of_the_app_in_order():
    folders = [("docs", "gone"), ("docs",), ("docs", "__pycache__"), ("ghost",), ("docs", "domain")]
    found = unmirrored("tests", "app", ("modules",), folders, {("docs",), ("docs", "domain")})
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("tests/modules/docs/gone: mirrors no folder of the app (app/modules/docs/gone)", "test-tree",
         "create app/modules/docs/gone/ in the app, or move what it holds to the folder that mirrors its subject, "
         "or remove it"),
        ("tests/modules/ghost: mirrors no folder of the app (app/modules/ghost)", "test-tree",
         "create app/modules/ghost/ in the app, or move what it holds to the folder that mirrors its subject, or "
         "remove it")]
