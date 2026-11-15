"""The private-imports check on hand-made source files: no file imports a name that starts with `_` from a file of the
app or of its tests."""
import pytest

from tests.modules.rules.builders import imp, in_tests, profile, source
from xarch.modules.rules.application.logic.private_imports import violations

ON = profile(private_imports=True)


def problems(*imports, checked=ON, tests=False) -> list[str]:
    file = in_tests("modules/docs/domain/test_doc.py", *imports) if tests else source("kernel/x.py", *imports)
    found = violations([file] if not tests else [], [file] if tests else [], checked, "app", "tests")
    return [str(v) for v in found]


def test_a_private_name_imported_from_the_app_is_reported_with_what_to_do():
    found = violations([source("kernel/x.py", imp(2, "app.cli.commands.check", "_json_refusal", "Format"))], [], ON,
                       "app", "tests")
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("app/kernel/x.py:2: imports the private name _json_refusal from app.cli.commands.check (private-imports)",
         "private-imports",
         "make _json_refusal public where it is defined (drop the `_`), or move it to a file both may import")]


@pytest.mark.parametrize("imports, tests, expected", [
    pytest.param([imp(1, "", "_helper", up=0)], False,
                 ["app/kernel/x.py:1: imports the private name _helper from . (private-imports)"],
                 id="a relative import"),
    pytest.param([imp(1, "tests.modules.docs.builders", "_make")], True,
                 ["tests/modules/docs/domain/test_doc.py:1: imports the private name _make from "
                  "tests.modules.docs.builders (private-imports)"], id="a test imports from test code"),
    pytest.param([imp(1, "app.kernel.ids", "_new")], True,
                 ["tests/modules/docs/domain/test_doc.py:1: imports the private name _new from app.kernel.ids "
                  "(private-imports)"], id="a test imports from the app"),
    pytest.param([imp(1, "app.kernel.ids", "__version__")], False, [], id="a dunder name"),
    pytest.param([imp(1, "typing", "_T"), imp(2, "yaml", "_x")], False, [], id="an outside package"),
    pytest.param([imp(1, "app.kernel._ids")], False, [], id="a whole file"),
    pytest.param([imp(1, "app.kernel.ids", "new")], False, [], id="a public name"),
])
def test_what_is_read_and_what_is_not(imports, tests, expected):
    assert problems(*imports, tests=tests) == expected


def test_it_is_off_without_the_guard():
    assert problems(imp(1, "app.kernel.ids", "_new"), checked=profile()) == []
