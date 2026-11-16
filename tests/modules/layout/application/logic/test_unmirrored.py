"""The test-tree rule on plain values: which folders of the tests mirror no folder of the app."""
import pytest

from tests.modules.layout.builders import PYTHON_NAMING
from xarch.modules.layout.application.logic.unmirrored import unmirrored

"""How Python names a folder, as its data file says."""


def reported(path: str) -> list[tuple[str, str, str]]:
    """The test folder tests/modules/<path> reported as mirroring no folder of the app: its line, rule and fix."""
    return [(f"tests/modules/{path}: mirrors no folder of the app (app/modules/{path})", "test-tree",
             f"create app/modules/{path}/ in the app, or move what it holds to the folder that mirrors its subject, or "
             "remove it")]


@pytest.mark.parametrize("path, found", [
    pytest.param(("docs", "__pycache__"), [], id="a folder of compiled files is hidden"),
    pytest.param((".cache",), reported(".cache"),
                 id="a folder the filesystem hides is the disk's to leave out, not the language's"),
    pytest.param(("_private", "x"), [], id="a folder below a private one is hidden"),
    pytest.param(("docs", "domain"), reported("docs/domain"), id="a plain folder is not hidden"),
])
def test_a_hidden_test_folder_mirrors_nothing_and_is_never_reported(path, found):
    violations = unmirrored("tests", "app", ("modules",), [path], set(), PYTHON_NAMING)
    assert [(str(v), v.rule, v.fix) for v in violations] == found


def test_unmirrored_reports_each_test_folder_that_mirrors_no_folder_of_the_app_in_order():
    folders = [("docs", "gone"), ("docs",), ("docs", "__pycache__"), ("ghost",), ("docs", "domain")]
    found = unmirrored("tests", "app", ("modules",), folders, {("docs",), ("docs", "domain")}, PYTHON_NAMING)
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("tests/modules/docs/gone: mirrors no folder of the app (app/modules/docs/gone)", "test-tree",
         "create app/modules/docs/gone/ in the app, or move what it holds to the folder that mirrors its subject, "
         "or remove it"),
        ("tests/modules/ghost: mirrors no folder of the app (app/modules/ghost)", "test-tree",
         "create app/modules/ghost/ in the app, or move what it holds to the folder that mirrors its subject, or "
         "remove it")]
